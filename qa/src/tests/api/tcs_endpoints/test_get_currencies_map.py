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
def test_get_currencies_map(is_http, is_db, yaml_config, catalog_url, catalog_code, publish_id):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: np_cats_qa.steps.db.steps.CatalogServiceDBSteps
    :type catalog_url: str
    :type catalog_code: str
    :type publish_id: ulid
    """

    # prepare
    shared_currency_catalog_url = yaml_config.data.CATALOG_DOMAIN + '/' + CatalogZIP.SHARED_CURRENCY_CATALOG
    shared_currency_catalog_code = '{}-MAIN-1'.format(TitleCode.SHARED_CURRENCY)

    # publish shared_currency catalog
    response_publish = is_http.cats.publish(shared_currency_catalog_url, shared_currency_catalog_code, publish_id)
    assert_that(response_publish, has_status_code(codes.created), allure_name='response has expected code')
    verify_publish_completed_with_status_in_db(is_db, publish_id, PublishStatus.COMPLETED)

    # publish test catalog
    new_publish_id = ulid()
    response = is_http.cats.publish(catalog_url, catalog_code, new_publish_id)
    assert_that(response, has_status_code(codes.created), allure_name='response has expected code')
    verify_publish_completed_with_status_in_db(is_db, new_publish_id, PublishStatus.COMPLETED)

    # call GET currencies map
    response = is_http.cats.get_currencies_map()
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')

    # verify currencies/map response: should show currencies and shared currencies for active titles
    currencies_data = response.json()['data']
    assert_that(currencies_data, not_empty(), allure_name='response data not empty')
    shared_currencies = []
    nptst_currencies = []

    for item in currencies_data:
        assert_that(item, has_entries(title=not_empty(),
                                      currencies=not_empty()),
                    allure_name='response has expected fields')
        if item['title'] == TitleCode.SHARED_CURRENCY:
            for currency in item['currencies']:
                shared_currencies.append(currency['platform_code'])
        if item['title'] == TitleCode.NPTST_TITLE:
            for currency in item['currencies']:
                nptst_currencies.append(currency['platform_code'])

    assert_that(currency, has_only_keys('local_code', 'owner_title', 'platform_code'),
                allure_name='currency has expected fields only')
    assert_that(shared_currencies, equal_to(yaml_config.data.CURRENCIES.SHARED),
                allure_name='response has expected shared currencies')
    assert_that(nptst_currencies, equal_to(yaml_config.data.CURRENCIES.SHARED + yaml_config.data.CURRENCIES.NPTST),
                allure_name='response has expected catalog currencies')
