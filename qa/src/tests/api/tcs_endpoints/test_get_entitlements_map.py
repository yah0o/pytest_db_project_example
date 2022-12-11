import allure
from hamcrest import equal_to, has_entries
from npqa_matchers.dictionary import has_only_keys
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import PublishStatus, TitleCode, CatalogZIP
from np_cats_qa.helpers import ulid
from np_cats_qa.matchers import not_empty
from np_cats_qa.verifications import verify_publish_completed_with_status_in_db


@allure.feature('cats')
@allure.story('tsc_endpoints')
def test_get_entitlements_map(is_http, is_db, yaml_config, catalog_url, catalog_code, publish_id):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type catalog_code: str
    :type publish_id: ulid
    """

    # prepare
    shared_currency_catalog_url = yaml_config.data.CATALOG_DOMAIN + '/' + CatalogZIP.SHARED_PREMIUM_CATALOG
    shared_currency_catalog_code = '{}-MAIN-1'.format(TitleCode.SHARED_PREMIUM)

    # publish shared_premium catalog
    response_publish = is_http.cats.publish(shared_currency_catalog_url, shared_currency_catalog_code, publish_id)
    assert_that(response_publish, has_status_code(codes.created), allure_name='response has expected code')
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    # publish test catalog
    new_publish_id = ulid()
    response = is_http.cats.publish(catalog_url, catalog_code, new_publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')
    verify_publish_completed_with_status_in_db(is_db, new_publish_id, PublishStatus.COMPLETED)

    # call GET /entitlements/map
    response = is_http.cats.get_entitlements_map()
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')

    # verify /entitlements/map response: should show premium_plus and shared_premium entitlements for active titles
    entitlements_data = response.json()['data']
    assert_that(entitlements_data, not_empty(), allure_name='response data not empty')

    for item in entitlements_data:
        assert_that(item, has_entries(entitlements=not_empty(),
                                      title=not_empty()), allure_name='response items has expected fields')
        for entitlement in item['entitlements']:
            assert_that(entitlement['local_code'] in ('premium', 'premium_plus', 'premium_subs'), equal_to(True))

    assert_that(entitlement, has_only_keys('local_code', 'owner_title', 'platform_code'),
                allure_name='response has only expected fields')
