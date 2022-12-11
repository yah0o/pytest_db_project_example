import allure
import pytest
from hamcrest import equal_to
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import CatalogError, EntityType


@allure.feature('cats')
@allure.story('get_entity_by_id')
def test_get_entity_by_id_negative(is_http):
    response = is_http.cats.get_entitiy_by_id(entity_id='not_exist')

    assert_that(response, has_status_code(codes.bad), allure_name='response has expected code')
    assert_that(response.json()['error']['code'], equal_to(CatalogError.ENTITY_NOT_FOUND))
    assert_that(response.json()['error']['context']['description'], equal_to('Entity is not found.'))
    assert_that(response.json()['error']['context']['entity_id'], equal_to('not_exist'))
