import allure
from hamcrest import equal_to
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
def test_get_currencies(is_http, is_db, yaml_config, catalog_url, catalog_code, publish_id):
    """
    :type is_http: db_prj_qa.steps.http.CatalogServiceHttpSteps
    :type is_db: db_prj_qa.steps.db.steps.CatalogServiceDBSteps
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

    # call GET /currencies
    response = is_http.cats.get_currencies()
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')

    # verify /currencies response: should show currencies for active titles
    currencies = response.json()['data']
    assert_that(currencies, not_empty(), allure_name='response data not empty')
    shared_currencies = []
    nptst_currencies = []

    for currency in currencies:
        if currency['title'] == TitleCode.SHARED_CURRENCY:
            shared_currencies.append(currency['code'])
        if currency['title'] == TitleCode.NPTST_TITLE:
            nptst_currencies.append(currency['code'])

    assert_that(currency, has_only_keys('title', 'code', 'decimal_places', 'is_real', 'is_reported'),
                allure_name='response has only expected fields')
    assert_that(shared_currencies, equal_to(yaml_config.data.CURRENCIES.SHARED),
                allure_name='response has expected shared currencies')
    assert_that(nptst_currencies, equal_to(yaml_config.data.CURRENCIES.NPTST),
                allure_name='response has expected catalog currencies')
