import json
import logging

import allure
import pytest
from hamcrest import has_entries, equal_to
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import PublishStatus, CatalogZIP, ContractError
from np_cats_qa.matchers import not_empty
from np_cats_qa.verifications import verify_publish_completed_with_status_in_db


# if run locally after start containers run first test_prepare_catalog first


@allure.feature('capi')
@allure.story('fetch_filter_properties')
def test_fetch_filter_properties(capi, yaml_config, mock_http):
    extract_path = 'tmp/'
    entity_file = 'filter_properties.json'

    response = capi.commerce.fetch_filter_properties_v1(title_code=yaml_config.data.TITLE_CODE)

    assert_that(allure_name='Response has filter properties',
                actual=response,
                matcher=has_entries(
                    filter_properties=not_empty()
                ))
    assert_that(allure_name='Response has 3 filter properties',
                actual=len(response['filter_properties']),
                matcher=equal_to(4))

    # prepare expected catalog data
    mock_http.extract_catalog_by_catalog_code_to(catalog_file=CatalogZIP.DEFAULT_CATALOG, extract_path=extract_path)

    with open(extract_path + entity_file) as f:
        entity_from_catalog = json.load(f)

    expected_data = []
    for item in entity_from_catalog:
        filter = dict()
        filter.update({'code': item['code'], 'type': item['value_type']})
        if 'metadata' in item.keys():
            filter.update({'metadata': item['metadata']})
        expected_data.append(filter)

    sorted_filter_properties = sorted(response['filter_properties'], key=lambda i: i['code'])
    sorted_expected_filter_properties = sorted(expected_data, key=lambda i: i['code'])

    assert_that(sorted_filter_properties, equal_to(sorted_expected_filter_properties),
                allure_name='response has expected entities')


@allure.feature('capi')
@allure.story('fetch_filter_properties')
@pytest.mark.parametrize('language', ['en', 'de', 'ru', 'fr'])
def test_fetch_filter_properties_with_localization(capi, yaml_config, mock_http, language):
    response = capi.commerce.fetch_filter_properties_v1(title_code=yaml_config.data.TITLE_CODE, language=language)

    assert_that(allure_name='Response has filter properties',
                actual=response,
                matcher=has_entries(
                    filter_properties=not_empty()
                ))

    localized_filter = None
    for item in response['filter_properties']:
        if item['code'] == 'localization':
            localized_filter = item

    localized_meta = 'Test_{}'.format(language.lower())
    assert_that(localized_filter['metadata']['name']['data'], equal_to({language: localized_meta,
                                                                        'value': localized_meta}),
                allure_name='response has expected localization')


@allure.feature('capi')
@allure.story('fetch_catalog_currencies')
@pytest.mark.parametrize('title_code', ['not_exist', 'ru.inactive', 'ru.inactive_db'])
def test_fetch_filter_properties_with_not_exist_title(capi, yaml_config, title_code, update_titles):
    response = capi.commerce.fetch_filter_properties_v1(title_code=title_code)
    assert_that(response.code, equal_to(ContractError.COMMERCE_CATALOG_ERROR))
