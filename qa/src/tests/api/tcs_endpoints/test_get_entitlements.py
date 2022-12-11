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
def test_get_entitlements(is_http, is_db, yaml_config, catalog_url, catalog_code, publish_id):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: np_cats_qa.steps.db.steps.CatalogServiceDBSteps
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

    # call GET /entitlements
    response = is_http.cats.get_entitlements()
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')

    # verify /entitlements response: should show premium_plus and shared_premium entitlements for active titles
    entitlements = response.json()['entitlements']
    assert_that(entitlements, not_empty(), allure_name='response data not empty')

    for entitlement in entitlements:
        assert_that(entitlement['code'] in ('premium', 'premium_plus', 'premium_subs'), equal_to(True))
        # check data consistency
        if entitlement['title_code'] == TitleCode.SHARED_PREMIUM:
            assert_that(entitlement, has_entries(id=not_empty(),
                                                 version=not_empty(),
                                                 code='premium',
                                                 title_code=TitleCode.SHARED_PREMIUM,
                                                 friendly_name=not_empty(),
                                                 reported=not_empty()),
                        allure_name='response items has expected fields')

    assert_that(entitlement, has_only_keys('id', 'version', 'code', 'title_code', 'friendly_name', 'reported'),
                allure_name='response has only expected fields')
