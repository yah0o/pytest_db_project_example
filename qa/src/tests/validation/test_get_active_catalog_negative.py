import allure
import pytest
from hamcrest import equal_to
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import PublishError, CatalogError
from np_cats_qa.verifications import verify_failed_response


@allure.feature('cats')
@allure.story('get_active_catalog_by_title_code_validation')
@pytest.mark.parametrize('title_code, error, status_codes',
                         [
                             ('', PublishError.CLIENT_ERROR, codes.not_found),
                             ([], PublishError.TITLE_NOT_FOUND, codes.bad_request),
                             ({}, PublishError.TITLE_NOT_FOUND, codes.bad_request),
                          ])
def test_get_active_catalog_by_invalid_title_code(is_http, title_code, error, status_codes):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    """
    response = is_http.cats.get_active_catalog_by_title_code(title_code, 'MAIN')
    assert_that(response, has_status_code(status_codes), allure_name='response has expected code')
    verify_failed_response(response, error)


@allure.feature('cats')
@allure.story('get_active_catalog_by_title_code_validation')
@pytest.mark.parametrize('catalog_type', ['NOT_EXIST', 123])
def test_get_active_catalog_by_title_code_not_exist_filter(is_http, title_code, catalog_type):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    """
    response = is_http.cats.get_active_catalog_by_title_code(title_code, type=catalog_type)
    assert_that(response, has_status_code(codes.bad_request), allure_name='response has expected code')
    # Need to change error message after fix
    verify_failed_response(response, CatalogError.CLIENT_ERROR)
    assert_that(response.json()['error']['context']['description'], equal_to(CatalogError.CATALOG_TYPE_CONTEXT))


@allure.feature('cats')
@allure.story('get_active_catalog_by_title_code_validation')
@pytest.mark.parametrize('catalog_type', ['NOT_EXIST', 123])
def test_get_active_catalog_by_title_code_not_exist_catalog(is_http, title_code, catalog_type):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    """
    response = is_http.cats.get_active_catalog_by_title_code(title_code, type=catalog_type)
    assert_that(response, has_status_code(codes.bad_request), allure_name='response has expected code')
    # Need to change error message after fix
    assert_that(response.json()['error']['code'], equal_to(CatalogError.CLIENT_ERROR))
    assert_that(response.json()['error']['context']['description'], equal_to(CatalogError.CATALOG_TYPE_CONTEXT))


@allure.feature('cats')
@allure.story('get_active_catalogs_validation')
@pytest.mark.parametrize('catalog_type', ['NOT_EXIST', 123])
def test_get_active_catalog_not_exist_filter(is_http, title_code, catalog_type):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    """
    response = is_http.cats.get_active_catalog(type=catalog_type)
    assert_that(response, has_status_code(codes.bad_request), allure_name='response has expected code')
    # Need to change error message after fix
    verify_failed_response(response, CatalogError.CLIENT_ERROR)
    assert_that(response.json()['error']['context']['description'], equal_to(CatalogError.CATALOG_TYPE_CONTEXT))


@allure.feature('cats')
@allure.story('get_active_catalogs_by_title_code_validation')
@pytest.mark.parametrize('title_code, error, status_codes',
                         [
                             ('', PublishError.CLIENT_ERROR, codes.not_found),
                             ([], PublishError.TITLE_NOT_FOUND, codes.bad_request),
                             ({}, PublishError.TITLE_NOT_FOUND, codes.bad_request),
                          ])
def test_get_active_catalogs_by_invalid_title_code(is_http, title_code, error, status_codes):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    """
    response = is_http.cats.get_active_catalogs_by_title_code(title_code)
    assert_that(response, has_status_code(status_codes), allure_name='response has expected code')

    verify_failed_response(response, error)


@allure.feature('cats')
@allure.story('get_active_catalogs_by_title_code_validation')
@pytest.mark.parametrize('catalog_type', ['NOT_EXIST', 123])
def test_get_active_catalogs_by_title_code_not_exist_filter(is_http, title_code, catalog_type):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    """
    response = is_http.cats.get_active_catalogs_by_title_code(title_code, type=catalog_type)
    assert_that(response, has_status_code(codes.bad_request), allure_name='response has expected code')
    # Need to change error message after fix
    verify_failed_response(response, CatalogError.CLIENT_ERROR)
    assert_that(response.json()['error']['context']['description'], equal_to(CatalogError.CATALOG_TYPE_CONTEXT))
