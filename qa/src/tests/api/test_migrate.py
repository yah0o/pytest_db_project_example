import copy

import allure
import pytest
from hamcrest import contains_string, any_of
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import CatalogStatus, PublishStatus, TitleCode
from np_cats_qa.data_generators import generate_string_datetime, \
    generate_catalog_code, generate_catalog_code_next, generate_catalog_code_with_random_title_code
from np_cats_qa.matchers import not_empty
from np_cats_qa.verifications import verify_terminated_catalog_in_db, \
    verify_catools_notification_sent, verify_publish_completed_with_status_in_db


@allure.feature('cats')
@allure.story('migrate')
@pytest.mark.parametrize('migrate_twice', [True, False])
def test_migrate(is_http, is_db, catalog_url, migrate_twice):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type mock_steps: db_prj_qa.steps.mock.steps.CatalogServiceMockSteps
    :type catalog_url: str
    :type catalog_code: str
    """

    catalog_code = generate_catalog_code(TitleCode.CATALOG_MIGRATION)

    # migrate catalog
    if migrate_twice:
        is_http.cats.migrate(catalog_url, catalog_code, activated_at=generate_string_datetime(),
                             terminated_at=generate_string_datetime())
    response = is_http.cats.migrate(catalog_url, catalog_code, activated_at=generate_string_datetime(),
                                    terminated_at=generate_string_datetime())
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.content.decode('UTF-8'), any_of(contains_string('Migrated'),
                                                         contains_string('Already migrated')),
                allure_name='catalog migrated')
    assert_that(is_db.get_catalog_by_catalog_code(catalog_code), not_empty(), allure_name='exist in db')


@allure.feature('cats')
@allure.story('migrate')
def test_migrate_update_terminated_at(is_http, is_db, catalog_url):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type title_catalog_code: str
    """
    catalog_code = generate_catalog_code_next(TitleCode.CATALOG_MIGRATION)

    # migrate catalog
    is_http.cats.migrate(catalog_url, catalog_code, activated_at=generate_string_datetime(),
                         terminated_at=None)
    response = is_http.cats.migrate(catalog_url, catalog_code, activated_at=generate_string_datetime(),
                                    terminated_at=generate_string_datetime())
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.content.decode('UTF-8'), contains_string('Terminated date was set.'),
                allure_name='Terminated date was set')
    assert_that(is_db.get_catalog_by_catalog_code(catalog_code)['terminated_at'], not_empty(),
                allure_name='exist in db')


@allure.feature('cats')
@allure.story('migrate')
@pytest.mark.parametrize('catalog_url, catalog_code, activated_at, terminated_at',
                         [
                             # catalog url
                             ('not_valid_url', generate_catalog_code_with_random_title_code(),
                              '2020-03-04T11:15:09.333Z', '2020-03-04T11:15:09.333Z'),
                             pytest.param('http://google.com', generate_catalog_code_with_random_title_code(),
                                          '2020-03-04T11:15:09.333Z', '2020-03-04T11:15:09.333Z',
                                          marks=pytest.mark.skip("BUG FREYA-605")),
                             (123, generate_catalog_code_with_random_title_code(), '2020-03-04T11:15:09.333Z',
                              '2020-03-04T11:15:09.333Z'),
                             (None, generate_catalog_code_with_random_title_code(), '2020-03-04T11:15:09.333Z',
                              '2020-03-04T11:15:09.333Z'),
                             # catalog code
                             (pytest.lazy_fixture('main_catalog_url'), 'catalog_code', '2020-03-04T11:15:09.333Z',
                              '2020-03-04T11:15:09.333Z'),
                             (pytest.lazy_fixture('main_catalog_url'), 'ru.11-11-x', '2020-03-04T11:15:09.333Z',
                              '2020-03-04T11:15:09.333Z'),
                             (pytest.lazy_fixture('main_catalog_url'), 123, '2020-03-04T11:15:09.333Z',
                              '2020-03-04T11:15:09.333Z'),
                             (pytest.lazy_fixture('main_catalog_url'), None, '2020-03-04T11:15:09.333Z',
                              '2020-03-04T11:15:09.333Z'),
                             # activated_at
                             (pytest.lazy_fixture('main_catalog_url'), generate_catalog_code_with_random_title_code(),
                              '2020-03-04', '2020-03-04T11:15:09.333Z'),
                             (pytest.lazy_fixture('main_catalog_url'), generate_catalog_code_with_random_title_code(),
                              'not_datetime', '2020-03-04T11:15:09.333Z'),
                             (pytest.lazy_fixture('main_catalog_url'), generate_catalog_code_with_random_title_code(),
                              True, '2020-03-04T11:15:09.333Z'),
                             # terminated_at
                             (pytest.lazy_fixture('main_catalog_url'), generate_catalog_code_with_random_title_code(),
                              '2020-03-04T11:15:09.333Z', '2020-03-04'),
                             (pytest.lazy_fixture('main_catalog_url'), generate_catalog_code_with_random_title_code(),
                              '2020-03-04T11:15:09.333Z', 'not_datetime'),
                             (pytest.lazy_fixture('main_catalog_url'), generate_catalog_code_with_random_title_code(),
                              '2020-03-04T11:15:09.333Z', False),
                         ])
def test_migrate_negative(is_http, catalog_url, catalog_code, activated_at, terminated_at):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type mock_steps: db_prj_qa.steps.mock.steps.CatalogServiceMockSteps
    :type catalog_url: str
    :type catalog_code: str
    """
    # migrate catalog
    response = is_http.cats.migrate(catalog_url, catalog_code, activated_at=activated_at,
                                    terminated_at=terminated_at)
    assert_that(response, has_status_code(codes.bad), allure_name='response has expected code')


@allure.feature('cats')
@allure.story('migrate')
def test_publish_new_catalog_and_check_old_terminated(is_http, is_db, catalog_url, mock_steps, publish_id):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    """
    mock_steps.journal_clear_history()

    new_title_code = TitleCode.PUBLISH_NEW_CATALOG
    new_catalog_code = generate_catalog_code(title_code=new_title_code)

    # migrate catalog
    is_http.cats.migrate(catalog_url, new_catalog_code, activated_at=generate_string_datetime(),
                         terminated_at=None)

    old_catalog_id = copy.deepcopy(new_catalog_code)
    # call publish

    new_catalog_code = '-'.join(new_catalog_code.split('-')[:-1] + [str(int(new_catalog_code.split('-')[2]) + 1)])
    publish_response = is_http.cats.publish(catalog_url, new_catalog_code, publish_id)
    assert_that(publish_response, has_status_code(codes.created), allure_name='response has expected code')
    verify_terminated_catalog_in_db(is_db, old_catalog_id)
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)
    verify_catools_notification_sent(mock_steps, status=CatalogStatus.ACTIVATED, publish_id=publish_id,
                                     catalog_code=new_catalog_code)
