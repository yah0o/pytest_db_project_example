import io
import json
import os
import zipfile
from pathlib import Path

import requests
from npqa_http import HttpClient
from npqa_mock.wiremock import WiremockClient, Stub
from npqa_mock.wiremock.client import Urls
from npqa_mock.wiremock.misc import process_body
from npqa_mock.wiremock.patterns import Request, Response
from npqa_report.decorators import step

from np_cats_qa.constants import CatalogZIP


class CatalogServiceMockSteps(object):
    def __init__(self, host, port):
        self.client = CustomWiremockClient(host, port)

    @step
    def setup_prepare(self, catalog_code, body):
        request = Request() \
            .with_method('POST') \
            .with_url(url='/catalog/api/v1/prepare') \
            .with_body([("matchesJsonPath", "$..[?(@.catalog_code=='{}')]".format(catalog_code))])

        response = Response() \
            .with_status(200) \
            .with_body(body, is_json=True) \
            .with_header('Content-Type', 'application/json')

        stub = Stub().when(request).reply(response)
        self.client.create_stub(stub)
        return stub

    @step
    def journal_get_all_requests(self):
        return self.client.get_all_requests()

    @step
    def journal_get_requests_by_pattern(self, request_pattern):
        return self.client.get_requests_by_pattern(request_pattern)

    @step
    def journal_clear_history(self):
        return self.client.clear_history()


class CustomWiremockClient(WiremockClient):

    def __get_base_url(self):
        return 'http://%s:%s' % (self.host, self.port)

    def get_requests_by_pattern(self, request_pattern):
        response = requests.post(self.__get_base_url() + Urls.REQUESTS + 'find',
                                 json=request_pattern.as_dict()['request'])
        # process_body(rq) instead of process_body(rq['request'])
        return [process_body(rq) for rq in json.loads(response.content)['requests']]


class WiremockHttpSteps(object):

    def __init__(self, base_url):
        self.client = HttpClient(base_url)
        self.mock_client = WiremockClient(base_url)

    @step
    def extract_catalog_by_catalog_code_to(self, extract_path, catalog_file=CatalogZIP.DEFAULT_CATALOG):
        response = self.client.get("/{catalog_file}".format(catalog_file=catalog_file))
        catalog_zipped = zipfile.ZipFile(io.BytesIO(response.content))
        catalog_zipped.extractall(extract_path)
