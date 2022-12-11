import io
import json
import os
import re
import zipfile
from pathlib import Path
from string import Template

from hamcrest import equal_to, has_property, all_of
from hamcrest import has_entry, has_entries, empty, matches_regexp
from npqa_matchers.http import has_status_code
from npqa_matchers.jsonschema import has_valid_schema
from npqa_mock.wiremock.patterns import Request
from npqa_report import assert_that
from requests import codes
from waiting import wait

from np_cats_qa.constants import PublishStatus, CatalogStatus, SERVICE_REALM
from np_cats_qa.data.schemas import FAILED_RESPONSE
from np_cats_qa.helpers import wait, delete_keys_from_dict
from np_cats_qa.matchers import not_empty


def verify_catools_notification_sent(mock_steps, status, publish_id, catalog_code, reason=None):
    title = catalog_code.split('-')[0].split('.')[1]
    params = dict(
        catalog_code=catalog_code,
        status=status,
        reason=reason
    )
    headers = [{'name': 'toolscontext', 'value': '{{"environment":"{0}","title":"{1}"}}'.format(SERVICE_REALM, title)},
               {'name': 'x-auth-secret', 'value': 'test-secret_key'}]

    verify_wiremock_request(mock_steps, "/api/v1/catalog_publish/{}/set_status/".format(publish_id), "put_request.json",
                            params, ['reason'] if reason is None else [], 'PUT', headers=headers)


def verify_coupons_notification_sent(mock_steps, status, publish_id, catalog_code, reason=None):
    title = catalog_code.split('-')[0].split('.')[1]
    params = dict(
        catalog_code=catalog_code,
        status=status,
        reason=reason
    )
    headers = [{'name': 'toolscontext', 'value': '{{"environment":"{0}","title":"{1}"}}'.format(SERVICE_REALM, title)}]

    verify_wiremock_request(mock_steps, "/api/v1/catalog_publish/{}/set_status/".format(publish_id), "put_request.json",
                            params, ['reason'] if reason is None else [], 'PUT', headers=headers)


def verify_common_notification_sent(mock_steps, status, publish_id, reason=None):
    params = dict(
        status=status,
        reason=reason
    )

    verify_wiremock_request(mock_steps, "/api/v1/catalog_publish/{}/set_status/".format(publish_id), "put_request.json",
                            params, ['reason'] if reason is None else [], 'PUT')


def has_valid_catalog_publications_info(status, publish_id, catalog_code, failure_reason=None):
    matchers = [
        has_entries(status=status,
                    created_at=not_empty(),
                    publish_id=publish_id,
                    catalog_code=catalog_code,
                    tracking_id=not_empty())
    ]
    if status in (CatalogStatus.ACTIVATED, CatalogStatus.TERMINATED):
        matchers.append(has_entry('activated_at', not_empty()))
    if status == CatalogStatus.TERMINATED:
        matchers.append(has_entry('terminated_at', not_empty()))
    if status == CatalogStatus.FAILED and failure_reason is not None:
        matchers.append(has_entry('failure', equal_to(failure_reason)))
    if status not in (CatalogStatus.IN_PROGRESS, CatalogStatus.PENDING):
        matchers.append(has_entry('finished_at', not_empty()))
    return all_of(*matchers)


def verify_prepare_method_called(mock_steps, catalog_code):
    params = dict(
        catalog_code=catalog_code
    )
    verify_wiremock_request(mock_steps, "/catalog/api/v1/prepare", "prepare_activated_request.json", params, )


def verify_prepare_method_called_n_times(mock_steps, catalog_code, nTimes):
    params = dict(
        catalog_code=catalog_code
    )
    verify_wiremock_request(mock_steps, "/catalog/api/v1/prepare", "prepare_activated_request.json", params, )
    assert_that(len(get_request(mock_steps, "/catalog/api/v1/prepare", 'POST')), equal_to(nTimes))


def verify_franz_event_sent(mock_steps, catalog_code, title_code):
    params = dict(
        catalog_code=catalog_code,
        title_code=title_code
    )
    verify_wiremock_request(mock_steps,
                            "/streams/api/v1/pushEvent/{}.np.catalogs.catalog_publish_v1".format(SERVICE_REALM),
                            "np.catalogs.catalog_publish_v1.json", params, ignore_params=["header", "published_at"])


def verify_activated_method_called(mock_steps, catalog_code):
    params = dict(
        catalog_code=catalog_code
    )
    verify_wiremock_request(mock_steps, "/catalog/api/v1/activated", "prepare_activated_request.json", params)


def get_request(mock_steps, request_url, request_method='POST'):
    request = Request() \
        .with_method(request_method) \
        .with_url(url=request_url)
    return mock_steps.journal_get_requests_by_pattern(request)


def findMetricValue(is_http, label, flow=None, critical_service=None):
    response = is_http.cats.metrics()
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected status_code')

    assert_that(response.text, matches_regexp(label), 'resp has no {} healthcheck metric'.format(label))
    if critical_service:
        node_metric = re.findall('%s{app=\"cats\",exception=\"\w*\",node_order=\"\d\",'
                                 'realm=\"%s\",status=\"\w+\",type=\"\w+\",}\s\d+\.\d+' % (label, SERVICE_REALM),
                                 response.text)
    else:
        node_metric = re.findall('%s{app=\"cats\",node_order=\"\d\",realm=\"%s\",}\s\d+\.\d+' % (label, SERVICE_REALM),
                                 response.text)
    return re.findall('\d+\.\d+', node_metric[0])


def findVersionMetricValue(is_http, label):
    response = is_http.cats.metrics()
    assert_that(response, has_status_code(codes.ok), allure_name='response has expected status_code')

    assert_that(response.text, matches_regexp(label), 'resp has no {} metric'.format(label))
    node_metric = re.findall(
        'app_version{app=\"cats\",node_order=\"\d\",realm=\"%s\",version=\".+\",}\s\d+\.\d+' % (SERVICE_REALM),
        response.text)

    return re.findall('version=\"(.+)\"', node_metric[0])


def verify_wiremock_request(mock_steps, request_url, template_file, template_params, ignore_params=[],
                            request_method='POST', request_json_schema=None, headers=None):
    wait(lambda: len(get_request(mock_steps, request_url, request_method)) > 0,
         waiting_for='Appropriate request',
         timeout_seconds=30,
         sleep_seconds=0.1)

    wiremock_requests_found = get_request(mock_steps, request_url, request_method)

    wiremock_request_url = wiremock_requests_found[0]["url"]
    assert_that(wiremock_request_url, equal_to(request_url))

    wiremock_request_body = wiremock_requests_found[0]["body"]

    if headers:
        request_headers = wiremock_requests_found[0]["headers"]
        for header in headers:
            assert_that(request_headers[header['name']], equal_to(header['value']), allure_name='Should contain header')

    if request_json_schema is not None:
        assert_that(wiremock_request_body, has_valid_schema(request_json_schema),
                    'Different request to JSON schema is expected (schema is {})'.format(request_json_schema))

    data_folder = Path(os.getcwd().split('src')[0])
    file = data_folder / ("src/db_prj_qa/steps/mock/request_templates/" + template_file)
    with open(file) as f:
        request_template = Template(f.read()).substitute(template_params)
    wiremock_expected_request_body = json.loads(request_template)

    if ignore_params:
        delete_keys_from_dict(wiremock_request_body, ignore_params)
        delete_keys_from_dict(wiremock_expected_request_body, ignore_params)

    assert_that(wiremock_request_body, equal_to(wiremock_expected_request_body),
                'Different request to wiremock is expected (template is {})'.format(template_file))


def verify_failed_response(response, error_code):
    response = response.json()
    assert_that(response, has_valid_schema(FAILED_RESPONSE), allure_name='error response has correct schema')
    assert_that(response['error'], has_entry('code', error_code), allure_name='response has expected error_code')


def wait_until_task_finished_in_db(is_db, publish_id):
    wait(lambda: is_db.get_publish_task_status(publish_id) in [PublishStatus.COMPLETED, PublishStatus.FAILED],
         waiting_for='Status COMPLETED or FAILED',
         timeout_seconds=30,
         sleep_seconds=0.1)


def verify_publish_completed_with_status_in_db(is_db, publish_id, status):
    # waiting FAILED or COMPLETED status to do not fail with Timeout issue
    wait(lambda: is_db.get_publish_task_status(publish_id) in [PublishStatus.COMPLETED, PublishStatus.FAILED],
         waiting_for='Status COMPLETED or FAILED',
         timeout_seconds=30,
         sleep_seconds=0.1)
    assert_that(is_db.get_publish_task_status(publish_id), equal_to(status), allure_name='must be equal status')


def verify_publish_status_in_db(is_db, publish_id, status):
    wait(lambda: is_db.get_publish_task_status(publish_id) == status,
         waiting_for='Status was changed to %s' % status,
         timeout_seconds=30,
         sleep_seconds=0.1)


def verify_publish_states_in_db(is_db, catalog_publish_id):
    publish_statuses = [PublishStatus.PENDING, PublishStatus.IN_PROGRESS, PublishStatus.COMPLETED]
    for status in publish_statuses:
        verify_publish_status_in_db(is_db, catalog_publish_id, status)


def has_valid_catalog_publish_info(status, publish_id, catalog_code):
    matchers = [
        has_entries(status=status,
                    created_at=not_empty(),
                    publish_id=publish_id,
                    catalog_code=catalog_code)
    ]
    if status in (CatalogStatus.ACTIVATED, CatalogStatus.TERMINATED):
        matchers.append(has_entry('activated_at', not_empty()))
    if status == CatalogStatus.TERMINATED:
        matchers.append(has_entry('terminated_at', not_empty()))
    if status == CatalogStatus.FAILED:
        matchers.append(has_entry('failure', not_empty()))
    if status not in (CatalogStatus.IN_PROGRESS, CatalogStatus.PENDING):
        matchers.append(has_entry('finished_at', not_empty()))
    return all_of(*matchers)


def verify_publish_states_failed(is_db, catalog_publish_id):
    publish_statuses = [PublishStatus.PENDING, PublishStatus.IN_PROGRESS, PublishStatus.FAILED]
    for status in publish_statuses:
        verify_publish_status_in_db(is_db, catalog_publish_id, status)


def verify_terminated_catalog_in_db(is_db, catalog_code):
    wait(lambda: is_db.get_catalog_by_catalog_code(catalog_code)['terminated_at'] is not None,
         waiting_for='terminated_at field has set ',
         timeout_seconds=30,
         sleep_seconds=0.1)


def compare_downloaded_and_original_catalogs(mock_http, catalog, catalog_file, download_path, original_path):
    catalog_instances = [
        {'file': 'currencies.json', 'key': 'currency_code'},
        {'file': 'entitlements.json', 'key': 'entitlement_code'},
        {'file': 'products.json', 'key': 'code'},
        {'file': 'storefronts.json', 'key': 'code'},
        {'file': 'overrides.json', 'key': 'code'},
        {'file': 'promotions.json', 'key': 'code'}
    ]

    catalog_zipped = zipfile.ZipFile(io.BytesIO(catalog))
    catalog_zipped.extractall(download_path)

    mock_http.extract_catalog_by_catalog_code_to(catalog_file=catalog_file, extract_path=original_path)

    for items in catalog_instances:
        with open(download_path + items['file'], 'r+', encoding="utf-8") as downloaded_file:
            downloaded_catalog = sorted(json.load(downloaded_file), key=lambda k: k[items['key']])[0]

        with open(original_path + items['file'], 'r+', encoding="utf-8") as original_file:
            original_catalog = sorted(json.load(original_file), key=lambda k: k[items['key']])[0]

        assert_that([key for key in downloaded_catalog if downloaded_catalog[key] != original_catalog[key]],
                    empty(), allure_name='Catalog entities are same')


def verify_audit(response, clickhouse_client,
                 request_tracking_id=None, request_emitter_id=None,
                 expected_action=None, expected_processor=None):
    response_tracking_id = None

    # capi response does not have headers attribute
    if hasattr(response, 'headers'):
        response_tracking_id = response.headers['x-np-tracking-id']

    if (request_tracking_id is not None):
        # capi response does not have headers attribute
        if not hasattr(response, 'headers'):
            response_tracking_id = request_tracking_id
        else:
            assert_that(response_tracking_id, equal_to(request_tracking_id),
                        'response x-np-tracking-id does not matches to request')

    assert_that(response_tracking_id, not_empty(), 'response tracking_id is empty')

    clickhouse_get_log = lambda: clickhouse_client.get_log(where='tracking=\'{}\''.format(response_tracking_id))

    wait(
        clickhouse_get_log,
        timeout_seconds=30, sleep_seconds=1
    )
    clickhouse_record = clickhouse_get_log()[0]
    matchers = []
    matchers.append(has_property('event_id', not_empty()))
    matchers.append(has_property('created_at', not_empty()))
    matchers.append(has_property('tracking_id', equal_to(response_tracking_id)))
    if expected_action is not None:
        matchers.append(has_property('action', equal_to(expected_action)))
    if expected_processor is not None:
        matchers.append(has_property('processor', equal_to(expected_processor)))
    if request_emitter_id is not None:
        matchers.append(has_property('requester', equal_to(request_emitter_id)))

    assert_that(clickhouse_record, all_of(*matchers))
