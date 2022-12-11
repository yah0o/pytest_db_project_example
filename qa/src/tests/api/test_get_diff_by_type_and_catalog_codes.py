import json
import shutil

import allure
import pytest
from hamcrest import equal_to, has_entries, is_not
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import CatalogZIP
from np_cats_qa.constants import PublishStatus, ChangeType, EntitiesBy
from np_cats_qa.data_generators import generate_catalog_url, generate_catalog_code
from np_cats_qa.helpers import ulid
from np_cats_qa.matchers import not_empty
from np_cats_qa.verifications import verify_publish_completed_with_status_in_db


@pytest.fixture
def clear_tmp():
    yield
    shutil.rmtree('tmp')


@pytest.fixture(scope='session')
def source_catalog_code(is_http, yaml_config, is_db):
    # publish catalog for the same title with different zip
    publish_id = ulid()
    catalog_code = generate_catalog_code(yaml_config.data.TITLE_CODE)
    catalog_url = generate_catalog_url(yaml_config, CatalogZIP.DEFAULT_CATALOG)
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # wait for catalog published
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)
    return catalog_code


@pytest.fixture(scope='session')
def destination_catalog_code(is_http, yaml_config, is_db):
    # publish catalog for the same title with different zip
    publish_id = ulid()
    catalog_code = generate_catalog_code(yaml_config.data.TITLE_CODE)
    catalog_url = generate_catalog_url(yaml_config, CatalogZIP.UPDATED_CATALOG)
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # wait for catalog published
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)
    return catalog_code


@allure.feature('cats')
@allure.story('get_initial_diff')
@pytest.mark.parametrize(('entity_type', 'entity_file'), [
    ('CURRENCY', 'currencies.json'),
    ('ENTITLEMENT', 'entitlements.json'),
    ('PRODUCT', 'products.json'),
    ('STOREFRONT', 'storefronts.json'),
    ('OVERRIDE', 'overrides.json'),
    ('PROMOTION', 'promotions.json'),
    ('FILTER_PROPERTY', 'filter_properties.json')])
@pytest.mark.parametrize('fields', [None, "active,metadata"])
def test_get_initial_diff(is_http, entity_type, mock_http, clear_tmp, entity_file,
                          get_active_catalog_code_by_title_code, fields):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    """

    # FREYA-843 - get single catalog tests

    extract_path = 'tmp/'
    mock_http.extract_catalog_by_catalog_code_to(catalog_file=CatalogZIP.DEFAULT_CATALOG, extract_path=extract_path)

    with open(extract_path + entity_file, 'r+', encoding="utf-8") as f:
        entity_from_catalog = json.load(f)
    response = is_http.cats.get_initial_diff_by_type_and_catalog_code(
        destination_catalog_code=get_active_catalog_code_by_title_code,
        entity_type=entity_type,
        fields=fields
    )
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(len(response.json()), equal_to(len(entity_from_catalog)))
    assert_that(response.json()[0], has_entries(change_type=equal_to('CREATE'),
                                                id=not_empty(),
                                                code=not_empty(),
                                                fields=not_empty()),
                allure_name='response has expected parameters')

    assert_that(response.json()[0]['fields'], has_entries(metadata=not_empty()),
                allure_name='fields has expected parameters')


@allure.feature('cats')
@allure.story('get_initial_diff_with_paging')
@pytest.mark.parametrize(('entity_type', 'entity_file'), [
    ('CURRENCY', 'currencies.json'),
    ('ENTITLEMENT', 'entitlements.json'),
    ('PRODUCT', 'products.json'),
    ('STOREFRONT', 'storefronts.json'),
    ('OVERRIDE', 'overrides.json'),
    ('PROMOTION', 'promotions.json'),
    ('FILTER_PROPERTY', 'filter_properties.json')
])
@pytest.mark.parametrize('limit', [None, 5])
def test_get_initial_diff_with_paging(is_http, entity_type, mock_http, clear_tmp, entity_file,
                                      get_active_catalog_code_by_title_code, limit):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    """

    extract_path = 'tmp/'
    mock_http.extract_catalog_by_catalog_code_to(catalog_file=CatalogZIP.DEFAULT_CATALOG, extract_path=extract_path)

    with open(extract_path + entity_file, 'r+', encoding="utf-8") as f:
        entity_from_catalog = json.load(f)

    response = is_http.cats.get_initial_diff_by_type_and_catalog_code(
        destination_catalog_code=get_active_catalog_code_by_title_code,
        entity_type=entity_type,
        limit=limit
    )
    count = len(response.json())
    last_id = response.json()[count - 1]['id'] if count > 0 else None
    total_count = count

    while last_id is not None:
        response = is_http.cats.get_initial_diff_by_type_and_catalog_code(
            destination_catalog_code=get_active_catalog_code_by_title_code,
            entity_type=entity_type,
            limit=limit,
            last_id=last_id
        )
        count = len(response.json())
        last_id = response.json()[count - 1]['id'] if count > 0 else None
        total_count += count

    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(total_count, equal_to(len(entity_from_catalog)))


@allure.feature('cats')
@allure.story('get_diff_with_fields')
@pytest.mark.parametrize(
    ('entity_type', 'fields', 'entity_count'), [
        ('CURRENCY', 'active', 3),
        ('ENTITLEMENT', 'max_amount,max_amount_global', 17),
        ('PRODUCT', 'active', 79),
        ('STOREFRONT', 'product_references', 51),
        ('OVERRIDE', 'overrides', 33),
        ('PROMOTION', 'end_time', 38),
        ('FILTER_PROPERTY', 'metadata', 3)
    ])
def test_get_initial_diff_with_fields(is_http, entity_type, yaml_config, destination_catalog_code,
                                      get_active_catalog_code_by_title_code, fields, entity_count):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    """
    response = is_http.cats.get_initial_diff_by_type_and_catalog_code(
        destination_catalog_code=get_active_catalog_code_by_title_code,
        entity_type=entity_type,
        fields=fields
    )
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(len(response.json()), equal_to(entity_count))


@allure.feature('cats')
@allure.story('get_initial_diff')
def test_get_initial_diff_none_fields_should_pass(is_http, mock_http, clear_tmp,
                                                  get_active_catalog_code_by_title_code):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    """

    # Response should get fields with None parameter

    extract_path = 'tmp/'
    mock_http.extract_catalog_by_catalog_code_to(catalog_file=CatalogZIP.DEFAULT_CATALOG, extract_path=extract_path)
    response = is_http.cats.get_initial_diff_by_type_and_catalog_code(
        destination_catalog_code=get_active_catalog_code_by_title_code,
        entity_type='CURRENCY',
        fields=None
    )
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(len(response.json()[0]['fields']), is_not(0))


@allure.feature('cats')
@allure.story('get_diff')
@pytest.mark.parametrize(
    ('entity_type', 'create_total', 'update_total', 'delete_total'), [
        ('CURRENCY', 0, 2, 1),
        ('ENTITLEMENT', 0, 4, 0),
        ('PRODUCT', 0, 4, 1),
        ('STOREFRONT', 0, 1, 3),
        ('OVERRIDE', 0, 6, 1),
        ('PROMOTION', 0, 1, 1),
        ('FILTER_PROPERTY', 0, 0, 1)
    ])
def test_get_diff(is_http, entity_type, mock_http, yaml_config, destination_catalog_code, source_catalog_code,
                  create_total, update_total, delete_total):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    """

    generate_catalog_url(yaml_config, CatalogZIP.UPDATED_CATALOG)

    response = is_http.cats.get_diff_by_type_and_catalog_code(
        destination_catalog_code=destination_catalog_code,
        source_catalog_code=source_catalog_code,
        entity_type=entity_type
    )

    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')

    counter = {ChangeType.CREATE: 0, ChangeType.UPDATE: 0, ChangeType.DELETE: 0}

    for entity in response.json():
        if 'change_type' in entity:
            counter[entity['change_type']] += 1

    assert_that(counter[ChangeType.CREATE], equal_to(create_total),
                allure_name='response has incorrect count of new entities')
    assert_that(counter[ChangeType.UPDATE], equal_to(update_total),
                allure_name='response has incorrect count of updated entities')
    assert_that(counter[ChangeType.DELETE], equal_to(delete_total),
                allure_name='response has incorrect count of deleted entities')


@allure.feature('cats')
@allure.story('get_diff_with_fields')
@pytest.mark.parametrize(
    ('entity_type', 'fields', 'entity_count'), [
        ('CURRENCY', 'active', 2),
        ('ENTITLEMENT', 'max_amount,max_amount_global', 2),
        ('PRODUCT', 'active', 1),
        ('STOREFRONT', 'product_references', 4),
        ('OVERRIDE', 'overrides', 7),
        ('PROMOTION', 'end_time', 2),
        ('FILTER_PROPERTY', 'metadata', 1)
    ])
def test_get_diff_with_fields(is_http, entity_type, yaml_config, destination_catalog_code,
                              source_catalog_code, fields, entity_count):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    """

    generate_catalog_url(yaml_config, CatalogZIP.UPDATED_CATALOG)

    response = is_http.cats.get_diff_by_type_and_catalog_code(
        destination_catalog_code=destination_catalog_code,
        source_catalog_code=source_catalog_code,
        entity_type=entity_type,
        fields=fields
    )
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(len(response.json()), equal_to(entity_count))


@allure.feature('cats')
@allure.story('get_diff_with_paging')
@pytest.mark.parametrize(
    ('entity_type', 'entity_count'), [
        ('CURRENCY', 3),
        ('ENTITLEMENT', 4),
        ('PRODUCT', 5),
        ('STOREFRONT', 4),
        ('OVERRIDE', 7),
        ('PROMOTION', 2),
        ('FILTER_PROPERTY', 1)
    ])
@pytest.mark.parametrize('limit', [1, 2])
def test_get_diff_with_paging(is_http, entity_type, yaml_config, destination_catalog_code,
                              source_catalog_code, limit, entity_count):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    """

    generate_catalog_url(yaml_config, CatalogZIP.UPDATED_CATALOG)

    response = is_http.cats.get_diff_by_type_and_catalog_code(
        destination_catalog_code=destination_catalog_code,
        source_catalog_code=source_catalog_code,
        entity_type=entity_type,
        limit=limit
    )

    count = len(response.json())
    last_id = response.json()[count - 1]['id'] if count > 0 else None
    total_count = count

    while last_id is not None:
        response = is_http.cats.get_diff_by_type_and_catalog_code(
            destination_catalog_code=destination_catalog_code,
            source_catalog_code=source_catalog_code,
            entity_type=entity_type,
            limit=limit,
            last_id=last_id
        )
        count = len(response.json())
        last_id = response.json()[count - 1]['id'] if count > 0 else None
        total_count += count

    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(total_count, equal_to(entity_count))


@allure.feature('cats')
@allure.story('get_diff_with_paging')
@pytest.mark.parametrize('last_id, code, entity_type_id, entity_type', [
    (EntitiesBy.ID, codes.bad_request, 1, 'product'),
    (EntitiesBy.ID, codes.bad_request, 1, 'not_exist_type'),
    (EntitiesBy.ID, codes.bad_request, 1, None),
    ('02c9b145-not-exist-87bb-b721166a082c', codes.bad_request, 1, 'entitlement'),
    (123, codes.bad_request, 1, 'entitlement')
])
@pytest.mark.parametrize('diff_type', ['initial', 'diff'])
def test_failure_diff_with_paging(is_http, title_code, code, yaml_config, entity_type, last_id, diff_type,
                                  get_active_catalog_code_by_title_code, source_catalog_code, entity_type_id):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    :type id: str
    :type code: http  status code
    """

    generate_catalog_url(yaml_config, CatalogZIP.UPDATED_CATALOG)

    if diff_type == 'initial':
        response = is_http.cats.get_initial_diff_by_type_and_catalog_code(
            destination_catalog_code=get_active_catalog_code_by_title_code,
            entity_type=entity_type,
            last_id=last_id
        )
    else:
        response = is_http.cats.get_diff_by_type_and_catalog_code(
            destination_catalog_code=get_active_catalog_code_by_title_code,
            source_catalog_code=source_catalog_code,
            entity_type=entity_type,
            last_id=last_id
        )
    assert_that(response, has_status_code(code), allure_name='response has expected code')
