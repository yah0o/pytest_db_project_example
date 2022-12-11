import allure
import pytest
from hamcrest import equal_to
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import CatalogZIP, EntityType, CatalogError


@allure.feature('cats')
@allure.story('get_entity_by_type')
@pytest.mark.parametrize('entity_type', ['not_exist', 123, None])
@pytest.mark.parametrize('by_code', ['title_code', 'catalog_code'])
def test_get_entity_by_type_negative(is_http, entity_type, title_code, get_active_catalog_code_by_title_code,
                                     by_code):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """
    if by_code is 'title_code':
        response = is_http.cats.get_entities_by_type_and_title_code(title_code, entity_type=entity_type)
    else:
        response = is_http.cats.get_entities_by_type_and_catalog_code(get_active_catalog_code_by_title_code,
                                                                      entity_type=entity_type)
    assert_that(response, has_status_code(codes.bad_request), allure_name='response has expected code')


@allure.feature('cats')
@allure.story('get_entity_by_type')
@pytest.mark.parametrize('language', ['not_exist', 1, None, '', True])
def test_get_entity_by_type_and_catalog_code_empty_or_invalid_language(is_http, mock_http,
                                                                       clear_tmp, get_active_catalog_code_by_title_code,
                                                                       language):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    """
    entity_type = 'CURRENCY'
    extract_path = 'tmp/'
    mock_http.extract_catalog_by_catalog_code_to(catalog_file=CatalogZIP.DEFAULT_CATALOG, extract_path=extract_path)

    response = is_http.cats.get_entities_by_type_and_catalog_code(catalog_code=get_active_catalog_code_by_title_code,
                                                                  entity_type=entity_type,
                                                                  language=language)

    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')


@allure.feature('cats')
@allure.story('get_entity_by_type_and_code')
@pytest.mark.parametrize('language', ['not_exist', 1, None, '', True])
def test_get_entity_by_type_and_code_localization_invalid_language(is_http, title_code, language):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """
    entity_type = 'STOREFRONT'
    entity_code = 'test_store_epic_wows_localized'

    response = is_http.cats.get_entities_by_type_code_and_title_code(title_code, entity_type=entity_type,
                                                                     code=entity_code,
                                                                     language=language
                                                                     )
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')


@allure.feature('cats')
@allure.story('get_entity_by_type_and_code')
@pytest.mark.parametrize('entity_type', [EntityType.ENTITLEMENT, EntityType.CURRENCY, EntityType.PRODUCT,
                                         EntityType.STOREFRONT, EntityType.OVERRIDE,
                                         EntityType.PROMOTION, EntityType.FILTER_PROPERTY])
def test_get_entity_by_type_and_title_code_not_exist_entity(is_http, title_code, entity_type):
    entity_code = 'not_exist'

    response = is_http.cats.get_entities_by_type_code_and_title_code(title_code, entity_type=entity_type,
                                                                     code=entity_code
                                                                     )
    assert_that(response, has_status_code(codes.bad), allure_name='response has expected code')
    assert_that(response.json()['error']['code'], equal_to(CatalogError.ENTITY_NOT_FOUND))
    assert_that(response.json()['error']['context']['description'], equal_to('Entity is not found.'))
    assert_that(response.json()['error']['context']['entity_type'], equal_to(entity_type))
    assert_that(response.json()['error']['context']['entity_code'], equal_to('not_exist'))


@allure.feature('cats')
@allure.story('get_entity_by_type_and_code')
@pytest.mark.parametrize('entity_type', [EntityType.ENTITLEMENT, EntityType.CURRENCY, EntityType.PRODUCT,
                                         EntityType.STOREFRONT, EntityType.OVERRIDE,
                                         EntityType.PROMOTION, EntityType.FILTER_PROPERTY])
def test_get_entity_by_type_code_and_catalog_code_not_exist(is_http, entity_type,
                                                            get_active_catalog_code_by_title_code):
    response = is_http.cats.get_entities_by_type_code_and_catalog_code(
        catalog_code=get_active_catalog_code_by_title_code,
        entity_type=entity_type,
        code='not_exist')

    assert_that(response, has_status_code(codes.bad), allure_name='response has expected code')
    assert_that(response.json()['error']['code'], equal_to(CatalogError.ENTITY_NOT_FOUND))
    assert_that(response.json()['error']['context']['description'], equal_to('Entity is not found.'))
    assert_that(response.json()['error']['context']['entity_type'], equal_to(entity_type))
    assert_that(response.json()['error']['context']['entity_code'], equal_to('not_exist'))
