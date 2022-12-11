# used in docker-compose.yaml option SERVICE_REALM
SERVICE_REALM = 'itests'


class PublishStatus(object):
    PENDING = 'PENDING'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'

class AUDIT(object):
    EXPECTED_CATS_ACTION_PUBLISH = '/api/v1/catalog/publish/'
    EXPECTED_CATS_ACTION_ACTIVE_CATALOGS = '/api/v1/titles/{title_code}/active_catalogs/{type}/'
    EXPECTED_CATS_PROCESSOR = 'dev-cats'

class PublishError(object):
    SERVER_ERROR = 'common.v1.internal-server-error'
    CLIENT_ERROR = 'common.v1.client-error'
    VALIDATION_ERROR = 'common.v1.validation-error'
    TITLE_NOT_FOUND = 'catalogs.v1.title-not-found'


class CatalogError(object):
    CATALOG_NOT_FOUND = 'catalogs.v1.catalog-not-found'
    TITLE_NOT_FOUND = 'catalogs.v1.title-not-found'
    CLIENT_ERROR = 'common.v1.client-error'
    CATALOG_TYPE_CONTEXT = 'Parameter must have a value among : main,coupon'
    ENTITY_NOT_FOUND = 'catalogs.v1.entity-not-found'


class CatalogStatus(object):
    ACTIVATED = 'ACTIVATED'
    TERMINATED = 'TERMINATED'
    FAILED = 'FAILED'
    PENDING = 'PENDING'
    IN_PROGRESS = 'IN_PROGRESS'

class EntityType(object):
    CURRENCY = 'CURRENCY'
    ENTITLEMENT = 'ENTITLEMENT'
    PRODUCT = 'PRODUCT'
    STOREFRONT = 'STOREFRONT'
    OVERRIDE = 'OVERRIDE'
    PROMOTION = 'PROMOTION'
    COUPON = 'COUPON'
    FILTER_PROPERTY = 'FILTER_PROPERTY'


class Contracts(object):
    COMMERCE_FETCH_STOREFRONT_CATEGORIES_V1 = 'commerce.fetch-storefront-categories.v1'
    COMMERCE_FETCH_STOREFRONT_CATEGORIES_V2 = 'commerce.fetch-storefront-categories.v2'
    COMMERCE_FETCH_FILTER_PROPERTIES_V1 = 'commerce.fetch-filter-properties.v1'
    COMMERCE_FETCH_CATALOG_CURRENCIES_V1 = 'commerce.fetch-catalog-currencies.v1'


class Metrics(object):
    MASTER_NODE_DESCRIPTION = 'Current master node id of the ignite cluster.'
    MASTER_NODE = 'master_of_cluster'


class TitleCode(object):
    NPTST_TITLE = 'ru.nptst'
    PREPARE_301 = 'ru.prepare_301'
    PREPARE_500 = 'ru.prepare_500'
    PREPARE_400 = 'ru.prepare_400'
    PREPARE_408 = 'ru.prepare_408'
    PREPARE_504 = 'ru.prepare_504'
    PREPARE_TIMEOUT = 'ru.prepare_TIMEOUT'

    FRANZ_200_FAILURE = 'ru.franz_200_fail'
    FRANZ_400_FAILURE = 'ru.franz_400'
    FRANZ_EMPTY_RESPONSE_FAILURE = 'ru.franz_empty'

    ACTIVATED_500 = 'ru.activated_500'
    ACTIVATED_400 = 'ru.activated_400'
    ACTIVATED_408 = 'ru.activated_408'

    SHARED_CURRENCY = 'ru.shared_currency'
    SHARED_PREMIUM = 'ru.shared_premium'

    PUBLISH_NEGATIVE = 'ru.publish_negative'
    PUBLISH_ORDER = 'ru.publish_order'
    PUBLISH_PREPARE = 'ru.prepare_big_response'
    PUBLISH_NEW_CATALOG = 'ru.publish_new_catalog'
    CATALOG_PUBLICATIONS = 'ru.catalog_publications'
    CATALOG_MIGRATION = 'ru.migration'

class Currency(object):
    SACOIN = 'sacoin'
    CREDITS = 'credits'

class TestCatalogPath(object):
    DOWNLOAD_PATH = 'tmp/downloaded_catalog/'
    ORIGINAL_PATH = 'tmp/original_catalog/'


class CatalogZIP(object):
    DEFAULT_CATALOG = 'test_catalog.zip'
    INVALID_FORMAT = 'catalog_invalid_format.zip'
    UPDATED_CATALOG = 'test_catalog_updated.zip'
    SHARED_CURRENCY_CATALOG = 'catalog_shared_currency.zip'
    SHARED_PREMIUM_CATALOG = 'catalog_shared_premium.zip'


class ChangeType(object):
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'


class EntitiesBy(object):
    ID = '807a7111-4fdc-4c0e-b062-e086bf7c3921'
    PRODUCT_ID = '78e75cf5-6cc8-46fa-a811-5d8e112f05b8'
    EXPECTED_TAG_ENTITLEMENT = 'barbarian_bundle_owner'
    EXPECTED_TAG_PRODUCT = 'barbarian_bundle'

class Tags(object):
    PREMIUM_EQUIPMENT = 'premium_equipment'
    BATTLE_PASS = 'battlePassAllowed'
    TEST = 'test'


class CatalogTypes(object):
    MAIN = 1
    COUPON = 2
    MAIN_TYPE = 'MAIN'
    COUPON_TYPE = 'COUPON'


class Regex(object):
    MAIN_CATALOG_CODE = '[a-z]*.*-MAIN-\d*'
    COUPON_CATALOG_CODE = '[a-z]*.*-COUPON-\d*'


class CatalogDiffError(object):
    ENTITY_TYPE = 'Parameter must have a value among : ' \
                  'currency,entitlement,product,storefront,override,promotion,coupon,filter_property'


class CategoryStatus(object):
    ACTIVE = 'active'
    EXPIRED = 'expired'
    WAITING_FOR_ACTIVATION = 'waiting_for_activation'


class ContractMessage(object):
    INVALID_DATA = 'Invalid request data'


class ContractError(object):
    COMMON_INTERNAL_SERVER_ERROR = 'common.v1.internal-server-error'
    COMMON_VALIDATION_ERROR = 'common.v1.validation-error'
    COMMERCE_BUSINESS_VALIDATION_ERROR = 'commerce.business-validation-error.v1'
    COMMERCE_CATALOG_ERROR = 'commerce.catalog-error.v1'
    COMMERCE_CATALOG_NOT_FOUND_ERROR = 'commerce.catalog-not-found.v1'
    COMMERCE_TITLE_NOT_FOUND_ERROR = 'commerce.title-not-found.v1'
    COMMERCE_STOREFRONT_NOT_FOUND_ERROR = 'commerce.storefront-not-found.v1'


class TitleId(object):
    SHARED_CURRENCY = '13'
    SHARED_PREMIUM = '4'
