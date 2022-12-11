import allure
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes
from ulid2 import generate_ulid_as_base32

from np_cats_qa.constants import AUDIT, PublishStatus
from np_cats_qa.constants import Contracts
from np_cats_qa.verifications import verify_audit, verify_publish_completed_with_status_in_db


@allure.feature('cats')
@allure.story('audit_lib')
def test_publish_audit(is_http, clickhouse_client, catalog_url, is_db,
                       title_code, catalog_code, publish_id):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type catalog_url: str
    :type catalog_code: str
    :type title_code: str
    :type publish_id: ulid
    """
    # Test on audit Publish, Get Active catalog calls
    tracking_id = generate_ulid_as_base32()
    emitter_id = '12'
    # publish catalog
    response = is_http.cats.publish(catalog_url, catalog_code, publish_id, tracking_id=tracking_id,
                                    emitter_id=emitter_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')
    # check clichouse
    verify_audit(response, clickhouse_client,
                 request_tracking_id=tracking_id,
                 request_emitter_id=emitter_id,
                 expected_action=AUDIT.EXPECTED_CATS_ACTION_PUBLISH,
                 expected_processor=AUDIT.EXPECTED_CATS_PROCESSOR)

    new_tracking_id = generate_ulid_as_base32()
    emitter_id = '123'

    # waiting FAILED or COMPLETED status
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    # get activate catalog
    get_active_catalog_response = is_http.cats.get_active_catalog_by_title_code(title_code, 'MAIN',
                                                                                tracking_id=new_tracking_id,
                                                                                emitter_id=emitter_id)
    # check clichouse
    verify_audit(get_active_catalog_response, clickhouse_client,
                 request_tracking_id=new_tracking_id,
                 request_emitter_id=emitter_id,
                 expected_action=AUDIT.EXPECTED_CATS_ACTION_ACTIVE_CATALOGS,
                 expected_processor=AUDIT.EXPECTED_CATS_PROCESSOR)


@allure.feature('cats')
@allure.story('audit_lib')
def test_fetch_storefront_categories_audit(capi, clickhouse_client, capi_client_emitter_id, yaml_config):
    tracking_id = generate_ulid_as_base32()
    storefront = yaml_config.data.STOREFRONT_WITH_TWO_CATEGORIES
    response = capi.commerce.fetch_storefront_categories_v2(title_code=yaml_config.data.TITLE_CODE,
                                                            storefront=storefront.CODE,
                                                            tracking_id=tracking_id)

    verify_audit(response, clickhouse_client, request_tracking_id=tracking_id,
                 expected_action=Contracts.COMMERCE_FETCH_STOREFRONT_CATEGORIES_V2,
                 request_emitter_id=capi_client_emitter_id,
                 expected_processor=AUDIT.EXPECTED_CATS_PROCESSOR)
