import allure
import pytest
from hamcrest import has_entries, equal_to
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import PublishStatus, PublishError, CatalogStatus, TitleCode
from np_cats_qa.data_generators import generate_catalog_code, generate_catalog_url
from np_cats_qa.helpers import random_id, ulid
from np_cats_qa.matchers import not_empty
from np_cats_qa.verifications import verify_failed_response, verify_catools_notification_sent, \
    verify_publish_completed_with_status_in_db, verify_prepare_method_called_n_times, \
    verify_publish_status_in_db, verify_publish_states_in_db, verify_prepare_method_called, \
    verify_activated_method_called, \
    has_valid_catalog_publish_info

new_catalog_id = random_id()


@allure.feature('cats')
@allure.story('publish')
def test_publish(is_http, is_db, catalog_url, title_code, catalog_code, publish_id, mock_steps):
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

    # publish catalog
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # verify catalog publication states
    verify_publish_states_in_db(is_db, publish_id)

    # verify notification about catalog status sent
    verify_catools_notification_sent(mock_steps, status=CatalogStatus.ACTIVATED, publish_id=publish_id,
                                     catalog_code=catalog_code)

    # verify 'prepare' and 'activated' methods_called
    verify_prepare_method_called(mock_steps, catalog_code=catalog_code)
    verify_activated_method_called(mock_steps, catalog_code=catalog_code)

    # get activate catalog
    response = is_http.cats.get_active_catalog_by_title_code(title_code, 'MAIN')
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.json(), has_entries(catalog_code=catalog_code,
                                             activated_at=not_empty(),
                                             terminated_at=None),
                allure_name='response has expected parameters')


@allure.feature('cats')
@allure.story('publish')
def test_publish_twice_with_the_same_catalog_and_publish_ids(is_http, is_db, catalog_url, title_code, catalog_code,
                                                             publish_id):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type title_code: str
    :type catalog_code: str
    :type publish_id: str
    """
    # publish catalog
    publish_response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(publish_response, has_status_code(codes.created), allure_name='response has expected code')

    # wait for catalog published
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    # get active catalog
    catalog_info_1 = is_http.cats.get_active_catalog_by_title_code(title_code, 'MAIN')
    assert_that(catalog_info_1, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(catalog_info_1.json(), has_entries(catalog_code=catalog_code,
                                                   activated_at=not_empty(),
                                                   terminated_at=None),
                allure_name='response has expected parameters')

    # call publish again
    publish_response_2 = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(publish_response_2, has_status_code(codes.created), allure_name='response has expected code')

    # get activate catalog after second publish
    catalog_info_2 = is_http.cats.get_active_catalog_by_title_code(title_code, 'MAIN')
    assert_that(catalog_info_2, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(catalog_info_2.json(), has_entries(catalog_code=catalog_code,
                                                   activated_at=not_empty(),
                                                   terminated_at=None),
                allure_name='response has expected parameters')

    # verify active catalog info wasn't changed
    assert_that(catalog_info_1.content, equal_to(catalog_info_2.content),
                allure_name='catalog info was not changed after second publish request')


@allure.feature('cats')
@allure.story('publish')
def test_publish_twice_when_catalog_and_publish_id_do_not_match(is_http, is_db, catalog_url, catalog_code,
                                                                catalog_code_next, publish_id):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type catalog_code: str
    :type catalog_code_next: str
    :type publish_id: str
    """
    # publish catalog
    publish_response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(publish_response, has_status_code(codes.created), allure_name='response has expected code')

    # wait for catalog published
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    # call publish again
    publish_response_2 = is_http.cats.publish(catalog_url, catalog_code_next, publish_id)
    assert_that(publish_response_2, has_status_code(codes.bad), allure_name='response has expected code')

    # verify error
    verify_failed_response(publish_response_2, PublishError.CLIENT_ERROR)


@allure.feature('cats')
@allure.story('publish')
def test_publish_new_catalog_and_check_old_terminated(is_http, is_db, catalog_url, title_code, mock_steps, catalog_code,
                                                      catalog_code_next, publish_id):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type title_code: str
    :type catalog_code: str
    :type catalog_code_next: str
    :type publish_id: str
    """
    mock_steps.journal_clear_history()

    # publish first catalog
    publish_response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(publish_response, has_status_code(codes.created), allure_name='response has expected code')

    # wait for catalog published
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)
    verify_catools_notification_sent(mock_steps, status=CatalogStatus.ACTIVATED, publish_id=publish_id,
                                     catalog_code=catalog_code)
    mock_steps.journal_clear_history()

    new_publish_id = ulid()
    # publish second catalog
    publish_response_2 = is_http.cats.publish(catalog_url, catalog_code_next, new_publish_id)
    assert_that(publish_response_2, has_status_code(codes.created), allure_name='response has expected code')

    # wait for catalog published
    verify_publish_completed_with_status_in_db(is_db, new_publish_id, PublishStatus.COMPLETED)

    # verify catalogs activation and termination time
    catalog_1_time = is_db.get_task_processing_time(publish_id)
    catalog_2_time = is_db.get_task_processing_time(new_publish_id)
    assert_that(catalog_1_time['terminated_at'], equal_to(catalog_2_time['activated_at']),
                allure_name='catalog1 terminated when catalog2 activated')

    # get activate catalog
    response = is_http.cats.get_active_catalog_by_title_code(title_code, 'MAIN')
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.json(), has_entries(catalog_code=catalog_code_next,
                                             activated_at=not_empty(),
                                             terminated_at=None),
                allure_name='response has expected parameters')

    # verify notification about catalog status sent
    verify_catools_notification_sent(mock_steps, status=CatalogStatus.ACTIVATED, publish_id=new_publish_id,
                                     catalog_code=catalog_code_next)
    verify_catools_notification_sent(mock_steps, status=CatalogStatus.TERMINATED, publish_id=publish_id,
                                     catalog_code=catalog_code)


@allure.feature('cats')
@allure.story('publish')
def test_publish_catalog_after_failed_status(is_http, is_db, mock_steps, catalog_url, title_code, catalog_code,
                                             publish_id):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type catalog_code: str
    :type publish_id: str
    """
    # to exclude invalid domain caching
    domain = ulid()
    # call publish to get FAILED status
    invalid_catalog_url = 'http://{}.ru/not_exist.zip'.format(domain)
    response_publish1 = is_http.cats.publish(invalid_catalog_url, catalog_code, publish_id)
    assert_that(response_publish1, has_status_code(codes.created), allure_name='response has expected code')

    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.FAILED)
    verify_catools_notification_sent(mock_steps, status=CatalogStatus.FAILED, publish_id=publish_id,
                                     catalog_code=catalog_code)

    new_publish_id = ulid()
    # call publish with correct parameters
    response_publish2 = is_http.cats.publish(catalog_url, catalog_code, new_publish_id)
    assert_that(response_publish2, has_status_code(codes.created), allure_name='response has expected code')

    verify_publish_completed_with_status_in_db(is_db, new_publish_id, PublishStatus.COMPLETED)

    # get activate catalog
    response = is_http.cats.get_active_catalog_by_title_code(title_code, 'MAIN')
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.json(), has_entries(catalog_code=catalog_code,
                                             activated_at=not_empty(),
                                             terminated_at=None),
                allure_name='response has expected parameters')


@allure.feature('cats')
@allure.story('publish_order')
def test_publish_several_catalogs_for_one_title(is_http, is_db, catalog_url):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type mock_steps: db_prj_qa.steps.mock.steps.CatalogServiceMockSteps
    :type catalog_url: str
    """
    # prepare
    title_code = TitleCode.PUBLISH_ORDER

    catalog_code_1 = generate_catalog_code(title_code)
    publish_id_1 = ulid()

    catalog_code_2 = generate_catalog_code(title_code)
    publish_id_2 = ulid()

    catalog_code_3 = generate_catalog_code(title_code)
    publish_id_3 = ulid()

    # call publish for three catalogs and one title
    response_publish1 = is_http.cats.publish(catalog_url, catalog_code_1, publish_id_1)
    assert_that(response_publish1, has_status_code(codes.created), allure_name='response has expected code')

    response_publish2 = is_http.cats.publish(catalog_url, catalog_code_2, publish_id_2)
    assert_that(response_publish2, has_status_code(codes.created), allure_name='response has expected code')

    response_publish3 = is_http.cats.publish(catalog_url, catalog_code_3, publish_id_3)
    assert_that(response_publish3, has_status_code(codes.created), allure_name='response has expected code')

    # verify catalog_1 only has status is IN_PROGRESS
    verify_publish_status_in_db(is_db, publish_id_1, PublishStatus.IN_PROGRESS)
    catalog2_status = is_db.get_publish_task_status(publish_id_2)
    catalog3_status = is_db.get_publish_task_status(publish_id_3)
    assert_that(catalog2_status and catalog3_status, equal_to(PublishStatus.PENDING),
                allure_name='catalog2 and catalog3 status should be PENDING, catalog1 only should be IN_PROGRESS')

    # wait for all catalogs processed
    verify_publish_completed_with_status_in_db(is_db, publish_id_3, PublishStatus.COMPLETED)

    # verify processing time
    catalog_1_time = is_db.get_task_processing_time(publish_id_1)
    catalog_2_time = is_db.get_task_processing_time(publish_id_2)
    catalog_3_time = is_db.get_task_processing_time(publish_id_3)

    # verify tasks processing order
    assert_that(
        catalog_1_time['started_at'] < catalog_1_time['finished_at'] < catalog_2_time['started_at'] < catalog_2_time[
            'finished_at'] < catalog_3_time['started_at'],
        equal_to(True), allure_name='catalogs processing order is correct')

    # verify catalogs activation and termination order
    assert_that(catalog_1_time['terminated_at'], equal_to(catalog_2_time['activated_at']),
                allure_name='catalog1 terminated when catalog2 activated')

    # get active catalog for title
    response = is_http.cats.get_active_catalog_by_title_code(title_code, 'MAIN')
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.json(), has_entries(catalog_code=catalog_code_3,
                                             activated_at=not_empty(),
                                             terminated_at=None),
                allure_name='response has expected parameters')


@allure.feature('cats')
@allure.story('publish')
@pytest.mark.parametrize('title_code', [
    TitleCode.PREPARE_500,
    TitleCode.PREPARE_504,
    TitleCode.PREPARE_408,
    TitleCode.PREPARE_400,
    TitleCode.PREPARE_TIMEOUT
])
def test_publish_when_critical_service_is_not_ready(is_http, is_db, catalog_url, publish_id, title_code):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type mock_steps: db_prj_qa.steps.mock.steps.CatalogServiceMockSteps
    :type catalog_url: str
    """

    catalog_code = generate_catalog_code(title_code)
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # verify catalog publication state in DB
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.FAILED)

    # check catalog publish status
    publish_status = is_http.cats.get_catalog_publish_status(publish_id)
    assert_that(publish_status, has_status_code(codes.ok), allure_name='response has expected code')

    catalog_publish_info = publish_status.json()[0]
    assert_that(catalog_publish_info, has_valid_catalog_publish_info(status=CatalogStatus.FAILED,
                                                                     publish_id=publish_id,
                                                                     catalog_code=catalog_code),
                allure_name='catalog_publish_status response is correct')


@allure.feature('cats')
@allure.story('publish')
@pytest.mark.parametrize('title_code', [
    TitleCode.PREPARE_TIMEOUT,
])
def test_3_retry_on_prepare_timeout(is_http, is_db, catalog_url, mock_steps, publish_id,
                                    title_code):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type mock_steps: db_prj_qa.steps.mock.steps.CatalogServiceMockSteps
    :type catalog_url: str
    """
    mock_steps.journal_clear_history()

    catalog_code = generate_catalog_code(title_code)
    # publish catalog
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # verify catalog publication state in DB
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.FAILED)

    # check catalog publish status
    publish_status = is_http.cats.get_catalog_publish_status(publish_id)
    assert_that(publish_status, has_status_code(codes.ok), allure_name='response has expected code')

    catalog_publish_info = publish_status.json()[0]
    assert_that(catalog_publish_info, has_valid_catalog_publish_info(status=CatalogStatus.FAILED,
                                                                     publish_id=publish_id,
                                                                     catalog_code=catalog_code),
                allure_name='catalog_publish_status response is correct')
    # first time + 3 retries= 4 calls
    verify_prepare_method_called_n_times(mock_steps, catalog_code, 4)


@allure.feature('cats')
@allure.story('publish')
@pytest.mark.parametrize('title_code', [
    TitleCode.ACTIVATED_500,
    TitleCode.ACTIVATED_408,
    TitleCode.ACTIVATED_400
])
def test_publish_when_other_services_not_ready(is_http, is_db, catalog_url, publish_id, title_code):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    """

    catalog_code = generate_catalog_code(title_code)

    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # verify catalog publication state in DB
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    # check catalog publish status
    publish_status = is_http.cats.get_catalog_publish_status(publish_id)
    assert_that(publish_status, has_status_code(codes.ok), allure_name='response has expected code')

    catalog_publish_info = publish_status.json()[0]
    assert_that(catalog_publish_info, has_valid_catalog_publish_info(status=CatalogStatus.ACTIVATED,
                                                                     publish_id=publish_id,
                                                                     catalog_code=catalog_code),
                allure_name='catalog_publish_status response is correct')

    # get active catalog
    response = is_http.cats.get_active_catalog_by_title_code(title_code, 'MAIN')
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.json(), has_entries(catalog_code=catalog_code,
                                             activated_at=not_empty()),
                allure_name='response has expected parameters')


@allure.feature('cats')
@allure.story('publish')
def test_publish_when_entity_was_changed_but_same_id(is_http, is_db, catalog_code, publish_id,
                                                     mock_steps,
                                                     yaml_config):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type mock_steps: db_prj_qa.steps.mock.steps.CatalogServiceMockSteps
    :type catalog_code: str
    :type publish_id: str
    """

    catalog_url = generate_catalog_url(yaml_config, 'catalog_invalid_entities.zip')
    mock_steps.journal_clear_history()

    # publish catalog
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # verify catalog publication states
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.FAILED)

    verify_catools_notification_sent(mock_steps,
                                     status=CatalogStatus.FAILED,
                                     publish_id=publish_id,
                                     catalog_code=catalog_code,
                                     reason='Entity with id \'43f3c84e-31b4-49cd-81fa-d04a0ded461d\' has updated '
                                            'field values \'{visible=false, new_field={}, '
                                            'prerequisites=null}\'.')


@allure.feature('cats')
@allure.story('publish')
def test_publish_with_the_same_code_but_different_content(is_http, is_db, catalog_code, publish_id, mock_steps,
                                                          yaml_config):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type mock_steps: db_prj_qa.steps.mock.steps.CatalogServiceMockSteps
    :type catalog_code: str
    :type publish_id: str
    """

    mock_steps.journal_clear_history()

    catalog_url = generate_catalog_url(yaml_config, 'catalog_with_the_same_code_first.zip')
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    # make sure that the first catalog is used for verification, and not the previous one
    for i in range(2):
        new_publish_id = ulid()
        catalog_url = generate_catalog_url(yaml_config, 'catalog_with_the_same_code_second_invalid.zip')
        response = is_http.cats.publish(catalog_url, catalog_code, new_publish_id)
        assert_that(response, has_status_code(codes.created), allure_name='response has expected code')
        verify_publish_completed_with_status_in_db(is_db, new_publish_id, PublishStatus.FAILED)

        verify_catools_notification_sent(mock_steps,
                                         status=CatalogStatus.FAILED,
                                         publish_id=new_publish_id,
                                         catalog_code=catalog_code,
                                         reason='Entity with id \'96c23858-3af7-11ec-8d3d-0242ac130003\' '
                                                'wasn\'t present in previous catalog with the same code.')


@allure.feature('cats')
@allure.story('publish v2')
def test_publish_v2(is_http, is_db, catalog_url, title_code, catalog_code, publish_id):
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    new_publish_id = ulid()
    publish_response_v2 = is_http.cats.v2_catalog_publish(
        catalog_url=catalog_url,
        title_code=title_code,
        tool_name='catool',
        catalog_type='MAIN',
        publish_id=new_publish_id
    )
    assert_that(publish_response_v2, has_status_code(codes.created), allure_name='response has expected code')
    verify_publish_completed_with_status_in_db(is_db, new_publish_id, PublishStatus.COMPLETED)

    publish_status = is_http.cats.get_catalog_publish_status(new_publish_id)
    assert_that(publish_status, has_status_code(codes.ok), allure_name='response has expected code')

    catalog_publish_info = publish_status.json()[0]
    pub_version = str(int(catalog_code.split("-")[-1]) + 1)
    assert_that(catalog_publish_info, has_valid_catalog_publish_info(status=CatalogStatus.ACTIVATED,
                                                                     publish_id=new_publish_id,
                                                                     catalog_code=title_code + '-MAIN-' + pub_version),
                allure_name='response has expected catalog_code')


@allure.feature('cats')
@allure.story('publish v2')
def test_v2_publish_version_for_new_title(is_http, is_db, catalog_url, wows_title_code, publish_id):
    publish_response_v2 = is_http.cats.v2_catalog_publish(
        catalog_url=catalog_url,
        title_code=wows_title_code,
        tool_name='catool',
        catalog_type='MAIN',
        publish_id=publish_id
    )
    assert_that(publish_response_v2, has_status_code(codes.created), allure_name='response has expected code')
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    publish_status = is_http.cats.get_catalog_publish_status(publish_id)
    assert_that(publish_status, has_status_code(codes.ok), allure_name='response has expected code')

    catalog_publish_info = publish_status.json()[0]
    assert_that(catalog_publish_info, has_valid_catalog_publish_info(status=CatalogStatus.ACTIVATED,
                                                                     publish_id=publish_id,
                                                                     catalog_code=wows_title_code + '-MAIN-' + '1'),
                allure_name='response has expected catalog_code')


@allure.feature('cats')
@allure.story('publish')
@pytest.mark.parametrize('title_code', [
    TitleCode.ACTIVATED_500,
    TitleCode.ACTIVATED_408,
    TitleCode.ACTIVATED_400
])
def test_publish_v2_when_other_services_not_ready(is_http, is_db, catalog_url, publish_id, title_code):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    """

    catalog_code = generate_catalog_code(title_code)

    publish_response_v2 = is_http.cats.v2_catalog_publish(
        catalog_url=catalog_url,
        title_code=catalog_code,
        tool_name='catool',
        catalog_type='MAIN',
        publish_id=publish_id
    )
    assert_that(publish_response_v2, has_status_code(codes.bad), allure_name='response has expected code')


@allure.feature('cats')
@allure.story('publish v2')
def test_v2_publish_catalog_after_failed_status(is_http, is_db, mock_steps, catalog_url, title_code, catalog_code,
                                                publish_id, catalog_code_next):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type catalog_code: str
    :type publish_id: str
    """
    # to exclude invalid domain caching
    domain = ulid()
    # call publish to get FAILED status
    invalid_catalog_url = 'http://{}.ru/not_exist.zip'.format(domain)
    response_publish1 = is_http.cats.publish(
        invalid_catalog_url,
        catalog_code,
        publish_id)
    assert_that(response_publish1, has_status_code(codes.created), allure_name='response has expected code')

    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.FAILED)
    verify_catools_notification_sent(mock_steps, status=CatalogStatus.FAILED, publish_id=publish_id,
                                     catalog_code=catalog_code)

    new_publish_id = ulid()
    response_v2 = is_http.cats.v2_catalog_publish(
        catalog_url=catalog_url,
        title_code=title_code,
        tool_name='catool',
        catalog_type='MAIN',
        publish_id=new_publish_id
    )
    assert_that(response_v2, has_status_code(codes.created), allure_name='response has expected code')
    verify_publish_completed_with_status_in_db(is_db, new_publish_id, PublishStatus.COMPLETED)

    # get activate catalog
    response = is_http.cats.get_active_catalog_by_title_code(title_code, 'MAIN')
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')


@allure.feature('cats')
@allure.story('publish v2')
def test_publish_v2_twice(is_http, is_db, catalog_url, title_code, mock_steps,
                          publish_id):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type title_code: str
    :type catalog_code: str
    :type catalog_code_next: str
    :type publish_id: str
    """
    mock_steps.journal_clear_history()

    # publish first catalog
    publish_response_v2 = is_http.cats.v2_catalog_publish(
        catalog_url=catalog_url,
        title_code=title_code,
        tool_name='catool',
        catalog_type='MAIN',
        publish_id=publish_id
    )
    assert_that(publish_response_v2, has_status_code(codes.created), allure_name='response has expected code')

    # wait for catalog published
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    # get active catalog
    catalog_info_1 = is_http.cats.get_active_catalog_by_title_code(title_code, 'MAIN')

    # call publish again
    publish_response_v2_2 = is_http.cats.v2_catalog_publish(
        catalog_url=catalog_url,
        title_code=title_code,
        tool_name='catool',
        catalog_type='MAIN',
        publish_id=publish_id
    )
    assert_that(publish_response_v2_2, has_status_code(codes.created), allure_name='response has expected code')
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    # get activate catalog after second publish
    catalog_info_2 = is_http.cats.get_active_catalog_by_title_code(title_code, 'MAIN')
    assert_that(catalog_info_2, has_status_code(codes.ok), allure_name='response has expected code')

    # verify active catalog info wasn't changed
    assert_that(catalog_info_1.content, equal_to(catalog_info_2.content),
                allure_name='catalog info was not changed after second publish request')


@allure.feature('cats')
@allure.story('publish v2')
def test_publish_v2_with_same_publish_id(is_http, is_db, catalog_url, title_code, publish_id):
    publish_response_v2 = is_http.cats.v2_catalog_publish(
        catalog_url=catalog_url,
        title_code=title_code,
        tool_name='catool',
        catalog_type='MAIN',
        publish_id=publish_id
    )
    assert_that(publish_response_v2, has_status_code(codes.created), allure_name='response has expected code')

    publish_response_v2_2 = is_http.cats.v2_catalog_publish(
        catalog_url=catalog_url,
        title_code=title_code,
        tool_name='catool',
        catalog_type='MAIN',
        publish_id=publish_id
    )
    assert_that(publish_response_v2_2, has_status_code(codes.created), allure_name='response has expected code')
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)


@allure.feature('cats')
@allure.story('publish v2')
@pytest.mark.parametrize('catalog_url', (None, '', 123, .5))
def test_publish_v2_invalid_catalog_url(is_http, is_db, catalog_url, title_code, mock_steps,
                                        publish_id):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type title_code: str
    :type catalog_code: str
    :type catalog_code_next: str
    :type publish_id: str
    """
    mock_steps.journal_clear_history()

    publish_response_v2 = is_http.cats.v2_catalog_publish(
        catalog_url=catalog_url,
        title_code=title_code,
        tool_name='catool',
        catalog_type='MAIN',
        publish_id=publish_id
    )
    assert_that(publish_response_v2, has_status_code(codes.bad), allure_name='response has expected code')


@allure.feature('cats')
@allure.story('publish v2')
@pytest.mark.parametrize('title_code', [
    TitleCode.PREPARE_500,
    TitleCode.PREPARE_504,
    TitleCode.PREPARE_408,
    TitleCode.PREPARE_400,
    TitleCode.PREPARE_TIMEOUT
])
def test_publish_v2_when_critical_service_is_not_ready(is_http, is_db, catalog_url, publish_id, title_code):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type mock_steps: db_prj_qa.steps.mock.steps.CatalogServiceMockSteps
    :type catalog_url: str
    """

    publish_response_v2 = is_http.cats.v2_catalog_publish(
        catalog_url=catalog_url,
        title_code=title_code,
        tool_name='catool',
        catalog_type='MAIN',
        publish_id=publish_id
    )
    assert_that(publish_response_v2, has_status_code(codes.created), allure_name='response has expected code')

    # verify catalog publication state in DB
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.FAILED)

    # check catalog publish status
    publish_status = is_http.cats.get_catalog_publish_status(publish_id)
    assert_that(publish_status, has_status_code(codes.ok), allure_name='response has expected code')

    catalog_publish_info = publish_status.json()[0]
    assert_that(catalog_publish_info, has_valid_catalog_publish_info(status=CatalogStatus.FAILED,
                                                                     publish_id=publish_id,
                                                                     catalog_code=not_empty()),
                allure_name='catalog_publish_status response is correct')


@allure.feature('cats')
@allure.story('republish')
def test_v2_republish(is_http, is_db, catalog_url, catalog_code, publish_id):
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    new_publish_id = ulid()
    republish_response = is_http.cats.v2_catalog_republish(
        tool_name='catool',
        catalog_code=catalog_code,
        publish_id=new_publish_id
    )
    assert_that(republish_response, has_status_code(codes.created), allure_name='response has expected code')
    verify_publish_completed_with_status_in_db(is_db, new_publish_id, PublishStatus.COMPLETED)

    publish_status = is_http.cats.get_catalog_publish_status(new_publish_id)
    assert_that(publish_status, has_status_code(codes.ok), allure_name='response has expected code')


@allure.feature('cats')
@allure.story('republish')
def test_v2_republish_wo_tool_name(is_http, is_db, catalog_url, catalog_code, publish_id):
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    new_publish_id = ulid()
    republish_response = is_http.cats.v2_catalog_republish(
        catalog_code=catalog_code,
        publish_id=new_publish_id
    )
    assert_that(republish_response, has_status_code(codes.bad), allure_name='response has expected code')


@allure.feature('cats')
@allure.story('republish')
def test_v2_republish_when_catalog_and_publish_id_do_not_match(is_http, is_db, catalog_url, catalog_code, publish_id,
                                                               catalog_code_next):
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    new_publish_id = ulid()
    republish_response = is_http.cats.v2_catalog_republish(
        tool_name='catool',
        catalog_code=catalog_code_next,
        publish_id=new_publish_id
    )
    assert_that(republish_response, has_status_code(codes.not_found), allure_name='response has expected code')


@allure.feature('cats')
@allure.story('republish')
def test_v2_republish_with_same_publish_id(is_http, is_db, catalog_url, catalog_code, publish_id):
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    republish_response = is_http.cats.v2_catalog_republish(
        tool_name='catool',
        catalog_code=catalog_code,
        publish_id=publish_id
    )
    assert_that(republish_response, has_status_code(codes.created), allure_name='response has expected code')
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

@allure.feature('cats')
@allure.story('republish')
@pytest.mark.parametrize('invalid_publish_id', (None, '', 'abc', 123))
def test_v2_republish_invalid_publish_id(is_http, is_db, catalog_url, catalog_code, publish_id, invalid_publish_id):
    republish_response = is_http.cats.v2_catalog_republish(
        tool_name='catool',
        catalog_code=catalog_code,
        publish_id=invalid_publish_id
    )
    assert_that(republish_response, has_status_code(codes.bad), allure_name='response has expected code')


@allure.feature('cats')
@allure.story('republish')
@pytest.mark.parametrize('invalid_catalog_code', (None, '', 'abc', 123))
def test_v2_republish_with_bad_catalog_code(is_http, is_db, catalog_url, catalog_code, publish_id,
                                            invalid_catalog_code):
    republish_response = is_http.cats.v2_catalog_republish(
        tool_name='catool',
        catalog_code=invalid_catalog_code,
        publish_id=publish_id
    )
    assert_that(republish_response, has_status_code(codes.bad), allure_name='response has expected code')
