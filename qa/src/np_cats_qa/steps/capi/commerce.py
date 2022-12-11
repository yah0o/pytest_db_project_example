from capi_lib_python import Client
from np_cats_qa.constants import Contracts
from npqa_report import step

from np_cats_qa.helpers import remove_nested_element


class CommerceCapiSteps(object):
    def __init__(self, request, app_id, amqp_url, contracts):
        self.client = Client(app_id, amqp_url=amqp_url, contracts=contracts)
        request.addfinalizer(self.client.close)

    @step
    def fetch_storefront_categories_v1(self, title_code, storefront=None, tracking_id=None, language=None, activation_statuses=None,
                                       fields_to_remove=None):

        body = dict(
            title_code=title_code
        )

        if storefront is not None:
            body.update({"storefront": storefront})
        if language is not None:
            body.update({"language": language})
        if activation_statuses is not None:
            body.update({"activation_statuses": activation_statuses})

        remove_nested_element(body, fields_to_remove)

        context = None
        if tracking_id is not None:
            context = {'tracking_id': tracking_id}

        try:
            return self.client.call(
                Contracts.COMMERCE_FETCH_STOREFRONT_CATEGORIES_V1,
                body,
                validate=True,
                context=context
            )
        except Exception as e:
            return e

    @step
    def fetch_storefront_categories_v2(self, title_code, storefront=None, tracking_id=None, language=None, activation_statuses=None,
        fields_to_remove=None):

        body = dict(
            title_code=title_code
        )

        if storefront is not None:
            body.update({"storefront": storefront})
        if language is not None:
            body.update({"language": language})
        if activation_statuses is not None:
            body.update({"activation_statuses": activation_statuses})

        remove_nested_element(body, fields_to_remove)

        context = None
        if tracking_id is not None:
            context = {'tracking_id': tracking_id}

        try:
            return self.client.call(
                Contracts.COMMERCE_FETCH_STOREFRONT_CATEGORIES_V2,
                body,
                validate=True,
                context=context
            )
        except Exception as e:
            return e

    @step
    def fetch_filter_properties_v1(self, title_code, language=None, fields_to_remove=None):

        body = dict(
            title_code=title_code
        )

        if language is not None:
            body.update({"language": language})

        remove_nested_element(body, fields_to_remove)

        try:
            return self.client.call(
                Contracts.COMMERCE_FETCH_FILTER_PROPERTIES_V1,
                body,
                validate=True
            )
        except Exception as e:
            return e

    @step
    def fetch_catalog_currencies_v1(self, title_code, currency_codes=None, etag=None):

        body = dict(
            title_code=title_code
        )

        if currency_codes is not None:
            body.update({"currency_codes": currency_codes})
        if etag is not None:
            body.update({"etag": etag})

        try:
            return self.client.call(
                Contracts.COMMERCE_FETCH_CATALOG_CURRENCIES_V1,
                body,
                validate=True
            )
        except Exception as e:
            return e