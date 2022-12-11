import allure
import pytest
from hamcrest import has_entries, has_key, any_of, contains_string, matches_regexp
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import CatalogError, PublishStatus, Regex, CatalogTypes
from np_cats_qa.data_generators import generate_catalog_code, generate_catalog_url
from np_cats_qa.matchers import not_empty
from np_cats_qa.verifications import verify_publish_states_in_db, verify_failed_response, \
    verify_publish_completed_with_status_in_db


@allure.feature('cats')
@allure.story('active_catalog')
def test_get_active_catalog_by_title_code_default(is_http, is_db, catalog_url, title_code, catalog_code, publish_id):
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
    response = is_http.cats.get_active_catalog_by_title_code(title_code, 'MAIN')
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.json(), has_entries(catalog_code=catalog_code,
                                             activated_at=not_empty(),
                                             title_code=title_code,
                                             type=CatalogTypes.MAIN_TYPE,
                                             version=not_empty()
                                             ), allure_name='response has expected parameters')
    assert_that(response.headers, has_key('Expires'))
    assert_that(response.headers['Expires'], any_of(contains_string('0 GMT'), contains_string('5 GMT')))


@allure.feature('cats')
@allure.story('active_catalog')
@pytest.mark.parametrize('catalog_code, catalog_url, title_code, catalog_type, tool_name, regexp', [
    (pytest.lazy_fixture('coupon_catalog_code'), pytest.lazy_fixture('coupon_catalog_url'), pytest.lazy_fixture('coupon_title_code'), 'COUPON', 'coupons', Regex.COUPON_CATALOG_CODE),
    (pytest.lazy_fixture('wowp_title_catalog_code'), pytest.lazy_fixture('main_catalog_url'), pytest.lazy_fixture('wowp_title_code'), 'MAIN', 'catool', Regex.MAIN_CATALOG_CODE),
])
def test_get_active_catalog_by_title_code_filter_by_type(is_http, is_db, catalog_url, title_code, catalog_code,
                                                         publish_id,
                                                         catalog_type, tool_name, regexp):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: np_cats_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type catalog_code: str
    :type title_code: str
    :type publish_id: ulid
    """
    # catalog type filters: MAIN, COUPON (see FREYA-757)

    # publish catalog
    response = is_http.cats.publisher_catalog_publish(catalog_url, tool_name, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # verify catalog publication states
    verify_publish_states_in_db(is_db, publish_id)

    # get activate catalog
    response = is_http.cats.get_active_catalog_by_title_code(title_code, type=catalog_type)
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.json(), has_entries(catalog_code=catalog_code,
                                             activated_at=not_empty(),
                                             title_code=title_code,
                                             type=catalog_type,
                                             version=not_empty()
                                             ), allure_name='response has expected parameters')
    assert_that(response.json()['catalog_code'], matches_regexp(regexp), 'incorrect catalog code in filter res')
    assert_that(response.headers, has_key('Expires'))
    assert_that(response.headers['Expires'], any_of(contains_string('0 GMT'), contains_string('5 GMT')))


@allure.feature('cats')
@allure.story('active_catalog')
def test_get_active_catalog_by_title_code_with_no_catalogs(is_http):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    """

    # get activate catalog for title without catalog
    title_code_without_catalog = 'ru.wows'
    response = is_http.cats.get_active_catalog_by_title_code(title_code_without_catalog, 'MAIN')
    assert_that(response, has_status_code(codes.bad_request), allure_name='response has expected code')
    verify_failed_response(response, CatalogError.CATALOG_NOT_FOUND)


@allure.feature('cats')
@allure.story('active_catalog')
@pytest.mark.parametrize('title_code', ['not_exist', 'ru.inactive', 'ru.inactive_db'])
def test_get_active_catalog_by_not_existing_title_code(is_http, title_code, update_titles):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_not_exist: str
    """

    # get activate catalog for title without catalog
    response = is_http.cats.get_active_catalog_by_title_code(title_code, 'MAIN')
    assert_that(response, has_status_code(codes.bad_request), allure_name='response has expected code')
    verify_failed_response(response, CatalogError.TITLE_NOT_FOUND)


@allure.feature('cats')
@allure.story('active_catalog')
def test_get_active_catalog_when_no_active(is_http, is_db, catalog_url, title_code, catalog_publish_id, catalog_id,
                                           catalog_code, publish_id):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: np_cats_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type title_code: str
    :type catalog_publish_id: int
    :type catalog_id: int
    """
    # publish catalog
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # verify catalog publication states
    verify_publish_states_in_db(is_db, publish_id)

    # update catalog in db
    is_db.set_terminated_at_for_catalog(code=catalog_code)

    # get activate catalog
    response = is_http.cats.get_active_catalog_by_title_code(title_code, 'MAIN')
    assert_that(response, has_status_code(codes.bad_request), allure_name='response has expected code')
    verify_failed_response(response, CatalogError.CATALOG_NOT_FOUND)


@allure.feature('cats')
@allure.story('active_catalog')
def test_get_active_catalog_when_it_failed(is_http, is_db, title_for_failed_publish, publish_id, yaml_config):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: np_cats_qa.steps.db.steps.CatalogServiceDBSteps
    :type title_for_failed_publish: str
    """
    # publish catalog
    catalog_code = generate_catalog_code(title_for_failed_publish)
    invalid_catalog_url = generate_catalog_url(yaml_config, 'invalid_url.zip')
    response = is_http.cats.publish(invalid_catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # verify catalog publication states
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.FAILED)

    # get activate catalog
    response = is_http.cats.get_active_catalog_by_title_code(title_for_failed_publish, 'MAIN')
    assert_that(response, has_status_code(codes.bad_request), allure_name='response has expected code')
    verify_failed_response(response, CatalogError.CATALOG_NOT_FOUND)
