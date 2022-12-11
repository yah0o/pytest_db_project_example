import allure
from npqa_matchers.http import has_text, has_status_code

from npqa_report import assert_that
from requests import codes


@allure.feature('cats')
@allure.story('ping')
def test_ping(is_http):
    """
    :type is_http: np_is_qa.steps.CatalogServiceHttpSteps
    """
    response = is_http.cats.ping()
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected status_code')
    assert_that(response, has_text('pong'), allure_name='response has expected text')
