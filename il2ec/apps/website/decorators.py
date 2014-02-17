# -*- coding: utf-8 -*-
"""
General purpose website decorators.
"""
from functools import wraps
from django.http import HttpResponseBadRequest


def ajax_api(view_func):
    """
    Decorator for API views that process AJAX POST requests.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.method == "POST" and request.is_ajax():
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseBadRequest()
    return wrapped_view
