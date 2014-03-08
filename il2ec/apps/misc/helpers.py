# -*- coding: utf-8 -*-
"""
General purpose helpers.
"""
import hashlib
import random

from django.utils import timezone


def random_string(length):
    """
    Returns a random string of given length.
    """
    return hashlib.sha1(unicode(random.random())).hexdigest()[:length]


def current_time_hash():
    return hashlib.md5(timezone.now().isoformat()).hexdigest()
