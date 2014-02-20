# -*- coding: utf-8 -*-
"""
General purpose website decorators.
"""
from functools import wraps

from django.http import HttpResponseBadRequest
from django.utils.decorators import available_attrs


def ajax_api(method='POST'):
    """
    Parametrized decorator for API views that checks that request was sent
    via AJAX by propper method.
    """
    def decorator(view_func):
        """
        View function decorator.
        """
        @wraps(view_func, assigned=available_attrs(view_func))
        def view_func_wrapper(request, *args, **kwargs):
            """
            Decorator for target API views that process AJAX requests.
            """
            if request.method == method and request.is_ajax():
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseBadRequest()

        return view_func_wrapper
    return decorator
