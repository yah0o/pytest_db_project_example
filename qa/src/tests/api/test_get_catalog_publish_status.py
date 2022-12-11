import allure
import pytest
from hamcrest import equal_to
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import PublishStatus, CatalogStatus
from np_cats_qa.helpers import ulid
from np_cats_qa.verifications import verify_publish_completed_with_status_in_db, verify_publish_status_in_db, \
    has_valid_catalog_publish_info


@allure.feature('cats')
@allure.story('get_publish_status')
def test_get_publish_status_when_catalog_activated(is_http, is_db, catalog_url, catalog_code, publish_id):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: np_cats_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type title_code: str
    :type transaction_id: str
    """
    # publish catalog
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # wait for publish process completed
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    # get publish status
    publish_status = is_http.cats.get_catalog_publish_status(publish_id)
    assert_that(publish_status, has_status_code(codes.ok), allure_name='response has expected code')

    catalog_publish_info = publish_status.json()[0]
    assert_that(catalog_publish_info, has_valid_catalog_publish_info(status=CatalogStatus.ACTIVATED,
                                                                     publish_id=publish_id,
                                                                     catalog_code=catalog_code),
                allure_name='catalog_publish_status response is correct')

    # TODO Can fail in case for example: created_at = '2020-01-29T07:19:34.838Z', activated_at='2020-01-29T07:19:40Z', finished_at= '2020-01-29T07:19:40.001Z'
    # TODO revert < catalog_publish_info['activated_at']
    assert_that(catalog_publish_info['created_at'] < catalog_publish_info[
        'finished_at'], equal_to(True), allure_name='catalog processing time is correct')


@allure.feature('cats')
@allure.story('get_publish_status')
def test_get_publish_status_when_catalog_terminated(is_http, is_db, catalog_url, catalog_code, catalog_code_next,
                                                    publish_id):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: np_cats_qa.steps.db.steps.CatalogServiceDBSteps
    :type mock_steps: np_cats_qa.steps.mock.steps.CatalogServiceMockSteps
    :type catalog_url: str
    :type catalog_code: str
    :type catalog_code_next: str
    :type catalog_id: int
    """
    new_transaction_id = ulid()

    # publish catalog
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # wait for publish process completed
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    # publish catalog for the same title_id again
    response = is_http.cats.publish(catalog_url, catalog_code_next, new_transaction_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # wait for publish process completed
    verify_publish_completed_with_status_in_db(is_db, new_transaction_id, PublishStatus.COMPLETED)

    # get publish status
    publish_status = is_http.cats.get_catalog_publish_status(publish_id)
    assert_that(publish_status, has_status_code(codes.ok), allure_name='response has expected code')

    catalog_publish_info = publish_status.json()[0]
    assert_that(catalog_publish_info, has_valid_catalog_publish_info(status=CatalogStatus.TERMINATED,
                                                                     publish_id=publish_id,
                                                                     catalog_code=catalog_code),
                allure_name='catalog_publish_status response is correct')


@allure.feature('cats')
@allure.story('get_publish_status')
@pytest.mark.parametrize('catalog_status', [CatalogStatus.IN_PROGRESS, CatalogStatus.PENDING, CatalogStatus.FAILED])
def test_get_publish_status_when_catalog_publish_in_progress_pending_or_failed(is_http, is_db, catalog_code,
                                                                               catalog_status, publish_id,
                                                                               catalog_url):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: np_cats_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_code: str
    :type transaction_id: str
    :type catalog_id: int
    """
    # to exclude invalid domain caching
    domain = ulid()
    if catalog_status == CatalogStatus.FAILED:
        catalog_url = 'http://{}.ru/not_exist.zip'.format(domain)

    # publish catalog
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # wait for publish status
    verify_publish_status_in_db(is_db, publish_id, catalog_status)

    # get publish status
    publish_status = is_http.cats.get_catalog_publish_status(publish_id)
    assert_that(publish_status, has_status_code(codes.ok), allure_name='response has expected code')

    catalog_publish_info = publish_status.json()[0]
    assert_that(catalog_publish_info, has_valid_catalog_publish_info(status=catalog_status,
                                                                     publish_id=publish_id,
                                                                     catalog_code=catalog_code),
                allure_name='catalog_publish_status response is correct')
