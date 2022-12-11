import allure
import pytest
from hamcrest import has_entry
from np_cats_qa.constants import PublishError
from np_cats_qa.verifications import verify_failed_response
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes


@allure.feature('cats')
@allure.story('publish_validation')
@pytest.mark.parametrize('publish_id', [
    'test',
    0,
    '01E07F4HQAKK2JNWEPQY2RGWVPextra',
    [],
    {}
])
def test_get_publish_status_with_invalid_catalog_publish_id(is_http, publish_id):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type catalog_publish_id: int
    """

    # get publish status
    publish_status_response = is_http.cats.get_catalog_publish_status(publish_id)
    assert_that(publish_status_response, has_status_code(codes.bad_request), allure_name='response has expected code')

    verify_failed_response(publish_status_response, PublishError.VALIDATION_ERROR)


@allure.feature('cats')
@allure.story('publish_validation')
@pytest.mark.parametrize('publish_id,', [
    '',
    pytest.param(' ', marks=pytest.mark.skip(reason='FREYA-459'))
])
def test_get_catalog_publish_status_when_catalog_publish_id_missing(is_http, publish_id):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type catalog_publish_id: int
    """
    publish_status_response = is_http.cats.get_catalog_publish_status(publish_id)
    assert_that(publish_status_response, has_status_code(codes.not_found), allure_name='response has expected code')
    assert_that(publish_status_response.json()['error'], has_entry('code', PublishError.CLIENT_ERROR),
                allure_name='response has expected error_code')
