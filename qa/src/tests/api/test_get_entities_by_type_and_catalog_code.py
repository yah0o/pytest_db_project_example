import json
import shutil

import allure
import pytest
from hamcrest import equal_to
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import CatalogZIP


@pytest.fixture
def clear_tmp():
    yield
    shutil.rmtree('tmp')


@allure.feature('cats')
@allure.story('get_entity_by_type')
@pytest.mark.parametrize(('entity_type', 'entity_file'), [
    ('CURRENCY', 'currencies.json'),
    ('ENTITLEMENT', 'entitlements.json'),
    ('PRODUCT', 'products.json'),
    ('STOREFRONT', 'storefronts.json'),
    ('OVERRIDE', 'overrides.json'),
    ('FILTER_PROPERTY', 'filter_properties.json'),
    ('PROMOTION', 'promotions.json')])
def test_get_entity_by_type_and_catalog_code(is_http, entity_type, mock_http,
                                             clear_tmp, entity_file, get_active_catalog_code_by_title_code):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    """

    extract_path = 'tmp/'
    mock_http.extract_catalog_by_catalog_code_to(catalog_file=CatalogZIP.DEFAULT_CATALOG, extract_path=extract_path)

    with open(extract_path + entity_file, 'r+', encoding="utf-8") as f:
        entity_from_catalog = json.load(f)
    response = is_http.cats.get_entities_by_type_and_catalog_code(catalog_code=get_active_catalog_code_by_title_code,
                                                                  entity_type=entity_type)

    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(len(response.json()), equal_to(len(entity_from_catalog)))


@allure.feature('cats')
@allure.story('get_entity_by_type')
def test_get_filter_property_by_type_and_catalog_code(is_http, mock_http, clear_tmp,
                                                      get_active_catalog_code_by_title_code):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    """

    extract_path = 'tmp/'
    entity_type = 'FILTER_PROPERTY'
    entity_file = 'filter_properties.json'

    mock_http.extract_catalog_by_catalog_code_to(catalog_file=CatalogZIP.DEFAULT_CATALOG, extract_path=extract_path)

    with open(extract_path + entity_file, 'r+', encoding="utf-8") as f:
        entity_from_catalog = json.load(f)
    response = is_http.cats.get_entities_by_type_and_catalog_code(catalog_code=get_active_catalog_code_by_title_code,
                                                                  entity_type=entity_type)

    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(len(response.json()), equal_to(len(entity_from_catalog)),
                allure_name='response has expected items number')

    sorted_filter_properties = sorted(response.json(), key=lambda i: i['code'])
    sorted_expected_filter_properties = sorted(entity_from_catalog, key=lambda i: i['code'])

    assert_that(sorted_filter_properties, equal_to(sorted_expected_filter_properties),
                allure_name='response has expected entities')


@allure.feature('cats')
@allure.story('get_entity_by_type')
@pytest.mark.parametrize('language', ["en", "ru", "zh_cn", "zh_sg", "zh_tw"])
@pytest.mark.parametrize(('entity_type', 'entity_file'), [
    ('CURRENCY', 'currencies.json'),
    ('ENTITLEMENT', 'entitlements.json')])
def test_get_entity_by_type_and_catalog_code_language(is_http, entity_type, mock_http,
                                                      clear_tmp, entity_file, get_active_catalog_code_by_title_code,
                                                      language):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    """

    extract_path = 'tmp/'
    mock_http.extract_catalog_by_catalog_code_to(catalog_file=CatalogZIP.DEFAULT_CATALOG, extract_path=extract_path)

    with open(extract_path + entity_file, 'r+', encoding="utf-8") as f:
        entity_from_catalog = json.load(f)
    response = is_http.cats.get_entities_by_type_and_catalog_code(catalog_code=get_active_catalog_code_by_title_code,
                                                                  entity_type=entity_type,
                                                                  language=language)

    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(len(response.json()), equal_to(len(entity_from_catalog)))


@allure.feature('cats')
@allure.story('get_entity_by_type')
def test_get_entity_by_type_and_catalog_code_empty_language(is_http, mock_http,
                                                            clear_tmp, get_active_catalog_code_by_title_code
                                                            ):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    """
    entity_type = 'CURRENCY'
    extract_path = 'tmp/'
    mock_http.extract_catalog_by_catalog_code_to(catalog_file=CatalogZIP.DEFAULT_CATALOG, extract_path=extract_path)

    response = is_http.cats.get_entities_by_type_and_catalog_code(catalog_code=get_active_catalog_code_by_title_code,
                                                                  entity_type=entity_type,
                                                                  language=None)

    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
