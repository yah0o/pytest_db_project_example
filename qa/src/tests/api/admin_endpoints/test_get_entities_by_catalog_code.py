import allure
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import PublishStatus
from np_cats_qa.verifications import verify_publish_completed_with_status_in_db
from hamcrest import contains_string, empty, is_not


@allure.feature('cats')
@allure.story('admin_endpoints')
def test_get_entities_by_catalog_code(is_http, is_db, mock_http, catalog_url, catalog_code, publish_id, title_code):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type catalog_code: str
    :type publish_id: ulid
    :type title_code: str
    """

    response = is_http.cats.publish(catalog_url, catalog_code, publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    # call GET /entities
    response = is_http.cats.get_entities_by_code('gold')
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(bool(response.json()), is_not(False))