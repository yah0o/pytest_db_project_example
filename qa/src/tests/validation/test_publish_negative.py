import allure
import pytest
from np_cats_qa.constants import PublishStatus, PublishError, TitleCode
from np_cats_qa.data_generators import generate_catalog_code, generate_catalog_url
from np_cats_qa.verifications import verify_failed_response, verify_publish_completed_with_status_in_db
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes


@allure.feature('cats')
@allure.story('publish_validation')
@pytest.mark.parametrize('url, status_code, error_code', [
    ('http://test.ru/not_exist.zip', codes.created, None),
    ('test', codes.bad_request, PublishError.VALIDATION_ERROR),
    ('', codes.bad_request, PublishError.VALIDATION_ERROR),
    (123, codes.bad_request, PublishError.CLIENT_ERROR),
    ([], codes.bad_request, PublishError.CLIENT_ERROR),
    ({}, codes.bad_request, PublishError.CLIENT_ERROR),
])
def test_publish_with_invalid_url(is_http, is_db, publish_id, url, status_code,
                                  error_code):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: np_cats_qa.steps.db.steps.CatalogServiceDBSteps
    :type publish_id: str
    """

    title_code = TitleCode.PUBLISH_NEGATIVE
    catalog_code = generate_catalog_code(title_code=title_code)

    response = is_http.cats.publish(url, catalog_code, publish_id)
    assert_that(response, has_status_code(status_code), allure_name='response has expected code')

    if status_code == codes.bad_request:
        verify_failed_response(response, error_code)
    else:
        verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.FAILED)


@allure.feature('cats')
@allure.story('publish_validation')
@pytest.mark.parametrize('title_instance_code, error_code', [
    ('ru.not_existing', PublishError.TITLE_NOT_FOUND),
    ('', PublishError.VALIDATION_ERROR),
    ([], PublishError.CLIENT_ERROR),
    ({}, PublishError.CLIENT_ERROR),
    (123, PublishError.CLIENT_ERROR),
])
@pytest.mark.skip(reason="now we send title in the catalog code")
def test_publish_with_invalid_title_instance_code(is_http, catalog_publish_id, catalog_id, catalog_url,
                                                  title_instance_code, error_code):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type catalog_url: str
    :type catalog_publish_id: int
    :type catalog_id: int
    """
    response = is_http.cats.publish(title_instance_code, catalog_url, catalog_id, catalog_publish_id)
    assert_that(response, has_status_code(codes.bad_request), allure_name='response has expected code')

    verify_failed_response(response, error_code)


@allure.feature('cats')
@allure.story('publish_validation')
@pytest.mark.parametrize('catalog_code, error_code', [
    ('test', PublishError.VALIDATION_ERROR),
    ('test-main-1', PublishError.VALIDATION_ERROR),
    ('test-MAIN-1d', PublishError.VALIDATION_ERROR),
    ('test-MAIN-1d-', PublishError.VALIDATION_ERROR),
    ('testMAIN-1d-', PublishError.VALIDATION_ERROR),
    ('test-d-MAIN-1', PublishError.VALIDATION_ERROR),
    ('MORE_THAN_50_12345678987654-MAIN-2147483648333333333', PublishError.VALIDATION_ERROR),
    ('', PublishError.VALIDATION_ERROR),
    (0, PublishError.CLIENT_ERROR),
    ([], PublishError.CLIENT_ERROR),
    ({}, PublishError.CLIENT_ERROR)
])
def test_publish_with_invalid_catalog_id(is_http, publish_id, catalog_url, catalog_code, error_code):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type catalog_url: str
    :type catalog_code: str
    :type publish_id: str
    """
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.bad_request), allure_name='response has expected code')

    verify_failed_response(response, error_code)


@allure.feature('cats')
@allure.story('publish_validation')
@pytest.mark.parametrize('publish_id, error_code', [
    ('test', PublishError.VALIDATION_ERROR),
    ('', PublishError.VALIDATION_ERROR),
    ('01e07exdkc5z04zqftkzeb1gqv', PublishError.VALIDATION_ERROR),
    ('01E07EXDKC5Z04ZQFTKZEB1GQVL', PublishError.VALIDATION_ERROR),
    (0, PublishError.CLIENT_ERROR),
    ([], PublishError.CLIENT_ERROR),
    ({}, PublishError.CLIENT_ERROR)
])
def test_publish_with_invalid_catalog_publish_id(is_http, publish_id, catalog_url,
                                                 catalog_code, error_code):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type catalog_url: str
    :type catalog_code: str
    :type publish_id: int
    """
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.bad_request), allure_name='response has expected code')

    verify_failed_response(response, error_code)


@allure.feature('cats')
@allure.story('publish_validation')
@pytest.mark.parametrize('missing_parameter', [
    'url',
    'catalog_code',
    'publish_id'
])
def test_publish_when_required_parameter_missing(is_http, publish_id, catalog_url, catalog_code,
                                                 missing_parameter):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type catalog_url: str
    :type catalog_id: int
    :type catalog_publish_id: int
    """

    request_body = dict(
        url=catalog_url,
        catalog_code=catalog_code,
        publish_id=publish_id
    )
    request_body.pop(missing_parameter)

    # publish catalog
    response = is_http.cats.publish(data=request_body)
    assert_that(response, has_status_code(codes.bad_request), allure_name='response has expected code')
    verify_failed_response(response, PublishError.VALIDATION_ERROR)


@allure.feature('cats')
@allure.story('catalog_validation')
@pytest.mark.parametrize('catalog', [
    'catalog_invalid_format.zip',
    'catalog_not_zip_format.json',
    'catalog_with_capital_letters_in_params.zip',
    'test_catalog_new_format.zip',
    'catalog_invalid_schema.zip'
])
def test_publish_when_catalog_validation_fails(is_http, is_db, publish_id, catalog_code, catalog, yaml_config):
    url = generate_catalog_url(yaml_config, catalog)
    response = is_http.cats.publish(url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.FAILED)
