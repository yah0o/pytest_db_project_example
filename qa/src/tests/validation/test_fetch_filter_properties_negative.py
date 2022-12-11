import allure
import pytest
from capi_lib_python import TriggerMessageValidationError
from hamcrest import equal_to, all_of, contains_string
from npqa_report import assert_that

from np_cats_qa.constants import ContractMessage


@allure.feature('capi')
@allure.story('fetch_filter_properties negative')
def test_fetch_filter_properties_without_required_params(capi, title_code):
    field_to_delete = 'title_code'
    response = capi.commerce.fetch_filter_properties_v1(title_code=title_code, fields_to_remove=field_to_delete,
                                                        language='en')

    assert_that(type(response), equal_to(TriggerMessageValidationError), allure_name='CAPI return error.')
    assert_that(response.args[0], all_of(contains_string(ContractMessage.INVALID_DATA),
                                         contains_string('\'{}\' is a required property'.format(field_to_delete))),
                allure_name='response has expected error')


@allure.feature('capi')
@allure.story('fetch_filter_properties negative')
@pytest.mark.parametrize('bad_title_code, bad_language, expected_error', [
                         (123,            False,        "not of type 'string'"),
                         ({},             False,         "not of type 'string'"),
                         ([],             False,         "not of type 'string'"),
                         ('',             False,         "is too short"),
                         ('a' * 51,       False,         "is too long"),
                         (False,          123,           "not of type 'string'"),
                         (False,          {},            "not of type 'string'"),
                         (False,          [],            "not of type 'string'"),
                         (False,          'a',           "is too short"),
                         (False,          'a' * 10,      "is too long")
])
def test_fetch_filter_properties_with_invalid_params(capi, yaml_config, title_code, bad_language, bad_title_code,
                                                     expected_error):
    title_code = yaml_config.data.TITLE_CODE if bad_title_code is False else bad_title_code
    language = 'en' if bad_language is False else bad_language

    response = capi.commerce.fetch_filter_properties_v1(title_code=title_code, language=language)

    assert_that(type(response), equal_to(TriggerMessageValidationError), allure_name='response has expected type')
    assert_that(response.args[0], all_of(contains_string(ContractMessage.INVALID_DATA),
                                         contains_string(expected_error)),
                allure_name='response has expected error')
