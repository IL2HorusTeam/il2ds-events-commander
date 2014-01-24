# -*- coding: utf-8 -*-
import logging

from coffin.shortcuts import render

from django.conf import settings
from django.contrib.auth import (REDIRECT_FIELD_NAME, authenticate,
    login as auth_login, )
from django.contrib.sites.models import get_current_site

from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url

from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from django.utils.http import is_safe_url
from django.utils.translation import ugettext as _

from auth.decorators import anonymous_required
from auth.forms import AuthenticationForm
from website.responses import JSONResponse


LOG = logging.getLogger(__name__)


@sensitive_post_parameters()
@csrf_protect
@never_cache
@anonymous_required
def sign_in(request, template_name='auth/pages/sign-in.html',
            redirect_field_name=REDIRECT_FIELD_NAME,
            authentication_form=AuthenticationForm,
            current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action with AJAX support.
    """
    def check_remember_me(value=None):
        duration = 31536000 if value is not None \
            else settings.SESSION_COOKIE_AGE # 365 days or default
        request.session.set_expiry(duration)

    if request.is_ajax() and request.method == "POST":
        user = authenticate(username=request.REQUEST.get('username'),
                            password=request.REQUEST.get('password'))
        if user is None:
            return JSONResponse.error(message=unicode(
                authentication_form.error_messages['invalid_login']))
        if user.is_active:
            auth_login(request, user)
            check_remember_me(request.REQUEST.get('remember-me'))
            return JSONResponse.success()
        else:
            return JSONResponse.error(message=unicode(
                authentication_form.error_messages['inactive']))

    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
            auth_login(request, form.get_user())
            check_remember_me(form.cleaned_data.get('remember-me'))
            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
        'signin_page': True,
    }
    if extra_context is not None:
        context.update(extra_context)
    return render(request, template_name, context)
