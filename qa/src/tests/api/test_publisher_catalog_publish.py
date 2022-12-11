import allure
import pytest
from hamcrest import has_entries, equal_to, contains_string, is_not
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import PublishStatus, CatalogStatus, TitleCode
from np_cats_qa.data_generators import generate_catalog_code
from np_cats_qa.helpers import ulid
from np_cats_qa.matchers import not_empty
from np_cats_qa.verifications import verify_prepare_method_called, \
    verify_activated_method_called, \
    has_valid_catalog_publish_info, verify_catools_notification_sent, verify_publish_completed_with_status_in_db, \
    verify_coupons_notification_sent


@allure.feature('cats')
@allure.story('publisher_catalog_publish')
@pytest.mark.parametrize('publish_catalog_code, catalog_url, publish_title_code, catalog_type, tool_name', [
    (pytest.lazy_fixture('coupon_catalog_code'), pytest.lazy_fixture('coupon_catalog_url'),
     pytest.lazy_fixture('coupon_title_code'), 'COUPON', 'coupons'),
    (pytest.lazy_fixture('wowp_title_catalog_code'), pytest.lazy_fixture('main_catalog_url'),
     pytest.lazy_fixture('wowp_title_code'), 'MAIN', 'catool'),
    (pytest.lazy_fixture('catalog_code'), pytest.lazy_fixture('main_catalog_url'),
     pytest.lazy_fixture('title_code'), 'MAIN', 'manual'),
])
def test_publisher_catalog_publish(is_http, is_db, catalog_url, publish_catalog_code, publish_title_code, publish_id,
                                   mock_steps, catalog_type,
                                   tool_name):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: np_cats_qa.steps.db.steps.CatalogServiceDBSteps
    :type mock_steps: np_cats_qa.steps.mock.steps.CatalogServiceMockSteps
    :type catalog_url: str
    :type publish_title_code: str
    :type catalog_code: str
    :type publish_id: str
    """
    # Publish test for main and coupons catalogs

    mock_steps.journal_clear_history()

    # publish catalog
    response = is_http.cats.publisher_catalog_publish(catalog_url, tool_name, publish_catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # verify catalog publication states
    # wait for catalog published
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    # verify notification about catalog status sent
    if tool_name == 'catool':
        verify_catools_notification_sent(mock_steps, status=CatalogStatus.ACTIVATED, publish_id=publish_id,
                                         catalog_code=publish_catalog_code)
    elif tool_name == 'coupons':
            verify_coupons_notification_sent(mock_steps, status=CatalogStatus.ACTIVATED, publish_id=publish_id,
                                             catalog_code=publish_catalog_code)
    # verify 'prepare' and 'activated' methods_called
    verify_prepare_method_called(mock_steps, catalog_code=publish_catalog_code)
    verify_activated_method_called(mock_steps, catalog_code=publish_catalog_code)

    # get activate catalog
    response = is_http.cats.get_active_catalog_by_title_code(publish_title_code, catalog_type)
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.json(), has_entries(catalog_code=publish_catalog_code,
                                             activated_at=not_empty(),
                                             terminated_at=None),
                allure_name='response has expected parameters')


@allure.feature('cats')
@allure.story('publisher_catalog_publish')
@pytest.mark.parametrize('catalog_code, catalog_url, title_code, catalog_type, tool_name', [
    (pytest.lazy_fixture('coupon_catalog_code'), pytest.lazy_fixture('coupon_catalog_url'),
     pytest.lazy_fixture('coupon_title_code'), 'COUPON', 'coupons'),
    (pytest.lazy_fixture('wowp_title_catalog_code'), pytest.lazy_fixture('main_catalog_url'),
     pytest.lazy_fixture('wowp_title_code'), 'MAIN', 'catool'),
])
def test_publisher_catalog_publish_twice_with_the_same_catalog_and_publish_ids(is_http, is_db, catalog_url, title_code,
                                                                               catalog_code,
                                                                               publish_id, catalog_type, tool_name):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: np_cats_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type title_code: str
    :type catalog_code: str
    :type publish_id: str
    """
    # publish catalog
    publish_response = is_http.cats.publisher_catalog_publish(catalog_url, tool_name, catalog_code, publish_id)
    assert_that(publish_response, has_status_code(codes.created), allure_name='response has expected code')

    # wait for catalog published
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    # get active catalog
    catalog_info_1 = is_http.cats.get_active_catalog_by_title_code(title_code, catalog_type)
    assert_that(catalog_info_1, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(catalog_info_1.json(), has_entries(catalog_code=catalog_code,
                                                   activated_at=not_empty(),
                                                   terminated_at=None),
                allure_name='response has expected parameters')

    # call publish again
    publish_response_2 = is_http.cats.publisher_catalog_publish(catalog_url, tool_name, catalog_code, publish_id)
    assert_that(publish_response_2, has_status_code(codes.created), allure_name='response has expected code')

    # get activate catalog after second publish
    catalog_info_2 = is_http.cats.get_active_catalog_by_title_code(title_code, catalog_type)
    assert_that(catalog_info_2, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(catalog_info_2.json(), has_entries(catalog_code=catalog_code,
                                                   activated_at=not_empty(),
                                                   terminated_at=None),
                allure_name='response has expected parameters')

    # verify active catalog info wasn't changed
    assert_that(catalog_info_1.content, equal_to(catalog_info_2.content),
                allure_name='catalog info was not changed after second publish request')


@allure.feature('cats')
@allure.story('publisher_catalog_publish')
@pytest.mark.parametrize('catalog_code, catalog_url, title_code, catalog_type, tool_name, nxt_catalog_code', [
    (pytest.lazy_fixture('coupon_catalog_code'), pytest.lazy_fixture('coupon_catalog_url'),
     pytest.lazy_fixture('coupon_title_code'), 'COUPON', 'coupons',
     pytest.lazy_fixture('coupon_catalog_code_next')),
    (pytest.lazy_fixture('wowp_title_catalog_code'), pytest.lazy_fixture('main_catalog_url'),
     pytest.lazy_fixture('wowp_title_code'), 'MAIN', 'catool',
     pytest.lazy_fixture('wowp_title_catalog_code_next')),
])
def test_publisher_catalog_publish_new_catalog_and_check_old_terminated(is_http, is_db, catalog_url, title_code,
                                                                        mock_steps,
                                                                        catalog_code,
                                                                        nxt_catalog_code, publish_id, catalog_type,
                                                                        tool_name):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: np_cats_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type title_code: str
    :type catalog_code: str
    :type catalog_code_next: str
    :type publish_id: str
    """
    mock_steps.journal_clear_history()

    # publish first catalog
    publish_response = is_http.cats.publisher_catalog_publish(catalog_url, tool_name, catalog_code, publish_id)
    assert_that(publish_response, has_status_code(codes.created), allure_name='response has expected code')

    # wait for catalog published
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)
    # verify notification about catalog status sent
    if tool_name == 'catool':
        verify_catools_notification_sent(mock_steps, status=CatalogStatus.ACTIVATED, publish_id=publish_id,
                                         catalog_code=catalog_code)
    else:
        verify_coupons_notification_sent(mock_steps, status=CatalogStatus.ACTIVATED, publish_id=publish_id,
                                         catalog_code=catalog_code)

    mock_steps.journal_clear_history()

    new_publish_id = ulid()
    # publish second catalog
    publish_response_2 = is_http.cats.publisher_catalog_publish(catalog_url, tool_name, nxt_catalog_code,
                                                                new_publish_id)
    assert_that(publish_response_2, has_status_code(codes.created), allure_name='response has expected code')

    # wait for catalog published
    verify_publish_completed_with_status_in_db(is_db, new_publish_id, PublishStatus.COMPLETED)

    # verify catalogs activation and termination time
    catalog_1_time = is_db.get_task_processing_time(publish_id)
    catalog_2_time = is_db.get_task_processing_time(new_publish_id)
    assert_that(catalog_1_time['terminated_at'], equal_to(catalog_2_time['activated_at']),
                allure_name='catalog1 terminated when catalog2 activated')

    # get activate catalog
    response = is_http.cats.get_active_catalog_by_title_code(title_code, catalog_type)
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.json(), has_entries(catalog_code=nxt_catalog_code,
                                             activated_at=not_empty(),
                                             terminated_at=None),
                allure_name='response has expected parameters')

    # verify notification about catalog status sent
    if tool_name == 'catool':
        verify_catools_notification_sent(mock_steps, status=CatalogStatus.ACTIVATED, publish_id=new_publish_id,
                                         catalog_code=nxt_catalog_code)
        verify_catools_notification_sent(mock_steps, status=CatalogStatus.TERMINATED, publish_id=publish_id,
                                         catalog_code=catalog_code)
    else:
        verify_coupons_notification_sent(mock_steps, status=CatalogStatus.ACTIVATED, publish_id=new_publish_id,
                                         catalog_code=nxt_catalog_code)
        verify_coupons_notification_sent(mock_steps, status=CatalogStatus.TERMINATED, publish_id=publish_id,
                                         catalog_code=catalog_code)


@allure.feature('cats')
@allure.story('publisher_catalog_publish')
@pytest.mark.parametrize('catalog_code, catalog_url, title_code, catalog_type, tool_name', [
    (pytest.lazy_fixture('coupon_catalog_code'), pytest.lazy_fixture('coupon_catalog_url'),
     pytest.lazy_fixture('coupon_title_code'), 'COUPON', 'coupons'),
    (pytest.lazy_fixture('wowp_title_catalog_code'), pytest.lazy_fixture('main_catalog_url'),
     pytest.lazy_fixture('wowp_title_code'), 'MAIN', 'catool')
])
def test_publisher_catalog_publish_catalog_after_failed_status(is_http, is_db, mock_steps, catalog_url, title_code,
                                                               catalog_code,
                                                               publish_id, catalog_type, tool_name):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: np_cats_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type catalog_code: str
    :type publish_id: str
    """
    # to exclude invalid domain caching
    domain = ulid()
    # call publish to get FAILED status
    invalid_catalog_url = 'http://{}.ru/not_exist.zip'.format(domain)
    response_publish_1 = is_http.cats.publisher_catalog_publish(invalid_catalog_url, tool_name, catalog_code,
                                                                publish_id)
    assert_that(response_publish_1, has_status_code(codes.created), allure_name='response has expected code')

    # waiting FAILED or COMPLETED status
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.FAILED)

    if tool_name == 'catool':
        verify_catools_notification_sent(mock_steps, status=CatalogStatus.FAILED, publish_id=publish_id,
                                         catalog_code=catalog_code)
    else:
        verify_coupons_notification_sent(mock_steps, status=CatalogStatus.FAILED, publish_id=publish_id,
                                         catalog_code=catalog_code)

    new_publish_id = ulid()
    # call publish with correct parameters
    response_publish_2 = is_http.cats.publisher_catalog_publish(catalog_url, tool_name, catalog_code, new_publish_id)
    assert_that(response_publish_2, has_status_code(codes.created), allure_name='response has expected code')
    verify_publish_completed_with_status_in_db(is_db, new_publish_id, PublishStatus.COMPLETED)

    # get activate catalog
    response = is_http.cats.get_active_catalog_by_title_code(title_code, catalog_type)
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.json(), has_entries(catalog_code=catalog_code,
                                             activated_at=not_empty(),
                                             terminated_at=None),
                allure_name='response has expected parameters')


@allure.feature('cats')
@allure.story('publisher_catalog_publish')
@pytest.mark.parametrize('catalog_code, title_code, error_code', [
    (generate_catalog_code(TitleCode.PREPARE_301), TitleCode.PREPARE_301,
     'Failed'),
    (generate_catalog_code(TitleCode.PREPARE_500), TitleCode.PREPARE_500,
     'failed_result_code'),
    (generate_catalog_code(TitleCode.PREPARE_504), TitleCode.PREPARE_504, 'TIMEOUT'),
    (generate_catalog_code(TitleCode.PREPARE_408), TitleCode.PREPARE_408, 'TIMEOUT'),
    (generate_catalog_code(TitleCode.PREPARE_400), TitleCode.PREPARE_400,
     'failed_result_code'),
    (generate_catalog_code(TitleCode.PREPARE_TIMEOUT), TitleCode.PREPARE_TIMEOUT,
     'TIMEOUT'),
])
def test_publisher_catalog_publish_when_critical_service_is_not_ready(is_http, is_db, catalog_url, publish_id,
                                                                      catalog_code, title_code, error_code):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: np_cats_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    """
    # publish catalog
    response = is_http.cats.publisher_catalog_publish(catalog_url, "catool", catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # waiting FAILED or COMPLETED status
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.FAILED)

    failure = is_db.get_task_failure(publish_id)
    assert_that(failure, contains_string('prodo:{}'.format(error_code)),
                allure_name='Should contain response error code')

    # check catalog publish status
    publish_status = is_http.cats.get_catalog_publish_status(publish_id)
    assert_that(publish_status, has_status_code(codes.ok), allure_name='response has expected code')

    catalog_publish_info = publish_status.json()[0]
    assert_that(catalog_publish_info, has_valid_catalog_publish_info(status=CatalogStatus.FAILED,
                                                                     publish_id=publish_id,
                                                                     catalog_code=catalog_code),
                allure_name='catalog_publish_status response is correct')


@allure.feature('cats')
@allure.story('publisher_catalog_publish')
def test_publisher_catalog_publish_truncated_error_message(is_http, is_db, catalog_url, mock_steps, publish_id):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: np_cats_qa.steps.db.steps.CatalogServiceDBSteps
    :type mock_steps: np_cats_qa.steps.mock.steps.CatalogServiceMockSteps
    :type catalog_url: str
    """
    title_code = TitleCode.PUBLISH_NEGATIVE
    catalog_code = generate_catalog_code(title_code)
    response_body = {
        'success': False,
        'error': {
            'code': 'failed_code',
            'message': ['1' * 21844 + 'removed']
        }
    }

    mock_steps.setup_prepare(catalog_code, response_body)
    # publish catalog
    response = is_http.cats.publisher_catalog_publish(catalog_url, "catool", catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # expected failed
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.FAILED)

    failure = is_db.get_task_failure(publish_id)
    assert_that(failure, is_not(contains_string('removed'.format())),
                allure_name='Should not contain extra symbols')


@allure.feature('cats')
@allure.story('publisher_catalog_publish')
def test_publisher_catalog_publish_big_cat_redirect_fail(is_http, is_db, wowp_title_catalog_code, publish_id,
                                                         mock_steps,
                                                         catalog_domain):
    mock_steps.journal_clear_history()

    # publish catalog
    response = is_http.cats.publisher_catalog_publish(catalog_domain + "/get_301.zip", "catool",
                                                      wowp_title_catalog_code,
                                                      publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # waiting FAILED status
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.FAILED)

    failure = is_db.get_task_failure(publish_id)
    assert_that(failure, contains_string('empty response'),
                allure_name='Should contain redirect error')
