# -*- coding: utf-8 -*-
"""
General purpose helpers.
"""
import hashlib
import random

from django.utils.translation import activate, deactivate


class Translator(object):
    """
    Helps getting strings in desired language. Example:

        with Translator('en'):
            s = ugettext("some string")
    """
    def __init__(self, language):
        self.language = language

    def __enter__(self):
        activate(self.language)

    def __exit__(self, type, value, traceback):
        deactivate()


def random_string(length):
    """
    Returns a random string of given length.
    """
    return hashlib.sha1(unicode(random.random())).hexdigest()[:length]
