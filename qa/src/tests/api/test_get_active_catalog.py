import allure
import pytest
from hamcrest import has_entries, has_key, any_of, contains_string, equal_to, matches_regexp
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import CatalogTypes, Regex
from np_cats_qa.matchers import not_empty


@allure.feature('cats')
@allure.story('active_catalogs')
def test_get_active_catalog_default(is_http, is_db, get_active_catalog_code_by_title_code):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :return: MAIN active catalogs by default (see FREYA-758)
    """

    response = is_http.cats.get_active_catalog('MAIN')
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.headers, has_key('Expires'))
    assert_that(response.headers['Expires'], any_of(contains_string('0 GMT'), contains_string('5 GMT')))

    for catalog in response.json():
        assert_that(catalog, has_entries(terminated_at=None,
                                         activated_at=not_empty(),
                                         catalog_code=not_empty(),
                                         title_code=not_empty(),
                                         type=not_empty(),
                                         version=not_empty()
                                         ), allure_name='response has expected parameters')
        assert_that(catalog['title_code'] + '-' + catalog['type'] + '-' + str(catalog['version']),
                    equal_to(catalog['catalog_code']), 'incorrect catalog code in filter res')
    assert_that([catalog['catalog_code'] for catalog in response.json()
                 if catalog['catalog_code'] == get_active_catalog_code_by_title_code], not_empty(),
                allure_name='response has expected parameters')
    assert_that(len(response.json()), equal_to(len(set([catalog['catalog_code'] for catalog in response.json()]))),
                allure_name='response has unique catalog codes')

    assert_that(sorted(is_db.get_active_catalogs(catalog_type=CatalogTypes.MAIN)),
                equal_to(sorted([catalog['catalog_code'] for catalog in response.json()])),
                allure_name='same catalog codes like in db')


@allure.feature('cats')
@allure.story('active_catalogs')
@pytest.mark.parametrize('catalog_type, ctype, regexp', [('MAIN', CatalogTypes.MAIN, Regex.MAIN_CATALOG_CODE),
                                                         ('COUPON', CatalogTypes.COUPON, Regex.COUPON_CATALOG_CODE)])
def test_get_active_catalog_filter_by_type(is_http, is_db, catalog_type, ctype, regexp):
    # FREYA-758 [for now filter by type: MAIN or COUPON]

    response = is_http.cats.get_active_catalog(type=catalog_type)
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.headers, has_key('Expires'))
    assert_that(response.headers['Expires'], any_of(contains_string('0 GMT'), contains_string('5 GMT')))

    for catalog in response.json():
        assert_that(catalog, has_entries(terminated_at=None,
                                         activated_at=not_empty(),
                                         catalog_code=not_empty(),
                                         title_code=not_empty(),
                                         type=not_empty(),
                                         version=not_empty()), allure_name='response has expected parameters')
        assert_that(catalog['catalog_code'], matches_regexp(regexp), 'incorrect catalog code in filter res')
        assert_that(catalog['title_code'] + '-' + catalog['type'] + '-' + str(catalog['version']),
                    equal_to(catalog['catalog_code']), 'incorrect catalog code in filter res')

    assert_that(len(response.json()), equal_to(len(set([catalog['catalog_code'] for catalog in response.json()]))),
                allure_name='response has unique catalog codes')
    assert_that(sorted(is_db.get_active_catalogs(catalog_type=ctype)),
                equal_to(sorted([catalog['catalog_code'] for catalog in response.json()])),
                allure_name='same catalog codes like in db')


@allure.feature('cats')
@allure.story('active_catalogs')
def test_get_active_catalog_etag(is_http):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    """

    response_with_etag = is_http.cats.get_active_catalog('MAIN')
    response = is_http.cats.get_active_catalog('MAIN', headers={"If-None-Match": response_with_etag.headers['ETag']})
    assert_that(response, has_status_code(codes.not_modified), allure_name='response has expected code')
