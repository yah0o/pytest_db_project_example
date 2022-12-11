import allure
import pytest
from hamcrest import equal_to, less_than_or_equal_to
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import PublishStatus, CatalogStatus, PublishError, TitleCode
from np_cats_qa.data_generators import generate_catalog_code
from np_cats_qa.helpers import ulid
from np_cats_qa.verifications import verify_publish_completed_with_status_in_db, has_valid_catalog_publications_info, \
    verify_publish_status_in_db, verify_failed_response


@allure.feature('cats')
@allure.story('get_catalog_publications')
def test_get_catalog_publications_activated(is_http, is_db, catalog_url, title_code, catalog_code,
                                            publish_id):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type catalog_code: str
    :type title_code: str
    :type publish_id: ulid
    """
    # publish catalog
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # wait for catalog published
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    # get catalog publications by title_code
    get_catalog_publications = is_http.cats.get_catalog_publications(title_code)
    assert_that(get_catalog_publications, has_status_code(codes.OK), allure_name='response has expected code')

    catalog_publications_info = get_catalog_publications.json()[0]

    assert_that(catalog_publications_info, has_valid_catalog_publications_info(status=CatalogStatus.ACTIVATED,
                                                                               publish_id=publish_id,
                                                                               catalog_code=catalog_code),
                allure_name='catalog_publish_status response is correct')
    assert_that(catalog_publications_info['created_at'] < catalog_publications_info[
        'finished_at'], equal_to(True), allure_name='catalog_publications_status response is correct')


@allure.feature('cats')
@allure.story('get_catalog_publications')
def test_get_catalog_publications_terminated(is_http, is_db, catalog_url, title_code, catalog_code,
                                             publish_id, catalog_code_next):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type catalog_code: str
    :type title_code: str
    :type publish_id: ulid
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

    # get catalog publications by title_code
    get_catalog_publications = is_http.cats.get_catalog_publications(title_code)
    assert_that(get_catalog_publications, has_status_code(codes.OK), allure_name='response has expected code')

    # get catalog publications that published in terminated state
    catalog_publications_terminated = [catalog for catalog in get_catalog_publications.json()
                                       if catalog['publish_id'] == publish_id]
    catalog_publications_info = catalog_publications_terminated[0]

    assert_that(catalog_publications_info, has_valid_catalog_publications_info(status=CatalogStatus.TERMINATED,
                                                                               publish_id=publish_id,
                                                                               catalog_code=catalog_code),
                allure_name='catalog_publications_status response is correct')


@allure.feature('cats')
@allure.story('get_catalog_publications')
@pytest.mark.parametrize('catalog_status', [CatalogStatus.IN_PROGRESS, CatalogStatus.PENDING, CatalogStatus.FAILED])
def test_get_catalog_publications_other_statuses(is_http, is_db, catalog_code, catalog_status,
                                                 publish_id, catalog_url, title_code):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type catalog_code: str
    :type title_code: str
    :type publish_id: ulid
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

    # get catalog publications by title_code
    get_catalog_publications = is_http.cats.get_catalog_publications(title_code)
    assert_that(get_catalog_publications, has_status_code(codes.OK), allure_name='response has expected code')

    # get catalog publications that published in terminated state
    catalog_publications_terminated = [catalog for catalog in get_catalog_publications.json()
                                       if catalog['publish_id'] == publish_id]
    catalog_publications_info = catalog_publications_terminated[0]

    assert_that(catalog_publications_info, has_valid_catalog_publications_info(status=catalog_status,
                                                                               publish_id=publish_id,
                                                                               catalog_code=catalog_code),
                allure_name='catalog_publications_status response is correct')


@allure.feature('cats')
@allure.story('get_catalog_publications_validation')
@pytest.mark.parametrize('limit, total_limit', [(None, 50),
                                                (1, 1),
                                                (5, 5),
                                                (0, 0)])
def test_get_catalog_publications_with_limit(is_http, title_code, limit, total_limit):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    """
    # default value for limit is 50 [When None]
    # get catalog publications by title_code
    get_catalog_publications = is_http.cats.get_catalog_publications(title_code, limit=limit)
    count = len(get_catalog_publications.json())
    if limit == None:
        # First run of all tests get <50 publications
        assert_that(count, less_than_or_equal_to(total_limit),
                    allure_name='catalog_publications response limit is correct')
    else:
        assert_that(count, equal_to(total_limit), allure_name='catalog_publications response limit is correct')


@allure.feature('cats')
@allure.story('get_catalog_publications_validation')
def test_get_catalog_publications_with_missed_title_code(is_http):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    """
    # default value for limit is 50 [When None]
    # get catalog publications by title_code
    get_catalog_publications = is_http.cats.get_catalog_publications('ru.not_existing')
    assert_that(get_catalog_publications, has_status_code(codes.bad_request), allure_name='response has expected code')
    verify_failed_response(get_catalog_publications, equal_to(PublishError.TITLE_NOT_FOUND))


@allure.feature('cats')
@allure.story('get_catalog_publications_validation')
@pytest.mark.parametrize('limit, error, status_codes', [(-1, PublishError.SERVER_ERROR, codes.server_error),
                                                        (.5, PublishError.CLIENT_ERROR, codes.bad_request),
                                                        ('test', PublishError.CLIENT_ERROR, codes.bad_request)])
def test_get_catalog_publications_with_invalid_limit(is_http, title_code, limit, error, status_codes):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    """
    # default value for limit is 50 [When None]
    # get catalog publications by title_code
    get_catalog_publications = is_http.cats.get_catalog_publications(title_code, limit=limit)
    assert_that(get_catalog_publications, has_status_code(status_codes), allure_name='response has expected code')
    verify_failed_response(get_catalog_publications, error)


@allure.feature('cats')
@allure.story('get_catalog_publications_validation')
@pytest.mark.parametrize('title_code, error, status_codes',
                         [
                             ('', PublishError.CLIENT_ERROR, codes.not_found),
                             ([], PublishError.TITLE_NOT_FOUND, codes.bad_request),
                             ({}, PublishError.TITLE_NOT_FOUND, codes.bad_request),
                         ])
def test_get_catalog_publications_by_invalid_title_code(is_http, title_code, error, status_codes):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    """
    # get catalog publications by title_code
    get_catalog_publications = is_http.cats.get_catalog_publications(title_code)

    assert_that(get_catalog_publications, has_status_code(status_codes), allure_name='response has expected code')
    verify_failed_response(get_catalog_publications, error)
