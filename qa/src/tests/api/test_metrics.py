import allure
import pytest
from hamcrest import matches_regexp, equal_to
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.matchers import not_empty
from np_cats_qa.verifications import findMetricValue, findVersionMetricValue


# if local: run test_prepare_catalog first after start containers


@allure.feature('cats')
@allure.story('metrics')
def test_metrics(is_http):
    """
    :type is_http: np_is_qa.steps.CatalogServiceHttpSteps
    """
    response = is_http.cats.metrics()
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected status_code')
    assert_that(response.text, matches_regexp('catalog_pulling_flow_duration_seconds_sum'),
                'resp has no catalog_pulling_sum metric')
    assert_that(response.text, matches_regexp('catalog_parsing_flow_duration_seconds_sum'),
                'resp has no catalog_parsing_sum metric')
    assert_that(response.text, matches_regexp('catalog_saving_flow_duration_seconds_sum'),
                'resp has no catalog_saving_sum metric')
    assert_that(response.text, matches_regexp('catalog_publishing_flow_duration_seconds_sum'),
                'resp has no catalog_publishing_sum metric')
    assert_that(response.text, matches_regexp('catalog_composing_flow_duration_seconds_sum'),
                'resp has no catalog_composing_sum metric')
    assert_that(response.text, matches_regexp('catalog_status_consumer_latency_*'),
                'resp has no catalog_status_consumer_latency metric')
    assert_that(response.text, matches_regexp('http_client_requests_*'),
                'resp has no out_request_ metric')
    assert_that(response.text, matches_regexp('tcs_healthy*'),
                'resp has no out_request_ metric')
    assert_that(response.text, matches_regexp('node_has_master_in_the_cluster*'),
                'resp has no out_request_ metric')
    assert_that(response.text, matches_regexp('db_connection_healthy*'),
                'resp has no out_request_ metric')
    assert_that(response.text, matches_regexp('critical_services_latency_flow_duration_seconds*'),
                'resp has no out_request_ metric')


@allure.feature('cats')
@allure.story('metrics')
def test_metrics_node_has_master_in_the_cluster(is_http):
    # FREYA-570
    """
    :type is_http: np_is_qa.steps.CatalogServiceHttpSteps
    """
    status_of_node = findMetricValue(is_http, 'node_has_master_in_the_cluster')
    assert_that(status_of_node[0], equal_to('1.0'), 'node hasn\'t master in cluster')


@allure.feature('cats')
@allure.story('metrics')
def test_metrics_ignite_cluster_topology_version(is_http):
    # FREYA-673
    """
    :type is_http: np_is_qa.steps.CatalogServiceHttpSteps
    """
    status_of_node = findMetricValue(is_http, 'io_discovery_CurrentTopologyVersion_total')
    assert_that(status_of_node[0], equal_to('1.0'), 'cluster topology version should be 1')


@allure.feature('cats')
@allure.story('metrics')
@pytest.mark.parametrize('label', [
    ('critical_services_latency_flow_duration_seconds_count'),
    ('critical_services_latency_flow_duration_seconds_sum'),
    ('critical_service_latency_prodo_flow_duration_seconds_count'),
    ('critical_service_latency_prodo_flow_duration_seconds_sum'),
    ('franz_service_latency_flow_duration_seconds_count'),
    ('franz_service_latency_flow_duration_seconds_sum'),
    ('http_prodo_request_flow_duration_seconds_count'),
    ('http_prodo_request_flow_duration_seconds_sum'),
    ('http_franz_request_flow_duration_seconds_count'),
    ('http_franz_request_flow_duration_seconds_sum')
])
def test_critical_services_latency_count(is_http, label):
    # FREYA-774
    """
    :type is_http: np_is_qa.steps.CatalogServiceHttpSteps
    """
    prodo_service_latency = findMetricValue(is_http, label, critical_service=True)
    assert_that(prodo_service_latency, not_empty(), 'metric is empty')


@allure.feature('cats')
@allure.story('metrics')
def test_app_version(is_http):
    """
    :type is_http: np_is_qa.steps.CatalogServiceHttpSteps
    """
    status_of_node = findVersionMetricValue(is_http, 'app_version')
    assert_that(status_of_node[0], not_empty(), 'metric is empty')


@allure.feature('cats')
@allure.story('metrics')
def test_metrics_node_has_title_update_in_the_cluster(is_http):
    # FREYA-1158
    """
    :type is_http: np_is_qa.steps.CatalogServiceHttpSteps
    """
    status_of_node = findMetricValue(is_http, 'title_update_in_the_cluster')
    assert_that(status_of_node[0], equal_to('1.0'), 'node hasn\'t master in cluster')
