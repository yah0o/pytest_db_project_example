import os
import random
import time
from collections import MutableMapping
from contextlib import suppress

from ulid2 import generate_ulid_as_base32
from waiting import wait as wait_lib

WAIT_TIMEOUT = int(os.environ.setdefault('TIMEOUT', '60'))


def wait(*args, **kwargs):
    """
    Wrapping 'wait()' method of 'waiting' library with default parameter values
    """
    params = {'timeout_seconds': WAIT_TIMEOUT,
              'sleep_seconds': (1, None)}
    params.update(kwargs)
    return wait_lib(*args, **params)


def random_id():
    return random.randint(1, 2147483647)


def ulid():
    # to exclude the same time ulid generation
    time.sleep(0.1)
    return generate_ulid_as_base32()


def delete_keys_from_dict(dictionary, keys):
    for key in keys:
        with suppress(KeyError):
            del dictionary[key]
    for value in dictionary.values():
        if isinstance(value, MutableMapping):
            delete_keys_from_dict(value, keys)


def remove_nested_element(element, fields_to_remove):
    if fields_to_remove:
        if type(fields_to_remove) is str:
            fields = fields_to_remove.split('.')
            if len(fields) > 1:
                remove_nested_element(element[fields[0]], ".".join(fields[1:len(fields)]))
            else:
                element.pop(fields[0])
        else:
            for i in fields_to_remove:
                element.pop(i)