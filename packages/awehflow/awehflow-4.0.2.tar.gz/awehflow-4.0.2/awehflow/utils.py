import datetime
import random
import string

import pytz


def merge_dicts(a, b, path=None):
    """merges b into a"""
    if path is None:
        path = []
    for key in b:
        if key in a and (isinstance(a[key], dict) and isinstance(b[key], dict)):
            merge_dicts(a[key], b[key], path + [str(key)])
        else:
            a[key] = b[key]
    return a


def random_string(string_length=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(string_length))


def uniquify_name(name):
    return "{name}_{random_string}".format(
        name=name,
        random_string=random_string(string_length=6)
    )


def utc_now(): #pragma: no cover
    return pytz.utc.localize(datetime.datetime.utcnow())


class JobStatus:
    RUNNING = 'running'
    FAILURE = 'failure'
    SUCCESS = 'success'
