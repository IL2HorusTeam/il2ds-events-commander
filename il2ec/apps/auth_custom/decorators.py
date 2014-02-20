# -*- coding: utf-8 -*-
"""
Authentication-related decorators.
"""
from functools import wraps

from django.http import HttpResponseRedirect
from django.utils.decorators import available_attrs


def anonymous_required(redirect_to=None):
    """
    Parametrized decorator for views that checks that the current user is
    anonymous. Encloses 'redirect_to' parameter into target function wrapper.
    """
    def decorator(view_func):
        """
        View function decorator.
        """
        @wraps(view_func, assigned=available_attrs(view_func))
        def view_func_wrapper(request, *args, **kwargs):
            """
            Target view function wrapper. Checks whether current user is
            anonymous. Redirects to specified or default page otherwise.
            """
            if request.user is not None and request.user.is_authenticated():
                if redirect_to is None:
                    from django.conf import settings
                    _redirect_to = settings.LOGIN_REDIRECT_URL
                else:
                    _redirect_to = redirect_to
                return HttpResponseRedirect(_redirect_to)
            return view_func(request, *args, **kwargs)

        return view_func_wrapper
    return decorator
