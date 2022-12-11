import allure
import pytest
from hamcrest import has_entries, contains_string
from np_cats_qa.constants import PublishStatus, CatalogStatus, TitleCode
from np_cats_qa.data_generators import generate_catalog_code
from np_cats_qa.matchers import not_empty
from np_cats_qa.verifications import verify_franz_event_sent, verify_publish_completed_with_status_in_db, \
    has_valid_catalog_publish_info
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes


@allure.feature('cats')
@allure.story('franz_success')
def test_success_event(is_http, is_db, catalog_url, title_code, catalog_code, publish_id, mock_steps):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: np_cats_qa.steps.db.steps.CatalogServiceDBSteps
    :type mock_steps: np_cats_qa.steps.mock.steps.CatalogServiceMockSteps
    :type catalog_url: str
    :type title_code: str
    :type catalog_code: str
    :type publish_id: str
    """
    mock_steps.journal_clear_history()

    # publish catalog
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # waiting FAILED or COMPLETED status
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    verify_franz_event_sent(mock_steps, catalog_code=catalog_code, title_code=title_code)

    # get activate catalog
    response = is_http.cats.get_active_catalog_by_title_code(title_code, 'MAIN')
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.json(), has_entries(catalog_code=catalog_code,
                                             activated_at=not_empty(),
                                             terminated_at=None),
                allure_name='response has expected parameters')


@allure.feature('cats')
@allure.story('franz_failure')
@pytest.mark.parametrize('title_code, error_code', [
    (TitleCode.FRANZ_200_FAILURE, 'franz_200_error_code'),
    (TitleCode.FRANZ_400_FAILURE, 'franz_400_error_code'),
    (TitleCode.FRANZ_EMPTY_RESPONSE_FAILURE, 'Got empty response from the franz.')
])
def test_failure(is_http, is_db, catalog_url, title_code, error_code, publish_id):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: np_cats_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type title_code: str
    :type catalog_code: str
    :type publish_id: str
    """

    catalog_code = generate_catalog_code(title_code)
    # publish catalog
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # waiting FAILED or COMPLETED status
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.FAILED)

    failure = is_db.get_task_failure(publish_id)
    assert_that(failure, contains_string('franz:{}'.format(error_code)),
                allure_name='Should contain response error code')

    # check catalog publish status
    publish_status = is_http.cats.get_catalog_publish_status(publish_id)
    assert_that(publish_status, has_status_code(codes.ok), allure_name='response has expected code')

    catalog_publish_info = publish_status.json()[0]
    assert_that(catalog_publish_info, has_valid_catalog_publish_info(status=CatalogStatus.FAILED,
                                                                     publish_id=publish_id,
                                                                     catalog_code=catalog_code),
                allure_name='catalog_publish_status response is correct')
