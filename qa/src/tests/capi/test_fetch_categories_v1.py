import allure
import pytest
from capi_lib_python import CAPIResponseError
from hamcrest import has_entries, equal_to
from hamcrest import has_length
from npqa_report import assert_that

from np_cats_qa.constants import CategoryStatus, ContractError
from np_cats_qa.matchers import not_empty


# if run locally after start containers run first test_prepare_catalog first


@allure.feature('capi')
@allure.story('fetch_categories')
def test_fetch_storefront_with_categories(capi, yaml_config):
    storefront = yaml_config.data.STOREFRONT_WITH_TWO_CATEGORIES
    response = capi.commerce.fetch_storefront_categories_v1(title_code=yaml_config.data.TITLE_CODE,
                                                            storefront=storefront.CODE)

    sorted_categories = sorted(response['categories'], key=lambda i: i['code'])

    assert_that(sorted_categories, has_length(2), allure_name='response has excepted categories number')
    assert_that(sorted_categories[0], has_entries(sort_number=storefront.CATEGORY_ACTIVE.SORT_NUMBER,
                                                  activation_status=CategoryStatus.ACTIVE,
                                                  code=storefront.CATEGORY_ACTIVE.CODE,
                                                  parent_code=storefront.CATEGORY_ACTIVE.PARENT_CODE),
                allure_name='category has expected parameters')

    assert_that(sorted_categories[1], has_entries(sort_number=storefront.CATEGORY_EXPIRED.SORT_NUMBER,
                                                  activation_status=CategoryStatus.EXPIRED,
                                                  code=storefront.CATEGORY_EXPIRED.CODE,
                                                  metadata={}),
                allure_name='category has expected parameters')


@allure.feature('capi')
@allure.story('fetch_categories')
def test_fetch_storefront_with_several_categories(capi, yaml_config):
    response = capi.commerce.fetch_storefront_categories_v1(title_code=yaml_config.data.TITLE_CODE,
                                                            storefront="test_store_categories", language="RU")

    assert_that(allure_name='Response has categories',
                actual=response,
                matcher=has_entries(
                    categories=not_empty()
                ))
    assert_that(allure_name='Response has 11 categories',
                actual=len(response['categories']),
                matcher=equal_to(11))


@allure.feature('capi')
@allure.story('fetch_categories_no_categories')
def test_fetch_categories_no_categories(capi, yaml_config):
    response = capi.commerce.fetch_storefront_categories_v1(title_code=yaml_config.data.TITLE_CODE,
                                                            storefront="test_store_without_categories")

    assert_that(response['categories'], equal_to([]), allure_name='Response has no categories')


@allure.story('fetch_categories_with_status_filter')
@pytest.mark.parametrize('status, expected_number', [
    (CategoryStatus.ACTIVE, 8),
    (CategoryStatus.EXPIRED, 2),
    (CategoryStatus.WAITING_FOR_ACTIVATION, 1)
])
def test_fecth_categories_with_status_filter(capi, yaml_config, status, expected_number):
    response = capi.commerce.fetch_storefront_categories_v1(title_code=yaml_config.data.TITLE_CODE,
                                                            storefront="test_store_categories",
                                                            activation_statuses=[status])
    categories = response['categories']
    assert_that(categories, has_length(expected_number), allure_name='response has expected categories number')
    for category in categories:
        assert_that(category['activation_status'], equal_to(status), allure_name='category has expected status')


@allure.feature('capi')
@allure.story('fetch_categories')
@pytest.mark.parametrize('language', ['EN', 'FR', 'RU', 'DE'])
def test_fetch_categories_with_meta_localization(capi, yaml_config, language):
    response = capi.commerce.fetch_storefront_categories_v1(title_code=yaml_config.data.TITLE_CODE,
                                                            storefront="test_store_with_category_and_meta_localization",
                                                            language=language)
    assert_that(response['categories'][0]['code'], equal_to('test_category_with_meta'),
                allure_name='response has correct category')
    localized_meta = 'Test_{}'.format(language.lower())
    assert_that(response['categories'][0]['metadata']['name']['data'], equal_to({language: localized_meta,
                                                                                 'value': localized_meta}),
                allure_name='response has expected localization')
    assert_that(response['categories'][0]['metadata']['description']['data'], equal_to({language: localized_meta,
                                                                                        'value': localized_meta}),
                allure_name='response has expected localization')


@allure.feature('capi')
@allure.story('fetch_categories_not_catalog')
def test_fetch_categories_no_catalog(capi, yaml_config):
    response = capi.commerce.fetch_storefront_categories_v1(title_code=yaml_config.data.NO_CATALOG_TITLE_CODE,
                                                            storefront=yaml_config.data.STOREFRONT_WITH_TWO_CATEGORIES.CODE)
    assert_that(type(response), equal_to(CAPIResponseError), allure_name='response has expected type')
    assert_that(response.code, equal_to(ContractError.COMMERCE_CATALOG_ERROR),
                allure_name='response has expected error code')

    assert_that(response.context['result_code'], equal_to('CATALOG_NOT_FOUND'),
                allure_name='Expected CATALOG_NOT_FOUND code')


@allure.feature('capi')
@allure.story('fetch_categories_negative')
def test_fetch_categories_when_storefront_not_found(capi, yaml_config, title_code):
    response = capi.commerce.fetch_storefront_categories_v1(title_code=title_code,
                                                            storefront='test_store_not_found')

    assert_that(type(response), equal_to(CAPIResponseError), allure_name='response has expected type')
    assert_that(response.code, equal_to(ContractError.COMMERCE_CATALOG_ERROR), allure_name='response has expected code')
    assert_that(response.args[1]['result_code'], equal_to('STOREFRONT_NOT_FOUND'),
                allure_name='response has expected result_code')

@allure.feature('capi')
@allure.story('fetch_categories_not_title')
@pytest.mark.parametrize('title_code', ['not_exist', 'ru.inactive', 'ru.inactive_db'])
def test_fetch_categories_no_title(capi, yaml_config, title_code, update_titles):
  response = capi.commerce.fetch_storefront_categories_v1(title_code=title_code,
                                                          storefront=yaml_config.data.STOREFRONT_WITH_TWO_CATEGORIES.CODE)
  assert_that(type(response), equal_to(CAPIResponseError), allure_name='response has expected type')
  assert_that(response.code, equal_to(ContractError.COMMERCE_CATALOG_ERROR),
              allure_name='response has expected error code')
  assert_that(response.code, equal_to(ContractError.COMMERCE_CATALOG_ERROR), allure_name='response has expected code')
  assert_that(response.args[1]['result_code'], equal_to('TITLE_NOT_FOUND'),
              allure_name='response has expected result_code')