import pytest
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import PublishStatus, TitleCode, CatalogZIP
from np_cats_qa.helpers import ulid
from np_cats_qa.verifications import verify_publish_completed_with_status_in_db

'''
This test should be run at first before all test suite. 
'''


@pytest.mark.prepare_data
def test_publish_catalog(is_http, is_db, catalog_url, title_code, catalog_code, publish_id, mock_steps, yaml_config):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type mock_steps: db_prj_qa.steps.mock.steps.CatalogServiceMockSteps
    :type catalog_url: str
    :type title_code: str
    :type catalog_code: str
    :type publish_id: str
    """
    mock_steps.journal_clear_history()

    # prepare shared currency data
    shared_currency_catalog_url = yaml_config.data.CATALOG_DOMAIN + '/' + CatalogZIP.SHARED_CURRENCY_CATALOG
    shared_currency_catalog_code = '{}-MAIN-1'.format(TitleCode.SHARED_CURRENCY)

    # publish shared_currency catalog
    response_publish = is_http.cats.publish(shared_currency_catalog_url, shared_currency_catalog_code, publish_id)
    assert_that(response_publish, has_status_code(codes.created), allure_name='response has expected code')
    # verify shared currency catalog publication states
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    # publish test catalog
    new_publish_id = ulid()
    response = is_http.cats.publish(catalog_url, catalog_code, new_publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # verify MAIN catalog publication states
    verify_publish_completed_with_status_in_db(is_db, new_publish_id, PublishStatus.COMPLETED)
