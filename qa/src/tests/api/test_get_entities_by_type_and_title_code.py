import json
import shutil

import allure
import pytest
from hamcrest import equal_to, empty
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import CatalogZIP, CatalogError
from np_cats_qa.constants import EntitiesBy, Tags
from np_cats_qa.matchers import not_empty
from np_cats_qa.verifications import verify_failed_response


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
def test_get_entity_by_type(is_http, entity_type, title_code, mock_http,
                            clear_tmp, entity_file):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """

    extract_path = 'tmp/'
    mock_http.extract_catalog_by_catalog_code_to(catalog_file=CatalogZIP.DEFAULT_CATALOG, extract_path=extract_path)

    with open(extract_path + entity_file, 'r+', encoding="utf-8") as f:
        entity_from_catalog = json.load(f)
    response = is_http.cats.get_entities_by_type_and_title_code(title_code, entity_type=entity_type)
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(len(response.json()), equal_to(len(entity_from_catalog)))


@allure.feature('cats')
@allure.story('get_entity_by_type')
def test_get_filter_property_by_type(is_http, title_code, mock_http, clear_tmp):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """

    extract_path = 'tmp/'
    entity_type = 'FILTER_PROPERTY'
    entity_file = 'filter_properties.json'
    mock_http.extract_catalog_by_catalog_code_to(catalog_file=CatalogZIP.DEFAULT_CATALOG, extract_path=extract_path)

    with open(extract_path + entity_file, 'r+', encoding="utf-8") as f:
        entity_from_catalog = json.load(f)
    response = is_http.cats.get_entities_by_type_and_title_code(title_code, entity_type=entity_type)

    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(len(response.json()), equal_to(len(entity_from_catalog)),
                allure_name='response has expected items number')

    sorted_filter_properties = sorted(response.json(), key=lambda i: i['code'])
    sorted_expected_filter_properties = sorted(entity_from_catalog, key=lambda i: i['code'])

    assert_that(sorted_filter_properties, equal_to(sorted_expected_filter_properties),
                allure_name='response has expected entities')


@allure.feature('cats')
@allure.story('get_entity_by_type')
@pytest.mark.parametrize(('entity_type', 'tags', 'expected_tag_result'), [
    ('ENTITLEMENT', Tags.PREMIUM_EQUIPMENT, EntitiesBy.EXPECTED_TAG_ENTITLEMENT),
    ('ENTITLEMENT', Tags.BATTLE_PASS, EntitiesBy.EXPECTED_TAG_ENTITLEMENT),
    ('PRODUCT', Tags.PREMIUM_EQUIPMENT, EntitiesBy.EXPECTED_TAG_PRODUCT),
    ('PRODUCT', Tags.BATTLE_PASS, EntitiesBy.EXPECTED_TAG_PRODUCT)
])
def test_get_entity_by_type_and_tags(is_http, entity_type, title_code, tags, expected_tag_result):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """
    # FREYA-1007
    # We have tags only in the ENTITLEMENTS and PRODUCTS

    response = is_http.cats.get_entities_by_type_and_title_code(title_code,
                                                                entity_type=entity_type,
                                                                tags=tags)
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    if entity_type == 'ENTITLEMENT':
        assert_that(response.json()[0]['entitlement_code'], equal_to(expected_tag_result),
                    allure_name='response has expected product filtered by tag')
    else:
        assert_that(response.json()[0]['code'], equal_to(expected_tag_result),
                    allure_name='response has expected product filtered by tag')


@allure.feature('cats')
@allure.story('get_entity_by_type')
@pytest.mark.parametrize(('entity_type', 'expected_amount'), [
    ('ENTITLEMENT', 2),
    ('PRODUCT', 7),
])
def test_get_entity_by_type_and_several_tags(is_http, entity_type, title_code, expected_amount):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """
    # FREYA-1007
    # based on tags entitlements, products count of catalog entities

    response = is_http.cats.get_entities_by_type_and_title_code(title_code,
                                                                entity_type=entity_type,
                                                                tags=Tags.PREMIUM_EQUIPMENT + ',' + Tags.TEST)
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    # Check that response has correct amount of entitlements [OR operator, 2 entitlements expected, 7 products]
    assert_that(len(response.json()), equal_to(expected_amount),
                allure_name='response has expected amount of entitlements filtered by tag')


@allure.feature('cats')
@allure.story('get_entity_by_type')
@pytest.mark.parametrize('tags', ['not_exist', 123, 'Test', ''])
@pytest.mark.parametrize('entity_type', ['ENTITLEMENT', 'PRODUCT'])
def test_get_entity_by_type_invalid_or_empty_tags(is_http, title_code,
                                                  tags, entity_type):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """

    response = is_http.cats.get_entities_by_type_and_title_code(title_code,
                                                                entity_type=entity_type,
                                                                tags=tags)
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    if tags == '':
        assert_that(response.json(), not_empty(), allure_name='not empty response when filtering by empty tags')
    else:
        assert_that(response.json(), empty(), allure_name='empty response when filtering by invalid tags')


@allure.feature('cats')
@allure.story('get_entity_by_type')
@pytest.mark.parametrize('language', ["en", "ru", "zh_cn", "zh_sg", "zh_tw"])
@pytest.mark.parametrize(('entity_type', 'entity_file'), [
    ('CURRENCY', 'currencies.json'),
    ('ENTITLEMENT', 'entitlements.json')])
def test_get_entity_by_type_language(is_http, clear_tmp, entity_type, title_code, mock_http, entity_file, language):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """

    extract_path = 'tmp/'
    mock_http.extract_catalog_by_catalog_code_to(catalog_file=CatalogZIP.DEFAULT_CATALOG, extract_path=extract_path)

    with open(extract_path + entity_file, 'r+', encoding="utf-8") as f:
        entity_from_catalog = json.load(f)
    response = is_http.cats.get_entities_by_type_and_title_code(title_code, entity_type=entity_type, language=language)
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(len(response.json()), equal_to(len(entity_from_catalog)))


@allure.feature('cats')
@allure.story('get_entity_by_type')
@pytest.mark.parametrize('title_code', ['not_exist', 'ru.inactive', 'ru.inactive_db'])
@pytest.mark.parametrize('entity_type', ['ENTITLEMENT', 'PRODUCT'])
def test_get_entity_by_type_invalid_title_code(is_http, title_code, update_titles,
                                               entity_type):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """

    response = is_http.cats.get_entities_by_type_and_title_code(title_code,
                                                                entity_type=entity_type)
    assert_that(response, has_status_code(codes.bad_request), allure_name='response has expected code')
    verify_failed_response(response, CatalogError.TITLE_NOT_FOUND)
