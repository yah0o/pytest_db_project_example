import allure
import pytest

from hamcrest import has_key, equal_to
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import PublishStatus, TestCatalogPath, CatalogError, CatalogZIP
from np_cats_qa.data_generators import generate_catalog_url, generate_catalog_code
from np_cats_qa.helpers import ulid
from np_cats_qa.verifications import verify_publish_completed_with_status_in_db, \
    compare_downloaded_and_original_catalogs, \
    verify_failed_response


@allure.feature('cats')
@allure.story('get_catalog_by_code')
def test_get_catalog_by_code(is_http, is_db, mock_http, clear_tmp, catalog_url, title_code, catalog_code, publish_id):
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

    # get catalog by catalog_code
    get_catalog = is_http.cats.get_catalog_by_code(catalog_code)
    assert_that(get_catalog, has_status_code(codes.OK), allure_name='response has expected code')

    # verify response headers
    assert_that(get_catalog.headers, has_key('Content-Disposition'))
    assert_that(get_catalog.headers['Content-Disposition'],
                equal_to('attachment; filename="{}"'.format(catalog_code + '.zip')))

    # compare original catalog and catalog in response
    compare_downloaded_and_original_catalogs(mock_http, get_catalog.content, CatalogZIP.DEFAULT_CATALOG,
                                             TestCatalogPath.DOWNLOAD_PATH, TestCatalogPath.ORIGINAL_PATH)


@allure.feature('cats')
@allure.story('get_catalog_by_code')
def test_get_catalog_by_code_when_catalog_updated(is_http, is_db, catalog_url, catalog_code, publish_id, mock_http,
                                                  yaml_config):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type catalog_code: str
    :type publish_id: str
    """
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # wait for catalog published
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    # publish catalog for the same title with different zip
    new_publish_id = ulid()
    new_catalog_code = generate_catalog_code(yaml_config.data.TITLE_CODE)
    new_catalog_url = generate_catalog_url(yaml_config, CatalogZIP.UPDATED_CATALOG)
    response = is_http.cats.publish(new_catalog_url, new_catalog_code, new_publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # wait for catalog published
    verify_publish_completed_with_status_in_db(is_db, new_publish_id, PublishStatus.COMPLETED)

    # get catalog by catalog_code
    get_catalog = is_http.cats.get_catalog_by_code(new_catalog_code)
    assert_that(get_catalog, has_status_code(codes.OK), allure_name='response has expected code')

    # compare original catalog and catalog in response
    compare_downloaded_and_original_catalogs(mock_http, get_catalog.content, CatalogZIP.UPDATED_CATALOG,
                                             TestCatalogPath.DOWNLOAD_PATH, TestCatalogPath.ORIGINAL_PATH)


@allure.feature('cats')
@allure.story('get_catalog_by_code')
def test_get_catalog_by_code_when_not_found(is_http, catalog_code):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type catalog_code: str
    """

    # get catalog by catalog_code
    response = is_http.cats.get_catalog_by_code(catalog_code)

    # verify response
    assert_that(response, has_status_code(codes.bad_request), allure_name='response has expected code')
    verify_failed_response(response, CatalogError.CATALOG_NOT_FOUND)


@allure.feature('cats')
@allure.story('get_catalog_by_code')
def test_get_catalog_by_code_when_publish_failed(is_http, yaml_config, catalog_code, publish_id, is_db, mock_steps):
    """
     :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type mock_steps: db_prj_qa.steps.mock.steps.CatalogServiceMockSteps
    :type catalog_code: str
    :type publish_id: ulid
    """
    # publish catalog with invalid zip
    url = generate_catalog_url(yaml_config, CatalogZIP.INVALID_FORMAT)
    response = is_http.cats.publish(url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')

    # wait publish failed
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.FAILED)

    # get catalog by catalog_code
    get_catalog_response = is_http.cats.get_catalog_by_code(catalog_code)

    # verify response
    assert_that(get_catalog_response, has_status_code(codes.bad_request), allure_name='response has expected code')
    verify_failed_response(get_catalog_response, CatalogError.CATALOG_NOT_FOUND)
