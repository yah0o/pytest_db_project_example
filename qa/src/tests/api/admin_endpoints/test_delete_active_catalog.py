from time import sleep

import allure
from hamcrest import  empty, is_not
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import CatalogError
from np_cats_qa.verifications import verify_publish_states_in_db, verify_failed_response


@allure.feature('cats')
@allure.story('active_catalog')
def test_delete_active_catalog_by_title_code_default(is_http, is_db, catalog_url, title_code, catalog_code, publish_id):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: np_cats_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type catalog_code: str
    :type title_code: str
    :type publish_id: ulid
    """
    # default catalog type filter is MAIN (FREYA-757)

    # publish catalog
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # verify catalog publication states
    verify_publish_states_in_db(is_db, publish_id)

    # get activate catalog
    response = is_http.cats.delete_active_catalog_by_title_code(title_code, 'MAIN')
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    get_catalog_from_db = is_db.get_catalog_by_catalog_code(catalog_code)
    # check that catalog terminated

    assert_that(get_catalog_from_db['terminated_at'], is_not(empty()))
    # check that there is no active catalog

    sleep(5)  # should be better way
    response = is_http.cats.get_active_catalog_by_title_code(title_code, 'MAIN')
    assert_that(response, has_status_code(codes.bad_request), allure_name='response has expected code')
    verify_failed_response(response, CatalogError.CATALOG_NOT_FOUND)


@allure.feature('cats')
@allure.story('active_catalog')
def test_delete_active_catalog_by_title_code_with_no_active_catalogs(is_http, is_db, title_code):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: np_cats_qa.steps.db.steps.CatalogServiceDBSteps
    :type title_code: str
    """

    # check that there is no active catalog
    response = is_http.cats.get_active_catalog_by_title_code(title_code, 'MAIN')
    assert_that(response, has_status_code(codes.bad_request), allure_name='response has expected code')
    verify_failed_response(response, CatalogError.CATALOG_NOT_FOUND)

    response = is_http.cats.delete_active_catalog_by_title_code(title_code, 'MAIN')
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
