import uuid


def entity():
    schema = {
        'entitlement_id': str(uuid.uuid4()),
        'entitlement_code': 'entitlement_test_code_1',
        'metadata': {
            'test_field': 'test_value_1',
            'wot': {
                'short_name': {
                    'data': {
                        'en': 'Scorpion',
                        'ru': 'Скорпион',
                        'zh_cn': 'M56 蝎式',
                        'zh_sg': 'Scorpion',
                        'zh_tw': 'Scorpion',
                        'value': ''
                    },
                    '@type': 'LocString'
                }
            }
        }
    }
    return schema


def storefront():
    schema = {
        'storefront_id': str(uuid.uuid4()),
        'code': 'storefront_test_code_1',
        'metadata': {
            'test_field': 'test_value_1',
            'wot': {
                'short_name': {
                    'data': {
                        'de': 'Test_meta_de',
                        'en': 'Test_meta_en',
                        'fr': 'Test_meta_fr',
                        'ru': 'Test_meta_ru',
                        'value': ''
                    },
                    '@type': 'LocString'
                }
            }
        },
        'categories': {
            'category_test_1': {
                'order': 1,
                'parent': None,
                'metadata': {
                    'name': {
                      'data': {
                        'de': 'Test_category_de',
                        'en': 'Test_category_en',
                        'fr': 'Test_category_fr',
                        'ru': 'Test_category_ru'
                      },
                      '@type': 'LocString'
                    }
                }
            }
        }
    }
    return schema


def fields():
    schema = {
        "extra_field_1": "extra_field_1_value",
        "extra_field_2": "extra_field_2_value",
    }
    return schema

def hangingTask():
    return {
        'id': '01E5YTYSSSP2VNV8K164SPJ1B7',
        'title_id': -1, # to do not have intersection with other titles
        'catalog_code': 'cat_code',
        'publisher': 'catool',
        'status': 'PENDING',
        'tracking_id': '01E5Z1AV6DBKMJTATANK7TP3HK',
        'url': 'http://wiremock:8080/test_catalog.zip',
        'node': '43ae6fb0-6841-4cff-a6f3-f4a81dcefc16'
    }
