import allure
import pytest
from capi_lib_python import TriggerMessageValidationError
from hamcrest import equal_to, all_of, contains_string
from npqa_report import assert_that

from np_cats_qa.constants import CategoryStatus, ContractMessage


@pytest.mark.parametrize('fields_to_remove', [
    'title_code',
    'storefront'
])
@allure.feature('capi')
@allure.story('fetch_categories_negative')
def test_fetch_categories_without_required_parameters(capi, title_code, yaml_config, fields_to_remove):
    storefront = yaml_config.data.STOREFRONT_WITH_TWO_CATEGORIES.CODE
    response = capi.commerce.fetch_storefront_categories_v2(title_code=title_code,
                                                            storefront=storefront,
                                                            fields_to_remove=fields_to_remove)
    assert_that(type(response), equal_to(TriggerMessageValidationError), allure_name='CAPI return error.')


@allure.feature('capi')
@allure.story('fetch_categories_negative')
@pytest.mark.parametrize(
    ('bad_title_code', 'bad_storefront', 'bad_language', 'bad_activation_status', 'expected_error'), [
    (123,               False,            False,          False,                   "not of type 'string'"),
    ({},                False,            False,          False,                   "not of type 'string'"),
    ([],                False,            False,          False,                   "not of type 'string'"),
    ("a" * 51,          False,            False,          False,                   "is too long"),
    ('',                False,            False,          False,                   "is too short"),
    (False,             123,              False,          False,                   "not of type 'string'"),
    (False,             {},               False,          False,                   "not of type 'string'"),
    (False,             [],               False,          False,                   "not of type 'string'"),
    (False,             '',               False,          False,                   "is too short"),
    (False,             'a' * 51,         False,          False,                   "is too long"),
    (False,             False,            123,            False,                   "not of type 'string'"),
    (False,             False,            {},             False,                   "not of type 'string'"),
    (False,             False,            [],             False,                   "not of type 'string'"),
    (False,             False,            'a' * 10,       False,                   "is too long"),
    (False,             False,            'a',            False,                   "is too short"),
    (False,             False,            False,          'test',                  "is not of type 'array'"),
    (False,             False,            False,          [],                      "is too short"),
    (False,             False,            False,          {},                      "is not of type 'array'"),
    (False,             False,            False,          123,                     "is not of type 'array'"),
    (False,             False,            False,          ['test'],                 "is not one of ['expired', "
                                                                                    "'active', "
                                                                                    "'waiting_for_activation']")
])
def test_fetch_categories_with_incorrect_parameters(capi, yaml_config, bad_title_code, bad_storefront,
                                                    bad_language, bad_activation_status, expected_error):
    title_code = yaml_config.data.TITLE_CODE if bad_title_code is False else bad_title_code
    storefront = yaml_config.data.STOREFRONT_WITH_TWO_CATEGORIES.CODE if bad_storefront is False else bad_storefront
    language = 'EN' if bad_language is False else bad_language
    activation_statuses = CategoryStatus.ACTIVE if bad_activation_status is False else bad_activation_status

    response = capi.commerce.fetch_storefront_categories_v2(title_code=title_code,
                                                            storefront=storefront,
                                                            language=language,
                                                            activation_statuses=activation_statuses)
    assert_that(type(response), equal_to(TriggerMessageValidationError), allure_name='response has expected type')
    assert_that(response.args[0], all_of(contains_string(ContractMessage.INVALID_DATA),
                                         contains_string(expected_error)),
                allure_name='response has expected error')
