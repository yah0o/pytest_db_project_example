import shutil

import allure
import pytest
from hamcrest import equal_to
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import CatalogZIP, CatalogDiffError, PublishError, CatalogError, PublishStatus
from np_cats_qa.data_generators import generate_catalog_url, generate_catalog_code
from np_cats_qa.helpers import ulid
from np_cats_qa.verifications import verify_publish_completed_with_status_in_db
from np_cats_qa.matchers import not_empty


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
@pytest.mark.parametrize(('destination_catalog_code', 'entity_type', 'error', 'description'), [
    (None, 'CURRENCY', CatalogError.CATALOG_NOT_FOUND, 'Catalog is not found.'),
    ('not_exist', 'ENTITLEMENT', CatalogError.CATALOG_NOT_FOUND, 'Catalog is not found.'),
    (0.5, 'PRODUCT', CatalogError.CATALOG_NOT_FOUND, 'Catalog is not found.'),
    (123, 'STOREFRONT', CatalogError.CATALOG_NOT_FOUND, 'Catalog is not found.'),
    (pytest.lazy_fixture('get_active_catalog_code_by_title_code'), 'not_exist', PublishError.CLIENT_ERROR,
     CatalogDiffError.ENTITY_TYPE),
    (pytest.lazy_fixture('get_active_catalog_code_by_title_code'), None, PublishError.CLIENT_ERROR,
     CatalogDiffError.ENTITY_TYPE),
    (pytest.lazy_fixture('get_active_catalog_code_by_title_code'), .5, PublishError.CLIENT_ERROR,
     CatalogDiffError.ENTITY_TYPE),
    (pytest.lazy_fixture('get_active_catalog_code_by_title_code'), 123, PublishError.CLIENT_ERROR,
     CatalogDiffError.ENTITY_TYPE)
])
def test_get_initial_diff_required_validation(is_http, mock_http, destination_catalog_code, entity_type, error, description):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    """

    # FREYA-843 - get single catalog tests

    extract_path = 'tmp/'
    mock_http.extract_catalog_by_catalog_code_to(catalog_file=CatalogZIP.DEFAULT_CATALOG, extract_path=extract_path)
    response = is_http.cats.get_initial_diff_by_type_and_catalog_code(
        destination_catalog_code=destination_catalog_code,
        entity_type=entity_type,
        fields=None
    )
    assert_that(response, has_status_code(codes.bad), allure_name='response has expected code')
    assert_that(response.json()['error']['code'], equal_to(error))
    assert_that(response.json()['error']['context']['description'], equal_to(description))
    if response.json()['error']['code'] == CatalogError.CATALOG_NOT_FOUND:
      assert_that(response.json()['error']['context']['catalog_code'], equal_to(str(destination_catalog_code)))



@allure.feature('cats')
@allure.story('get_initial_diff')
@pytest.mark.parametrize(('fields', 'fields_result'), [
    (123, {}),
    (.5, {}),
    ('not_exist', {})
])
def test_get_initial_diff_fields_validation_should_pass(is_http, is_db, mock_http, clear_tmp,
                                                        get_active_catalog_code_by_title_code, fields,
                                                        fields_result):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    """

    # Should passed with empty list of fields in response

    extract_path = 'tmp/'
    mock_http.extract_catalog_by_catalog_code_to(catalog_file=CatalogZIP.DEFAULT_CATALOG, extract_path=extract_path)
    response = is_http.cats.get_initial_diff_by_type_and_catalog_code(
        destination_catalog_code=get_active_catalog_code_by_title_code,
        entity_type='CURRENCY',
        fields=fields
    )
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.json()[0]['fields'], equal_to(fields_result))


@allure.feature('cats')
@allure.story('get_initial_diff')
@pytest.mark.parametrize('limit, error', [
    (.5, CatalogError.CLIENT_ERROR),
    (9223372036854775808, CatalogError.CLIENT_ERROR),
    ('test', CatalogError.CLIENT_ERROR),
    (0, [])
])
def test_get_initial_diff_with_paging_validation(is_http, is_db, mock_http,
                                                 get_active_catalog_code_by_title_code, limit, error):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    """

    response = is_http.cats.get_initial_diff_by_type_and_catalog_code(
        destination_catalog_code=get_active_catalog_code_by_title_code,
        entity_type='CURRENCY',
        limit=limit
    )
    if limit is not 0:
        assert_that(response, has_status_code(codes.bad), allure_name='response has expected code')
        assert_that(response.json()['error']['code'], equal_to(error))
    else:
        assert_that(response.json(), equal_to(error))


@allure.feature('cats')
@allure.story('get_diff')
@pytest.mark.parametrize(
    ('src_catalog_code', 'dest_catalog_code', 'entity_type', 'error', 'description'), [
        (None, pytest.lazy_fixture('destination_catalog_code'), 'CURRENCY', CatalogError.CATALOG_NOT_FOUND, 'Catalog is not found.'),
        ('not_exist', pytest.lazy_fixture('destination_catalog_code'), 'CURRENCY', CatalogError.CATALOG_NOT_FOUND,
         'Catalog is not found.'),
        (123, pytest.lazy_fixture('destination_catalog_code'), 'CURRENCY', CatalogError.CATALOG_NOT_FOUND, 'Catalog is not found.'),
        (pytest.lazy_fixture('source_catalog_code'), None, 'CURRENCY', CatalogError.CATALOG_NOT_FOUND, 'Catalog is not found.'),
        (pytest.lazy_fixture('source_catalog_code'), 'not_exist', 'CURRENCY', CatalogError.CATALOG_NOT_FOUND,
         'Catalog is not found.'),
        (pytest.lazy_fixture('source_catalog_code'), '123', 'CURRENCY', CatalogError.CATALOG_NOT_FOUND, 'Catalog is not found.'),
        (pytest.lazy_fixture('source_catalog_code'), pytest.lazy_fixture('destination_catalog_code'), None,
         PublishError.CLIENT_ERROR,
         CatalogDiffError.ENTITY_TYPE),
        (pytest.lazy_fixture('source_catalog_code'), pytest.lazy_fixture('destination_catalog_code'), 123,
         PublishError.CLIENT_ERROR,
         CatalogDiffError.ENTITY_TYPE),
        (pytest.lazy_fixture('source_catalog_code'), pytest.lazy_fixture('destination_catalog_code'), 'not_exist',
         PublishError.CLIENT_ERROR,
         CatalogDiffError.ENTITY_TYPE),
    ])
def test_get_diff_required_validation(is_http, entity_type, yaml_config, dest_catalog_code,
                                      src_catalog_code, error, description
                                      ):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    """

    response = is_http.cats.get_diff_by_type_and_catalog_code(
        destination_catalog_code=dest_catalog_code,
        source_catalog_code=src_catalog_code,
        entity_type=entity_type
    )
    assert_that(response, has_status_code(codes.bad), allure_name='response has expected code')
    assert_that(response.json()['error']['code'], equal_to(error))
    assert_that(response.json()['error']['context']['description'], equal_to(description))
    if response.json()['error']['code'] == CatalogError.CATALOG_NOT_FOUND:
      assert_that(response.json()['error']['context']['catalog_code'], not_empty())


@allure.feature('cats')
@allure.story('get_diff')
@pytest.mark.parametrize(('fields', 'fields_result'), [
    (123, []),
    (.5, []),
    ('not_exist', [])
])
def test_get_diff_with_fields_validation_should_pass(is_http, yaml_config, destination_catalog_code,
                                                     source_catalog_code, fields, fields_result):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    """

    generate_catalog_url(yaml_config, CatalogZIP.UPDATED_CATALOG)

    response = is_http.cats.get_diff_by_type_and_catalog_code(
        destination_catalog_code=destination_catalog_code,
        source_catalog_code=source_catalog_code,
        entity_type='COUPON',
        fields=fields
    )
    assert_that(response.json(), equal_to(fields_result))


@allure.feature('cats')
@allure.story('get_diff')
@pytest.mark.parametrize('limit, error', [
    (.5, CatalogError.CLIENT_ERROR),
    (9223372036854775808, CatalogError.CLIENT_ERROR),
    ('test', CatalogError.CLIENT_ERROR),
    (0, CatalogError.CATALOG_NOT_FOUND)
])
def test_get_diff_with_paging_validation(is_http, limit, error):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    """

    response = is_http.cats.get_diff_by_type_and_catalog_code(
        destination_catalog_code=destination_catalog_code,
        source_catalog_code=source_catalog_code,
        entity_type='CURRENCY',
        limit=limit
    )
    assert_that(response, has_status_code(codes.bad), allure_name='response has expected code')
    assert_that(response.json()['error']['code'], equal_to(error))
