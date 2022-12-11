from npqa_http import HttpClient
from npqa_report import step
from ulid2 import generate_ulid_as_base32


def get_headers(tracking_id=None, emitter_id=None):
    headers = {}
    if emitter_id is not None:
        headers.update({"x-np-emitter-id": emitter_id})
    if tracking_id is not None:
        headers.update({"x-np-tracking-id": tracking_id})
    return headers


class CatalogServiceSteps(object):
    def __init__(self, base_url):
        default_headers = {
            'Content-type': 'application/json',
            'x-np-tracking-id': generate_ulid_as_base32()
        }
        self.client = HttpClient(base_url, default_headers=default_headers, raise_for_status=False)

    @step
    def ping(self):
        url = '/ping'
        return self.client.get(url)

    @step
    def healthy(self):
        url = '/healthy'
        return self.client.get(url)

    @step
    def metrics(self):
        url = '/metrics'
        return self.client.get(url)

    @step
    def swagger(self):
        url = '/swagger'
        return self.client.get(url)

    @step
    def ignite_info(self):
        url = '/ignite/info'
        return self.client.get(url)

    @step
    def publish(self, catalog_url=None, catalog_code=None, publish_id=None, data=None, tracking_id=None,
                emitter_id=None):
        url = '/api/v1/catalog/publish'
        if data is None:
            data = dict(
                url=catalog_url,
                catalog_code=catalog_code,
                publish_id=publish_id
            )

        response = self.client.post(url, json=data, headers=get_headers(tracking_id=tracking_id, emitter_id=emitter_id))
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def publisher_catalog_publish(self, catalog_url=None, tool_name=None, catalog_code=None, publish_id=None,
                                  data=None):
        url = '/api/v1/{tool_name}/catalog/publish'.format(tool_name=tool_name)
        if data is None:
            data = dict(
                url=catalog_url,
                catalog_code=catalog_code,
                publish_id=publish_id
            )
        response = self.client.post(url, json=data)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def v2_catalog_publish(self, catalog_url=None, tool_name=None, title_code=None, catalog_type=None, publish_id=None,
                           data=None):
        url = '/api/v2/{tool_name}/catalog/publish'.format(tool_name=tool_name)
        if data is None:
            data = dict(
                url=catalog_url,
                title_code=title_code,
                catalog_type=catalog_type,
                publish_id=publish_id
            )
        response = self.client.post(url, json=data)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def v2_catalog_republish(self, tool_name=None, catalog_code=None, publish_id=None,
                             data=None):
        url = '/api/v2/{tool_name}/catalog/republish'.format(tool_name=tool_name)
        if data is None:
            data = dict(
                catalog_code=catalog_code,
                publish_id=publish_id
            )
        response = self.client.post(url, json=data)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def migrate(self, catalog_url, catalog_code, activated_at, terminated_at=None):
        url = '/api/v1/catalog/migrate'
        data = dict(
            url=catalog_url,
            catalog_code=catalog_code,
            activated_at=activated_at,
            terminated_at=terminated_at
        )
        response = self.client.post(url, json=data)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_active_catalog_by_title_code(self, title_code, type, tracking_id=None, emitter_id=None):
        url = "/api/v1/titles/{title_code}/active_catalogs/{type}".format(title_code=title_code, type=type)
        response = self.client.get(url, headers=get_headers(tracking_id=tracking_id, emitter_id=emitter_id))
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_active_catalogs_by_title_code(self, title_code, type=None):
        url = "/api/v1/titles/{title_code}/active_catalogs".format(title_code=title_code)
        if type is not None:
            url += "?type={type}".format(type=type)
        response = self.client.get(url)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_active_catalog(self, type=None, headers=None):
        url = "/api/v1/titles/active_catalogs"
        if type is not None:
            url += "?type={type}".format(type=type)
        response = self.client.get(url, headers=headers)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_catalog_publish_status(self, publish_id):
        url = "/api/v1/catalog/publish/{publish_id}/status".format(publish_id=publish_id)
        response = self.client.get(url)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_entities_by_type_and_title_code(self, title_code, entity_type, tags=None, language=None):
        url = "/api/v1/titles/{title_code}/entities/{entity_type}".format(title_code=title_code,
                                                                          entity_type=entity_type)
        if tags or language is not None:
            params = {
                'tags': tags,
                'language': language
            }
            response = self.client.get(url, params=params)
        else:
            response = self.client.get(url)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_entities_by_type_and_catalog_code(self, catalog_code, entity_type, language=None):
        url = "/api/v1/catalogs/{catalog_code}/entities/{entity_type}".format(catalog_code=catalog_code,
                                                                              entity_type=entity_type)
        if language is not None:
            params = {
                'language': language
            }
            response = self.client.get(url, params=params)
        else:
            response = self.client.get(url)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_product_with_applied_promo(self, catalog_code, product_code, promo_code, storefront_code):
        url = "/api/v1/catalog/{catalog_code}/product/{product_code}" \
              "?promo_code={promo_code}&storefront_code={storefront_code}".format(catalog_code=catalog_code,
                                                                                  product_code=product_code,
                                                                                  promo_code=promo_code,
                                                                                  storefront_code=storefront_code
                                                                                  )
        response = self.client.get(url)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_initial_diff_by_type_and_catalog_code(self, destination_catalog_code, entity_type,
                                                  fields=None, last_id=None, limit=None):
        url = "/api/v1/catalogs/{destination_catalog_code}/entities/{entity_type}/diff/initial".format(
            destination_catalog_code=destination_catalog_code,
            entity_type=entity_type
        )
        params = {
            'fields': fields,
            'last_id': last_id,
            'limit': limit
        }
        response = self.client.get(url, params=params)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_diff_by_type_and_catalog_code(self, destination_catalog_code, entity_type, source_catalog_code,
                                          fields=None, last_id=None, limit=None):
        url = "/api/v1/catalogs/{destination_catalog_code}/entities/{entity_type}/diff/{source_catalog_code}".format(
            destination_catalog_code=destination_catalog_code,
            entity_type=entity_type,
            source_catalog_code=source_catalog_code
        )
        params = {
            'fields': fields,
            'last_id': last_id,
            'limit': limit
        }
        response = self.client.get(url, params=params)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_entities_by_type_code_and_title_code(self, title_code, entity_type, code, language=None):
        url = "/api/v1/titles/{title_code}/entities/{entity_type}/{code}".format(title_code=title_code,
                                                                                 entity_type=entity_type,
                                                                                 code=code)

        if language is not None:
            params = {
                'language': language
            }
            response = self.client.get(url, params=params)
        else:
            response = self.client.get(url)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_catalog_by_code(self, catalog_code):
        url = "/api/v1/catalogs/{catalog_code}".format(catalog_code=catalog_code)
        response = self.client.get(url)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_entitiy_by_id(self, entity_id, language=None):
        url = "/api/v1/entities/{entity_id}".format(entity_id=entity_id)
        if language is not None:
            params = {
                'language': language
            }
            response = self.client.get(url, params=params)
        else:
            response = self.client.get(url)

        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_entities_by_type_code_and_catalog_code(self, catalog_code, entity_type, code):
        url = "/api/v1/catalogs/{catalog_code}/entities/{entity_type}/{code}".format(catalog_code=catalog_code,
                                                                                     entity_type=entity_type,
                                                                                     code=code)
        response = self.client.get(url)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_catalog_publications(self, title_code, limit=None):
        url = "/api/v1/titles/{title_code}/catalog/publications".format(title_code=title_code)
        params = {
            'limit': limit
        }
        response = self.client.get(url, params=params)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_currencies(self):
        url = "/api/v1/currencies"
        response = self.client.get(url)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_titles_by_entity_id(self, id):
        url = "/api/v1/entities/{id}/titles".format(id=id)
        response = self.client.get(url)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_entities_by_id(self, id):
        url = "/api/v1/entities/{id}".format(id=id)
        response = self.client.get(url)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_catalogs_by_entity_id(self, id):
        url = "/api/v1/entities/{id}/catalogs".format(id=id)
        response = self.client.get(url)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_entities_by_code(self, code):
        url = "/api/v1/entities/{code}/list".format(code=code)
        response = self.client.get(url)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_currencies_map(self):
        url = "/api/v1/currencies/map"
        response = self.client.get(url)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_entitlements(self):
        url = "/api/v1/entitlements"
        response = self.client.get(url)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def get_entitlements_map(self):
        url = "/api/v1/entitlements/map"
        response = self.client.get(url)
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def delete_active_catalog_by_title_code(self, title_code, type, tracking_id=None, emitter_id=None):
        url = "/api/v1/titles/{title_code}/active_catalogs/{type}".format(title_code=title_code, type=type)
        response = self.client.delete(url, headers=get_headers(tracking_id=tracking_id, emitter_id=emitter_id))
        assert 'x-np-tracking-id' in response.headers
        return response

    @step
    def update_titles(self):
        url = "/api/v1/titles/update"
        response = self.client.get(url)
        assert 'x-np-tracking-id' in response.headers
        return response
