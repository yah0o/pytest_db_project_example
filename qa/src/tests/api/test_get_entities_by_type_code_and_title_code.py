import json

import allure
import pytest
from hamcrest import empty, equal_to
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import CatalogZIP, CatalogError
from np_cats_qa.verifications import verify_failed_response


@allure.feature('cats')
@allure.story('get_entity_by_type_and_code')
@pytest.mark.parametrize(('entity_type', 'entity_code', 'code_field', 'entity_file'), [
    ('CURRENCY', 'gold', 'currency_code', 'currencies.json'),
    ('FILTER_PROPERTY', 'ent_level', 'code', 'filter_properties.json'),
    ('ENTITLEMENT', 'test_entitlement_generic', 'entitlement_code', 'entitlements.json'),
    ('PRODUCT', 'test_product_entitlement', 'code', 'products.json'),
    ('STOREFRONT', 'test_store', 'code', 'storefronts.json'),
    ('OVERRIDE', 'test_override', 'code', 'overrides.json'),
    ('PROMOTION', 'test_promotion', 'code', 'promotions.json')
])
def test_get_entity_by_type_and_code(is_http, mock_http, clear_tmp, entity_type, entity_code, title_code,
                                     code_field, entity_file):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """

    extract_path = 'tmp/'
    mock_http.extract_catalog_by_catalog_code_to(catalog_file=CatalogZIP.DEFAULT_CATALOG, extract_path=extract_path)

    with open(extract_path + entity_file, 'r+', encoding="utf-8") as f:
        entities_from_catalog = json.load(f)
        entity_from_catalog = next(item for item in entities_from_catalog if item[code_field] == entity_code)
    response = is_http.cats.get_entities_by_type_code_and_title_code(title_code, entity_type=entity_type,
                                                                     code=entity_code)

    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that([key for key in entity_from_catalog if entity_from_catalog[key] != response.json()[key]],
                empty(), allure_name='Catalog entities are same')


@allure.feature('cats')
@allure.story('get_entity_by_type_and_code')
@pytest.mark.parametrize(('entity_type', 'entity_code'), [
    ('CURRENCY', 'not_exist_code'),
    ('ENTITLEMENT', None),
    ('ENTITLEMENT', 123),
    ('ENTITLEMENT', '!@$%^&*(()'),
    ('not_exist', 'not_exist')

])
def test_get_entity_by_type_and_code_negative(is_http, entity_type, entity_code,
                                              title_code):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: np_cats_qa.steps.db.steps.CatalogServiceDBSteps
    :type title_code: str
    """

    response = is_http.cats.get_entities_by_type_code_and_title_code(title_code, entity_type=entity_type,
                                                                     code=entity_code)

    assert_that(response, has_status_code(codes.bad), allure_name='response has expected code')


@allure.feature('cats')
@allure.story('get_entity_by_type_and_code')
@pytest.mark.parametrize(('entity_type', 'entity_code', 'entity_file', 'language'), [
    ('STOREFRONT', 'test_store_epic_wows_localized', 'storefronts.json', 'ru'),
    ('STOREFRONT', 'test_store_epic_wows_localized', 'storefronts.json', 'en')
])
def test_get_entity_by_type_and_code_localization(is_http, mock_http, entity_type, entity_code, title_code, entity_file,
                                                  language):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """
    extract_path = 'tmp/'
    mock_http.extract_catalog_by_catalog_code_to(catalog_file=CatalogZIP.DEFAULT_CATALOG, extract_path=extract_path)
    code_field = 'code'

    response = is_http.cats.get_entities_by_type_code_and_title_code(title_code, entity_type=entity_type,
                                                                     code=entity_code,
                                                                     language=language
                                                                     )
    with open(extract_path + entity_file, 'r+', encoding="utf-8") as f:
        entities_from_catalog = json.load(f)
        entity_from_catalog = next(item for item in entities_from_catalog if item[code_field] == entity_code)

    # specified localization category metadata from catalog
    catalog_loc_category_meta_title = entity_from_catalog['categories']['featured']['metadata']['title']['data']
    catalog_loc_category_type = entity_from_catalog['categories']['doubloons']['metadata']['description']['data']
    catalog_loc_category_type_title = entity_from_catalog['categories']['doubloons']['metadata']['title']['data']
    catalog_loc_category_customizations_data = entity_from_catalog['categories']['doubloons']['metadata']['title'][
        'data']

    # check that specified localization category metadata from catalog equal to localizaed data in res
    assert_that(catalog_loc_category_meta_title[language],
                equal_to(response.json()['categories']['featured']['metadata']['title']['data'][language]),
                allure_name='category meta title has an appropriate language')
    assert_that(catalog_loc_category_type[language],
                equal_to(response.json()['categories']['doubloons']['metadata']['description']['data'][language]),
                allure_name='category localization category type has an appropriate language')
    assert_that(catalog_loc_category_type_title[language],
                equal_to(response.json()['categories']['doubloons']['metadata']['title']['data'][
                             language]),
                allure_name='category localization category type title has an appropriate language')
    assert_that(catalog_loc_category_customizations_data[language],
                equal_to(response.json()['categories']['doubloons']['metadata']['title']['data'][language]),
                allure_name='category localization category customizations data has an appropriate language')

    # check that only localized data in res
    assert_that(len(response.json()['categories']['featured']['metadata']['title']['data']) != len(
        catalog_loc_category_meta_title),
                equal_to(True), allure_name='categories has expected language in response')


@allure.feature('cats')
@allure.story('get_entity_by_type')
@pytest.mark.parametrize('title_code', ['not_exist', 'ru.inactive', 'ru.inactive_db'])
def test_get_entities_by_type_code_and_invalid_title_code(is_http, title_code, update_titles
                                                          ):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """

    response = is_http.cats.get_entities_by_type_code_and_title_code(title_code, entity_type='CURRENCY',
                                                                     code='gold')
    assert_that(response, has_status_code(codes.bad_request), allure_name='response has expected code')
    verify_failed_response(response, CatalogError.TITLE_NOT_FOUND)
