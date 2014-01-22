# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.contrib.auth import (REDIRECT_FIELD_NAME, authenticate,
    login as auth_login, )
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import get_current_site

from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse

from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from django.utils.http import is_safe_url
from django.utils.translation import ugettext as _

from website.responses import JSONResponse


LOG = logging.getLogger(__name__)


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='auth/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action with AJAX support.
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        if request.is_ajax():
            user = authenticate(
                username=request.REQUEST.get('username'),
                password=request.REQUEST.get('password'))
            if user is None:
                return JSONResponse.error(message=_("Wrong login or password"))
            if user.is_active:
                auth_login(request, user)
                return JSONResponse.success()
            else:
                return JSONResponse.error(message=_("Account is disabled"))
        else:
            form = authentication_form(request, data=request.POST)
            if form.is_valid():
                if not is_safe_url(url=redirect_to, host=request.get_host()):
                    redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
                auth_login(request, form.get_user())
                return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)
