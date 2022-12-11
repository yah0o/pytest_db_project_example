import shutil

import pytest

from np_cats_qa.constants import EntitiesBy
from np_cats_qa.data_generators import generate_catalog_code, generate_coupon_catalog_code, \
    generate_catalog_code_next, generate_coupon_catalog_code_next
from np_cats_qa.helpers import random_id, ulid
from np_cats_qa.steps import CatalogServiceHttpSteps
from np_cats_qa.steps.capi import CapiSteps
from np_cats_qa.steps.db.cats import CatalogServiceDBSteps
from np_cats_qa.steps.mock.steps import CatalogServiceMockSteps, WiremockHttpSteps
from tests import load_capi_from_artifactory_and_path
from paudit_qa.clients import ClickHouseClient


@pytest.fixture(scope='session')
def is_http(yaml_config):
    base_url = 'http://{host}:{port}'.format(**yaml_config.cats.http)
    return CatalogServiceHttpSteps(base_url)


@pytest.fixture(scope='session')
def is_db(yaml_config):
    db_url = 'postgres://{user}:{password}@{host}:{port}/{db}'.format(**yaml_config.cats.db)
    return CatalogServiceDBSteps(db_url)


@pytest.fixture
def mock_steps(yaml_config):
    """
    init app mock steps
    """
    return CatalogServiceMockSteps(**yaml_config.wiremock)


@pytest.fixture
def mock_http(yaml_config):
    base_url = 'http://{host}:{port}'.format(**yaml_config.wiremock)
    return WiremockHttpSteps(base_url)


@pytest.fixture
def title_code(yaml_config):
    return yaml_config.data.TITLE_CODE


@pytest.fixture
def coupon_title_code(yaml_config):
    return yaml_config.data.TITLE_CODE


@pytest.fixture
def wowp_title_code(yaml_config):
    return yaml_config.data.WOWP_TITLE_CODE


@pytest.fixture
def wows_title_code(yaml_config):
    return yaml_config.data.WOWS_TITLE_CODE


@pytest.fixture
def catalog_url(yaml_config):
    return yaml_config.data.CATALOG_DOMAIN + '/' + yaml_config.data.DEFAULT_CATALOG


@pytest.fixture
def main_catalog_url(yaml_config):
    return yaml_config.data.CATALOG_DOMAIN + '/' + yaml_config.data.DEFAULT_CATALOG


@pytest.fixture
def coupon_catalog_url(yaml_config):
    return yaml_config.data.CATALOG_DOMAIN + '/' + yaml_config.data.DEFAULT_COUPON_CATALOG


@pytest.fixture
def catalog_domain(yaml_config):
    return yaml_config.data.CATALOG_DOMAIN


@pytest.fixture(scope='session')
def clickhouse_client(yaml_config):
    return ClickHouseClient(host='localhost')


@pytest.fixture
def not_exist_coupon_catalog_url(yaml_config):
    return yaml_config.data.CATALOG_DOMAIN + '/' + yaml_config.data.NOT_EXIST_COUPON_CATALOG


@pytest.fixture
def catalog_publish_id():
    return random_id()


@pytest.fixture
def publish_id():
    return ulid()


@pytest.fixture
def catalog_code(yaml_config):
    return generate_catalog_code(yaml_config.data.TITLE_CODE)


@pytest.fixture
def catalog_code_next(yaml_config):
    return generate_catalog_code_next(yaml_config.data.TITLE_CODE)


@pytest.fixture
def main_catalog_code(yaml_config):
    return generate_catalog_code(yaml_config.data.TITLE_CODE)


@pytest.fixture
def wowp_title_catalog_code(yaml_config):
    return generate_catalog_code(yaml_config.data.WOWP_TITLE_CODE)


@pytest.fixture
def wowp_title_catalog_code_next(yaml_config):
    return generate_catalog_code_next(yaml_config.data.WOWP_TITLE_CODE)


@pytest.fixture
def coupon_catalog_code(yaml_config):
    return generate_coupon_catalog_code(yaml_config.data.TITLE_CODE)


@pytest.fixture
def coupon_catalog_code_next(yaml_config):
    return generate_coupon_catalog_code_next(yaml_config.data.TITLE_CODE)


@pytest.fixture
def catalog_id():
    return random_id()


@pytest.fixture
def title_not_exist(yaml_config):
    return yaml_config.data.TITLE_NOT_EXIST


@pytest.fixture
def title_inactive(yaml_config):
    return yaml_config.data.TITLE_INACTIVE


@pytest.fixture
def title_for_failed_publish(yaml_config):
    return yaml_config.data.TITLE_FOR_FAILED_PUBLISH


@pytest.fixture
def publish_catalog(is_http, catalog_url, catalog_code, publish_id):
    return is_http.cats.publish(catalog_url, catalog_code, publish_id)


@pytest.fixture
def clear_tmp():
    yield
    shutil.rmtree('tmp')


@pytest.fixture
def get_active_catalog_code_by_title_code(is_http, title_code):
    return is_http.cats.get_active_catalog_by_title_code(title_code, 'MAIN').json()['catalog_code']


@pytest.fixture
def update_titles(is_http):
    return is_http.cats.update_titles()


@pytest.fixture(scope='session')
def contracts(yaml_config):
    return load_capi_from_artifactory_and_path(
        yaml_config.cats.capi.stable_capi,
        yaml_config.cats.capi.unstable_capi,
        yaml_config.cats.capi.draft_capi_path
    )


@pytest.fixture(scope='session')
def capi_client_emitter_id(yaml_config):
    return yaml_config.cats.capi.client_emitter_id


@pytest.fixture(scope='session')
def capi(yaml_config, contracts, request):
    return CapiSteps(
        request,
        yaml_config.cats.capi.client_emitter_id,
        'amqp://{username}:{password}@{host}:{port}/{vhost}'.format(**yaml_config.cats.capi.rabbit),
        contracts
    )
