import allure
import pytest

from hamcrest import equal_to, has_entries
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.matchers import not_empty


@allure.feature('cats')
@allure.story('ignite')
def test_ignite_info(is_http):
    """
    :type is_http: np_is_qa.steps.CatalogServiceHttpSteps
    """
    response = is_http.cats.ignite_info()
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected status_code')
    assert_that(response.json(), has_entries(node_id=not_empty(),
                                             topology_version=1,
                                             cluster_nodes=not_empty()
                                             ),
                allure_name='response has expected parameters')
    assert_that(response.json()['node_id'], equal_to(response.json()['cluster_nodes'][0]['id']))
