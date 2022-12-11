import random
import string
import time
from datetime import datetime


def generate_title_code():
    return 'ru.' + ''.join(random.choices(string.ascii_lowercase, k=5))


def generate_catalog_code(title_code):
    return title_code + '-MAIN-' + str(round(time.time()))


def generate_catalog_code_next(title_code):
    return title_code + '-MAIN-' + str(round(time.time()) + 1)


def generate_coupon_catalog_code(title_code):
    return title_code + '-COUPON-' + str(round(time.time()))


def generate_coupon_catalog_code_next(title_code):
    return title_code + '-COUPON-' + str(round(time.time()) + 1)


def generate_catalog_url(yaml_config, catalog_zip):
    return yaml_config.data.CATALOG_DOMAIN + '/' + catalog_zip


def generate_catalog_code_with_random_title_code(title_code=generate_title_code()):
    return generate_catalog_code(title_code)


def generate_string_datetime():
    time.sleep(0.002)
    return "{}Z".format(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3])
