import allure
import pytest
from hamcrest import equal_to
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import CatalogTypes, CatalogError, PublishError


@allure.feature('cats')
@allure.story('test_get_overridden_product')
@pytest.mark.parametrize('catalog_code, expected_error', [
    ('ru.test-MAIN-1', codes.bad),
    ('', codes.not_found),
    ([], codes.bad),
    ({}, codes.bad),
    (123, codes.bad)])
def test_get_product_with_incorrect_catalog_code(is_http, title_code, catalog_code, expected_error):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """
    product_code = 'product_with_expired_promo'
    promo_code = 'test_override_promo'
    storefront_code = 'test_store'

    response = is_http.cats.get_product_with_applied_promo(catalog_code=catalog_code,
                                                           product_code=product_code,
                                                           promo_code=promo_code,
                                                           storefront_code=storefront_code)

    error_code = PublishError.CLIENT_ERROR if expected_error == codes.not_found else CatalogError.CATALOG_NOT_FOUND
    assert_that(response, has_status_code(expected_error), allure_name='response has expected code')
    assert_that(response.json()['error']['code'], equal_to(error_code), allure_name='response has expected error')


@allure.feature('cats')
@allure.story('test_get_overridden_product')
@pytest.mark.parametrize('product_code, expected_error', [
    ('test', codes.bad),
    ('', codes.not_found),
    ([], codes.bad),
    ({}, codes.bad),
    (123, codes.bad)])
def test_get_product_with_incorrect_product_code(is_http, title_code, product_code, expected_error):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """
    promo_code = 'test_override_promo'
    storefront_code = 'test_store'

    active_catalog = is_http.cats.get_active_catalog_by_title_code(title_code, CatalogTypes.MAIN_TYPE)

    response = is_http.cats.get_product_with_applied_promo(catalog_code=active_catalog.json()['catalog_code'],
                                                           product_code=product_code,
                                                           promo_code=promo_code,
                                                           storefront_code=storefront_code)

    error_code = PublishError.CLIENT_ERROR if expected_error == codes.not_found else CatalogError.ENTITY_NOT_FOUND
    assert_that(response, has_status_code(expected_error), allure_name='response has expected code')
    assert_that(response.json()['error']['code'], equal_to(error_code), allure_name='response has expected error')


@allure.feature('cats')
@allure.story('test_get_overridden_product')
@pytest.mark.parametrize('promo_code, expected_error', [
    ('test', codes.bad),
    ('', codes.bad),
    ([], codes.bad),
    ({}, codes.bad),
    (123, codes.bad)])
def test_get_product_with_incorrect_promo_code(is_http, title_code, promo_code, expected_error):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """
    product_code = 'product_with_expired_promo'
    storefront_code = 'test_store'

    active_catalog = is_http.cats.get_active_catalog_by_title_code(title_code, CatalogTypes.MAIN_TYPE)

    response = is_http.cats.get_product_with_applied_promo(catalog_code=active_catalog.json()['catalog_code'],
                                                           product_code=product_code,
                                                           promo_code=promo_code,
                                                           storefront_code=storefront_code)

    error_code = PublishError.CLIENT_ERROR if expected_error == codes.not_found else CatalogError.ENTITY_NOT_FOUND
    assert_that(response, has_status_code(expected_error), allure_name='response has expected code')
    assert_that(response.json()['error']['code'], equal_to(error_code), allure_name='response has expected error')


@allure.feature('cats')
@allure.story('test_get_overridden_product')
@pytest.mark.parametrize('storefront_code, expected_error', [
    ('test', codes.bad),
    ('', codes.bad),
    ([], codes.bad),
    ({}, codes.bad),
    (123, codes.bad)])
def test_get_product_with_incorrect_storefront_code(is_http, title_code, storefront_code, expected_error):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """
    product_code = 'product_with_expired_promo'
    promo_code = 'test_override_promo'

    active_catalog = is_http.cats.get_active_catalog_by_title_code(title_code, CatalogTypes.MAIN_TYPE)

    response = is_http.cats.get_product_with_applied_promo(catalog_code=active_catalog.json()['catalog_code'],
                                                           product_code=product_code,
                                                           promo_code=promo_code,
                                                           storefront_code=storefront_code)

    error_code = PublishError.CLIENT_ERROR if expected_error == codes.not_found else CatalogError.ENTITY_NOT_FOUND
    assert_that(response, has_status_code(expected_error), allure_name='response has expected code')
    assert_that(response.json()['error']['code'], equal_to(error_code), allure_name='response has expected error')
