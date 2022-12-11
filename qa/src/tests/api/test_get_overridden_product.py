import allure
import pytest
from hamcrest import has_entries, has_key, equal_to
from npqa_matchers.http import has_status_code
from npqa_report import assert_that
from requests import codes

from np_cats_qa.constants import CatalogTypes, PublishError


@allure.feature('cats')
@allure.story('test_get_overridden_product')
@pytest.mark.parametrize('product_code, promo_code, storefront_code', [
    ('test_product_discount_vc_price', 'discount_fixed_vc_promotion', 'test_fixed_vc_discount_store'),
    ('product_with_expired_promo', 'test_override_promo', 'test_store'),
    ('product_with_promo_not_started', 'promotion_not_started', 'test_store'),
    ('product_vc_with_promo_not_started', 'promotion_not_started', 'test_store')
])
def test_get_product_with_promo(is_http, title_code, product_code, promo_code, storefront_code):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """

    active_catalog = is_http.cats.get_active_catalog_by_title_code(title_code, CatalogTypes.MAIN_TYPE)
    response = is_http.cats.get_product_with_applied_promo(catalog_code=active_catalog.json()['catalog_code'],
                                                           product_code=product_code,
                                                           promo_code=promo_code,
                                                           storefront_code=storefront_code)

    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.json(), has_entries(friendly_name='overridden_name',
                                             metadata=has_key('overridden_namespace')))


@allure.feature('cats')
@allure.story('test_get_overridden_product')
def test_get_product_when_product_does_not_match_promo(is_http, title_code):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """
    product_code = 'test_product_xp'
    promo_code = 'blank_fields_override_promotion'
    storefront_code = 'test_blank_fields_override_store'

    active_catalog = is_http.cats.get_active_catalog_by_title_code(title_code, CatalogTypes.MAIN_TYPE)
    response = is_http.cats.get_product_with_applied_promo(catalog_code=active_catalog.json()['catalog_code'],
                                                           product_code=product_code,
                                                           promo_code=promo_code,
                                                           storefront_code=storefront_code)

    assert_that(response, has_status_code(codes.bad), allure_name='response has expected code')
    assert_that(response.json()['error']['code'], equal_to(PublishError.CLIENT_ERROR),
                allure_name='response has expected error')
    assert_that(response.json()['error']['context']['description'],
                equal_to("Promo \'{}\' hasn\'t got specified product \'{}\'".format(promo_code, product_code)))


@allure.feature('cats')
@allure.story('test_get_overridden_product')
def test_get_product_when_storefront_does_not_match_promo(is_http, title_code):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """
    product_code = 'test_product_discount_vc_price'
    promo_code = 'discount_fixed_vc_promotion'
    storefront_code = 'test_store'

    active_catalog = is_http.cats.get_active_catalog_by_title_code(title_code, CatalogTypes.MAIN_TYPE)
    response = is_http.cats.get_product_with_applied_promo(catalog_code=active_catalog.json()['catalog_code'],
                                                           product_code=product_code,
                                                           promo_code=promo_code,
                                                           storefront_code=storefront_code)

    assert_that(response, has_status_code(codes.bad), allure_name='response has expected code')
    assert_that(response.json()['error']['code'], equal_to(PublishError.CLIENT_ERROR),
                allure_name='response has expected error')
    assert_that(response.json()['error']['context']['description'],
                equal_to("Promo \'{}\' hasn\'t got specified storefront \'{}\'".format(promo_code, storefront_code)))


@allure.feature('cats')
@allure.story('test_get_overridden_product')
def test_get_product_with_several_fields_overridden(is_http, title_code):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """
    product_code = 'product_rm_with_categories'
    promo_code = 'promo_several_fields_overridden'
    storefront_code = 'test_store'
    overriden_value = 'overridden_data'

    active_catalog = is_http.cats.get_active_catalog_by_title_code(title_code, CatalogTypes.MAIN_TYPE)
    response = is_http.cats.get_product_with_applied_promo(catalog_code=active_catalog.json()['catalog_code'],
                                                           product_code=product_code,
                                                           promo_code=promo_code,
                                                           storefront_code=storefront_code)
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.json(), has_entries(friendly_name=overriden_value,
                                             purchasable=False,
                                             visible=False,
                                             tags=overriden_value,
                                             giftable=True,
                                             fulfillment_type="HOLD",
                                             merge_quantity=False,
                                             restricted=["kr"],
                                             payment_group=[overriden_value],
                                             personal_limit=10,
                                             categories=[overriden_value],
                                             metadata=has_key(overriden_value)),
                allure_name='response fields have expected values')


@allure.feature('cats')
@allure.story('test_get_overridden_product_by_new_promo')
def test_get_product_with_several_fields_overridden_by_new_promo(is_http, title_code):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """
    # NEW LQO format FREYA-1168
    product_code = 'product_rm_with_categories'
    promo_code = 'new_promo_several_fields_overridden'
    storefront_code = 'test_store'
    overriden_value = 'overridden_data'

    active_catalog = is_http.cats.get_active_catalog_by_title_code(title_code, CatalogTypes.MAIN_TYPE)
    response = is_http.cats.get_product_with_applied_promo(catalog_code=active_catalog.json()['catalog_code'],
                                                           product_code=product_code,
                                                           promo_code=promo_code,
                                                           storefront_code=storefront_code)
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.json(), has_entries(friendly_name=overriden_value,
                                             purchasable=False,
                                             visible=False,
                                             tags=overriden_value,
                                             giftable=True,
                                             fulfillment_type="HOLD",
                                             merge_quantity=False,
                                             restricted=["kr"],
                                             payment_group=[overriden_value],
                                             personal_limit=10,
                                             realm_limit=20,
                                             show_limit_exceeded=True,
                                             categories=[overriden_value],
                                             metadata=has_key(overriden_value)),
                allure_name='response fields have expected values')


@allure.feature('cats')
@allure.story('test_get_overridden_product_by_new_promo')
def test_get_product_with_several_fields_overridden_by_new_promo_empty_limits(is_http, title_code):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """
    # NEW LQO format FREYA-1168
    product_code = 'product_rm_wo_categories'
    promo_code = 'new_promo_several_fields_overridden_empty_limits'
    storefront_code = 'test_store'
    overriden_value = 'overridden_data'

    active_catalog = is_http.cats.get_active_catalog_by_title_code(title_code, CatalogTypes.MAIN_TYPE)
    response = is_http.cats.get_product_with_applied_promo(catalog_code=active_catalog.json()['catalog_code'],
                                                           product_code=product_code,
                                                           promo_code=promo_code,
                                                           storefront_code=storefront_code)
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.json(), has_entries(friendly_name=overriden_value,
                                             purchasable=False,
                                             visible=False,
                                             tags=overriden_value,
                                             giftable=True,
                                             fulfillment_type="HOLD",
                                             merge_quantity=False,
                                             restricted=["kr"],
                                             payment_group=[overriden_value],
                                             show_limit_exceeded=True,
                                             categories=[overriden_value],
                                             metadata=has_key(overriden_value)),
                allure_name='response fields have expected values')


@allure.feature('cats')
@allure.story('test_get_overridden_product')
def test_get_product_with_several_overrides(is_http, title_code):
    """
    :type is_http: np_cats_qa.steps.http.CatalogServiceHttpSteps
    :type title_code: str
    """
    product_code = 'test_product_discount_vc_and_real_price'
    promo_code = 'many_discounts_second_half_promotion'
    storefront_code = 'test_discount_multiple_promos_store'

    active_catalog = is_http.cats.get_active_catalog_by_title_code(title_code, CatalogTypes.MAIN_TYPE)
    response = is_http.cats.get_product_with_applied_promo(catalog_code=active_catalog.json()['catalog_code'],
                                                           product_code=product_code,
                                                           promo_code=promo_code,
                                                           storefront_code=storefront_code)
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected code')
    assert_that(response.json(), has_entries(tags='override_4'), allure_name='response fields have expected values')
