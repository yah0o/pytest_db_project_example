import allure
import pytest
from hamcrest import has_entries, has_key, any_of, contains_string, matches_regexp
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import Regex, CatalogError
from np_cats_qa.matchers import not_empty
from np_cats_qa.verifications import verify_failed_response
from tests.conftest import get_active_catalog_code_by_title_code


@allure.feature('cats')
@allure.story('active_catalogs_by_title_code')
def test_get_active_catalogs_by_title_code_default(is_http, title_code):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """
    # FREYA-757

    # get activate catalogs by title code
    response = is_http.cats.get_active_catalogs_by_title_code(title_code)
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    for catalog in response.json():
        assert_that(catalog, has_entries(terminated_at=None,
                                         activated_at=not_empty(),
                                         catalog_code=not_empty(),
                                         title_code=title_code,
                                         type=not_empty(),
                                         version=not_empty()
                                         ), allure_name='response has expected parameters')
        assert_that([catalog['catalog_code'] for catalog in response.json()
                     if catalog['catalog_code'] == get_active_catalog_code_by_title_code], not_empty(),
                    allure_name='response has expected parameters')
    assert_that(response.headers, has_key('Expires'))
    assert_that(response.headers['Expires'], any_of(contains_string('0 GMT'), contains_string('5 GMT')))


@allure.feature('cats')
@allure.story('active_catalogs_by_title_code')
@pytest.mark.parametrize('catalog_type, regexp', [('MAIN', Regex.MAIN_CATALOG_CODE),
                                                  ('COUPON', Regex.COUPON_CATALOG_CODE)])
def test_get_active_catalogs_filter_by_type(is_http, catalog_type, regexp, title_code):
    # FREYA-758 [for now filter by type: MAIN or COUPON]

    # get activate catalogs by title code
    response = is_http.cats.get_active_catalogs_by_title_code(title_code, type=catalog_type)
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')

    for catalog in response.json():
        assert_that(catalog, has_entries(terminated_at=None,
                                         activated_at=not_empty(),
                                         catalog_code=not_empty(),
                                         title_code=title_code,
                                         type=catalog_type,
                                         version=not_empty()
                                         ), allure_name='response has expected parameters')
        assert_that(catalog['catalog_code'], matches_regexp(regexp), 'incorrect catalog code in filter res')


@allure.feature('cats')
@allure.story('active_catalog')
@pytest.mark.parametrize('title_code', ['not_exist', 'ru.inactive', 'ru.inactive_db'])
def test_get_active_catalogs_by_not_existing_title_code(is_http, title_code, update_titles):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_not_exist: str
    """

    # get activate catalog for title without catalog
    response = is_http.cats.get_active_catalogs_by_title_code(title_code, 'MAIN')
    assert_that(response, has_status_code(codes.bad_request), allure_name='response has expected code')
    verify_failed_response(response, CatalogError.TITLE_NOT_FOUND)