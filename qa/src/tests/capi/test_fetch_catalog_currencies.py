import allure
import pytest
from capi_lib_python.exceptions import CAPIResponseError
from hamcrest import equal_to, has_key, has_length, has_entry, has_entries
from npqa_report import assert_that

from np_cats_qa.constants import TitleCode, Currency, ContractError
from np_cats_qa.matchers import not_empty


@allure.feature('capi')
@allure.story('fetch_catalog_currencies')
def test_fetch_catalog_currencies(capi, yaml_config):
    response = capi.commerce.fetch_catalog_currencies_v1(title_code=yaml_config.data.TITLE_CODE)
    sorted_currencies_data = sorted(response['currencies'], key=lambda i: i['platform_code'])
    assert_that(sorted_currencies_data, not_empty(), allure_name='response data not empty')

    shared_currencies = []
    nptst_currencies = []

    for item in sorted_currencies_data:
        assert_that(item, has_entries(owner_title=not_empty(),
                                      platform_code=not_empty()),
                    allure_name='response has expected fields')
        if item['owner_title'] == TitleCode.SHARED_CURRENCY:
            shared_currencies.append(item['platform_code'])
            if item['code'] == 'gold':
                assert_that(item, has_entries(media=not_empty(),
                                              metadata=not_empty(),
                                              localization=not_empty()),
                            allure_name='ru.shared_currency.gold has expected fields')

        if item['owner_title'] == TitleCode.NPTST_TITLE:
            nptst_currencies.append(item['platform_code'])

    assert_that(shared_currencies, equal_to(yaml_config.data.CURRENCIES_WITH_NON_ACTIVE.SHARED),
                allure_name='response has expected shared currencies')
    assert_that(nptst_currencies, equal_to(yaml_config.data.CURRENCIES_WITH_NON_ACTIVE.NPTST),
                allure_name='response has expected catalog currencies')


@allure.feature('capi')
@allure.story('fetch_catalog_currencies')
def test_fetch_catalog_currencies_with_etag(capi, yaml_config):
    response = capi.commerce.fetch_catalog_currencies_v1(title_code=yaml_config.data.TITLE_CODE)
    assert_that(response, has_key('etag'), allure_name='response has etag')

    response2 = capi.commerce.fetch_catalog_currencies_v1(title_code=yaml_config.data.TITLE_CODE, etag=response['etag'])
    assert_that(isinstance(response2, CAPIResponseError), equal_to(True), allure_name='CAPI return error.')
    assert_that(response2.code, equal_to('common.not-modified.v1'), allure_name='CAPI return error.')


@allure.feature('capi')
@allure.story('fetch_catalog_currencies')
def test_fetch_catalog_currencies_with_codes_filter(capi, yaml_config):
    response = capi.commerce.fetch_catalog_currencies_v1(title_code=yaml_config.data.TITLE_CODE,
                                                         currency_codes=['credits'])

    assert_that(response['currencies'], has_length(1), allure_name='response has expected currencies number')
    assert_that(response['currencies'][0], has_entry('code', 'credits'), allure_name='response has expected currency')


@allure.feature('capi')
@allure.story('fetch_catalog_currencies')
def test_fetch_catalog_currencies_non_standard_currency(capi, yaml_config):
    # fetch 'sacoin' non-standard curency
    response = capi.commerce.fetch_catalog_currencies_v1(title_code=yaml_config.data.TITLE_CODE,
                                                         currency_codes=['sacoin'])
    assert_that(response['currencies'], has_length(1), allure_name='response has expected currencies number')
    assert_that(response['currencies'][0]['code'], equal_to(Currency.SACOIN),
                allure_name='response has expected currency code')
    assert_that(response['currencies'][0], has_entries(localization=not_empty(),
                                                       is_active=True,
                                                       is_reported=True,
                                                       metadata=not_empty(),
                                                       owner_title=yaml_config.data.TITLE_CODE,
                                                       platform_code=yaml_config.data.TITLE_CODE + '.'
                                                                     + Currency.SACOIN,
                                                       media=not_empty()
                                                       ),
                allure_name='ru.nptst.sacoin has expected fields')


@allure.feature('capi')
@allure.story('fetch_catalog_currencies')
def test_fetch_catalog_currencies_filter_different_currencies(capi, yaml_config):
    response = capi.commerce.fetch_catalog_currencies_v1(title_code=yaml_config.data.TITLE_CODE,
                                                         currency_codes=['sacoin', 'credits'])
    assert_that(response['currencies'], has_length(2), allure_name='response has expected currencies number')
    assert_that(response['currencies'][0]['code'], equal_to(Currency.SACOIN),
                allure_name='response has expected currency code')
    assert_that(response['currencies'][1]['code'], equal_to(Currency.CREDITS),
                allure_name='response has expected currency code')


@allure.feature('capi')
@allure.story('fetch_catalog_currencies')
def test_fetch_catalog_currencies_with_not_exist_currency(capi, yaml_config):
    response = capi.commerce.fetch_catalog_currencies_v1(title_code=yaml_config.data.TITLE_CODE,
                                                         currency_codes=['not_exist'])
    assert_that(response['currencies'], has_length(0), allure_name='response has expected currencies number')


@allure.feature('capi')
@allure.story('fetch_catalog_currencies')
@pytest.mark.parametrize('title_code', ['not_exist', 'ru.inactive', 'ru.inactive_db'])
def test_fetch_catalog_currencies_with_not_exist_title(capi, yaml_config, title_code, update_titles):
    response = capi.commerce.fetch_catalog_currencies_v1(title_code=title_code)
    assert_that(response.code, equal_to(ContractError.COMMERCE_CATALOG_ERROR))
