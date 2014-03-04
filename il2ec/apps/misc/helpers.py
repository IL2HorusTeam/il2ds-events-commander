# -*- coding: utf-8 -*-
"""
General purpose helpers.
"""
import hashlib
import random


def random_string(length):
    """
    Returns a random string of given length.
    """
    return hashlib.sha1(unicode(random.random())).hexdigest()[:length]
