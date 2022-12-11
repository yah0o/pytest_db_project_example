from datetime import datetime, timedelta

import allure
import pytest
from hamcrest import equal_to
from npqa_report import assert_that

from np_cats_qa.data.schemas import schemas
from np_cats_qa.helpers import wait
from np_cats_qa.verifications import findMetricValue


@pytest.fixture(autouse=True)
def clear(is_http, is_db):
    is_db.delete_publish_task(schemas.hangingTask()['id'])
    yield
    is_db.delete_publish_task(schemas.hangingTask()['id'])


@allure.feature('cats')
@allure.story('alerts')
def test_hanging_task(is_http, is_db):
    hanging_task_count = findMetricValue(is_http, 'hanging_tasks')
    assert_that(hanging_task_count[0], equal_to('0.0'), 'expected 0 hanging tasks')
    hanging_task = {**schemas.hangingTask(), 'created_at': datetime.utcnow() - timedelta(seconds=60)}
    is_db.add_publish_task(hanging_task)
    wait(lambda: findMetricValue(is_http, 'hanging_tasks')[0] == '1.0',
         waiting_for='New hanging task will appear',
         timeout_seconds=30,
         sleep_seconds=0.1)
