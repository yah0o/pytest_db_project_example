import json

import allure
import pytest
from hamcrest import equal_to, has_entries, is_not
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import EntitiesBy
from np_cats_qa.data.schemas import schemas
from np_cats_qa.matchers import not_empty


@allure.feature('cats')
@allure.story('get_entity_by_id')
def test_get_entity_by_id(is_http, is_db):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type title_code: str
    """
    entity = schemas.entity()
    fields = schemas.fields()

    is_db.add_new_entity_data_into_db(entity['entitlement_id'], entity['entitlement_code'], 1,
                                      json.dumps(fields), json.dumps(entity['metadata']))
    response = is_http.cats.get_entitiy_by_id(entity_id=entity['entitlement_id'])

    expected = {**entity, **fields}
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.json(), equal_to(expected))


@allure.feature('cats')
@allure.story('get_entity_by_id')
@pytest.mark.parametrize('id, code, entity_type_id', [
    ('02c9b145-not-exist-87bb-b721166a082c', codes.bad_request, 1),
    (None, codes.bad_request, 1),
    (123, codes.bad_request, 1)
])
def test_failure_get_entity_by(is_http, is_db, id, code, entity_type_id):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type id: str
    :type code: http  status code
    """

    is_db.add_new_entity_data_into_db(EntitiesBy.ID, 'test_code', entity_type_id, json.dumps({}), json.dumps({}))
    response = is_http.cats.get_entitiy_by_id(entity_id=id)

    assert_that(response, has_status_code(code), allure_name='response has expected code')


@allure.feature('cats')
@allure.story('test_get_entity_with_set_name')
def test_get_entity_with_set_name(is_http):
    # FREYA-1032
    response = is_http.cats.get_entitiy_by_id(entity_id=EntitiesBy.PRODUCT_ID)

    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.json(), has_entries(name=not_empty()))
    # Check that length of 'name' parameter of test product wot metadata  is correct
    assert_that(len(response.json()['name']['data']), equal_to(6),
                allure_name='name parameter in response has expected length')


@allure.feature('cats')
@allure.story('get_entity_by_id')
@pytest.mark.parametrize('language', ["en", "ru", "zh_cn", "zh_sg", "zh_tw"])
def test_get_entity_by_id_localized(is_http, is_db, language):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    """
    entity = schemas.entity()
    fields = schemas.fields()

    is_db.add_new_entity_data_into_db(entity['entitlement_id'], entity['entitlement_code'], 1,
                                      json.dumps(fields), json.dumps(entity['metadata']))
    response = is_http.cats.get_entitiy_by_id(entity_id=entity['entitlement_id'],
                                              language=language)

    expected = {**entity, **fields}
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')

    response_dict = response.json()
    assert_that(response_dict['metadata'], is_not(equal_to(expected['metadata'])))
    assert_that(response_dict['metadata']['wot']['short_name']['data']['value'],
                equal_to(expected['metadata']['wot']['short_name']['data'][language]))

    del response_dict['metadata']
    del expected['metadata']
    assert_that(response_dict, equal_to(expected))


@allure.feature('cats')
@allure.story('get_entity_by_id')
@pytest.mark.parametrize('language', ["en", "ru", "de", "fr"])
def test_get_entity_by_id_localized_category(is_http, is_db, language):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    """
    storefront = schemas.storefront()
    fields = {k: v for k, v in storefront.items() if k not in {'metadata'}}

    is_db.add_new_entity_data_into_db(storefront['storefront_id'], storefront['code'], 4,
                                      json.dumps(fields), json.dumps(storefront['metadata']))
    response = is_http.cats.get_entitiy_by_id(entity_id=storefront['storefront_id'],
                                              language=language)

    expected = {**storefront, **fields}
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')

    response_dict = response.json()
    assert_that(response_dict['metadata'], is_not(equal_to(expected['metadata'])))
    assert_that(response_dict['metadata']['wot']['short_name']['data']['value'],
                equal_to(expected['metadata']['wot']['short_name']['data'][language]))

    expected_category_meta = expected['categories']['category_test_1']['metadata']
    resp_category_meta = response_dict['categories']['category_test_1']['metadata']
    assert_that(resp_category_meta, is_not(equal_to(expected_category_meta)))
    assert_that(resp_category_meta['name']['data']['value'],
                equal_to(expected_category_meta['name']['data'][language]))

    del response_dict['metadata']
    del response_dict['categories']
    del expected['metadata']
    del expected['categories']
    assert_that(response_dict, equal_to(expected))


@allure.feature('cats')
@allure.story('get_entity_by_id')
@pytest.mark.parametrize('language', ["by", "es", "ar"])
def test_get_entity_by_id_localized_category_not_exist_language(is_http, is_db, language):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    """
    storefront = schemas.storefront()
    fields = {k: v for k, v in storefront.items() if k not in {'metadata'}}

    is_db.add_new_entity_data_into_db(storefront['storefront_id'], storefront['code'], 4,
                                      json.dumps(fields), json.dumps(storefront['metadata']))
    response = is_http.cats.get_entitiy_by_id(entity_id=storefront['storefront_id'],
                                              language=language)

    expected = {**storefront, **fields}
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')

    response_dict = response.json()
    assert_that(response_dict['metadata'], is_not(equal_to(expected['metadata'])))
    assert_that(response_dict['metadata']['wot']['short_name']['data']['value'],
                equal_to('Test_meta_en'), allure_name='response has default en language')

    expected_category_meta = expected['categories']['category_test_1']['metadata']
    resp_category_meta = response_dict['categories']['category_test_1']['metadata']
    assert_that(resp_category_meta, is_not(equal_to(expected_category_meta)))
    assert_that(resp_category_meta['name']['data']['value'],
                equal_to('Test_category_en'), allure_name='response category has default en language')

    del response_dict['metadata']
    del response_dict['categories']
    del expected['metadata']
    del expected['categories']
    assert_that(response_dict, equal_to(expected))
