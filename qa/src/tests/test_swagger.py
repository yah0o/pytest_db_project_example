import allure

from npqa_matchers.http import has_status_code

from npqa_report import assert_that
from requests import codes


@allure.feature('cats')
@allure.story('swagger')
def test_swagger_ok(is_http):
    """
    :type is_http: np_is_qa.steps.CatalogServiceHttpSteps
    """
    response = is_http.cats.swagger()
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected status_code')
