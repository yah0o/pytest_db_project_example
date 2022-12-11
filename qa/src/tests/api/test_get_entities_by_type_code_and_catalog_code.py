import json
import shutil

import allure
import pytest
from hamcrest import empty
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import CatalogZIP


@pytest.fixture
def clear_tmp():
    yield
    shutil.rmtree('tmp')


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
def test_get_entity_by_type_code_and_catalog_code(is_http, entity_type, entity_code,
                                                  title_code, mock_http, get_active_catalog_code_by_title_code,
                                                  clear_tmp, code_field, entity_file):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """

    extract_path = 'tmp/'
    mock_http.extract_catalog_by_catalog_code_to(catalog_file=CatalogZIP.DEFAULT_CATALOG, extract_path=extract_path)

    with open(extract_path + entity_file, 'r+', encoding="utf-8") as f:
        entities_from_catalog = json.load(f)
        entity_from_catalog = next(item for item in entities_from_catalog if item[code_field] == entity_code)
    response = is_http.cats.get_entities_by_type_code_and_catalog_code(
        catalog_code=get_active_catalog_code_by_title_code,
        entity_type=entity_type,
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
def test_get_entity_by_type_code_and_catalog_code_negative(is_http, entity_type, entity_code, title_code,
                                                           get_active_catalog_code_by_title_code):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """

    response = is_http.cats.get_entities_by_type_code_and_catalog_code(get_active_catalog_code_by_title_code,
                                                                       entity_type=entity_type,
                                                                       code=entity_code)

    assert_that(response, has_status_code(codes.bad), allure_name='response has expected code')


@allure.feature('cats')
@allure.story('get_entity_by_type_and_code_case_sensitive')
@pytest.mark.parametrize(('entity_type', 'entity_code', 'code_field', 'entity_file'), [
    ('CURRENCY', 'gold', 'currency_code', 'currencies.json'),
    ('FILTER_PROPERTY', 'ent_level', 'code', 'filter_properties.json'),
    ('ENTITLEMENT', 'test_entitlement_generic', 'entitlement_code', 'entitlements.json'),
    ('PRODUCT', 'test_product_entitlement', 'code', 'products.json'),
    ('STOREFRONT', 'test_store', 'code', 'storefronts.json'),
    ('OVERRIDE', 'test_override', 'code', 'overrides.json'),
    ('PROMOTION', 'test_promotion', 'code', 'promotions.json')
])
def test_get_entity_by_type_code_case_sensitive_and_catalog_code(is_http, entity_type, entity_code,
                                                                 mock_http, get_active_catalog_code_by_title_code,
                                                                 clear_tmp, code_field, entity_file):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    """

    extract_path = 'tmp/'
    mock_http.extract_catalog_by_catalog_code_to(catalog_file=CatalogZIP.DEFAULT_CATALOG, extract_path=extract_path)

    with open(extract_path + entity_file, 'r+', encoding="utf-8") as f:
        entities_from_catalog = json.load(f)
        entity_from_catalog = next(item for item in entities_from_catalog if item[code_field] == entity_code)
    response_ok = is_http.cats.get_entities_by_type_code_and_catalog_code(
        catalog_code=get_active_catalog_code_by_title_code,
        entity_type=entity_type,
        code=entity_code)

    response_upper = is_http.cats.get_entities_by_type_code_and_catalog_code(
        catalog_code=get_active_catalog_code_by_title_code,
        entity_type=entity_type,
        code=entity_code.upper())

    assert_that(response_ok, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that([key for key in entity_from_catalog if entity_from_catalog[key] != response_ok.json()[key]],
                empty(), allure_name='Catalog entities are same')

    assert_that(response_upper, has_status_code(codes.bad), allure_name='response has expected code')
