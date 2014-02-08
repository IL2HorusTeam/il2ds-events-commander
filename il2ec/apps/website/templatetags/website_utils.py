# -*- coding: utf-8 -*-
"""
Different helper template tags.
"""
from django import template
from django.conf import settings


register = template.Library()


@register.filter
def native_lang(value):
    """
    Returns native language name by its code.
    """
    lang_dict = dict(settings.LANGUAGES_INFO)
    if value not in lang_dict:
        return value
    name, native = lang_dict[value]
    return native
