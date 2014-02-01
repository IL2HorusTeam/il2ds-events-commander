# -*- coding: utf-8 -*-
"""
Views which handle authentication-related requests.
"""
import logging

from coffin.shortcuts import render
from coffin.views.generic import FormView

from django.conf import settings as dj_settings
from django.contrib import messages
from django.contrib.auth import (REDIRECT_FIELD_NAME, login as auth_login,
    get_user_model, )
from django.contrib.sites.models import get_current_site

from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url

from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.utils.translation import ugettext as _

from auth_custom import settings
from auth_custom.decorators import anonymous_required
from auth_custom.forms import AuthenticationForm, SignUpForm, SignUpRequestForm
from auth_custom.helpers import email_confirm_sign_up
from auth_custom.models import SignUpRequest
from website.responses import JSONResponse


LOG = logging.getLogger(__name__)


def __do_sign_in(request, form):
    """
    Helper sign in function: authenticate user and update session expiry date
    if 'remember-me' field was checked.
    """
    auth_login(request, form.get_user())
    if form.cleaned_data.get('remember_me'):
        request.session.set_expiry(settings.REMEMBER_ME_AGE)


@sensitive_post_parameters()
@csrf_protect
@never_cache
@anonymous_required()
def sign_in(request,                                    # pylint: disable=R0913
            template_name='auth_custom/pages/sign-in.html',
            redirect_field_name=REDIRECT_FIELD_NAME,
            authentication_form=AuthenticationForm,
            current_app=None,                           # pylint: disable=W0613
            extra_context=None):
    """
    Displays the login form and handles the login action with AJAX support.
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)

        if request.is_ajax():
            # Process AJAX request --------------------------------------------
            if form.is_valid():
                __do_sign_in(request, form)
                return JSONResponse.success()
            else:
                msg = ' '.join([
                    # Convert lists of lists into a flat list
                    e for errs in form.errors.values() for e in errs
                ])
                return JSONResponse.error(message=unicode(msg))

        # Process non-AJAX request --------------------------------------------
        if form.is_valid():
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(dj_settings.LOGIN_REDIRECT_URL)
            __do_sign_in(request, form)
            return HttpResponseRedirect(redirect_to)
    else:
        # Process GET request -------------------------------------------------
        form = authentication_form(request)

    current_site = get_current_site(request)
    context = {
        'form': form,
        'site': current_site,
        'site_name': current_site.name,
        'signin_page': True,
        redirect_field_name: redirect_to,
    }
    if extra_context is not None:
        context.update(extra_context)
    return render(request, template_name, context)


class SignUpRequestView(FormView):
    """
    View for sign up request.
    """
    form_class = SignUpRequestForm
    template_name = 'auth_custom/pages/sign-up-request.html'
    template_success_name = 'auth_custom/pages/sign-up-request-done.html'

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    @method_decorator(anonymous_required())
    def dispatch(self, *args, **kwargs):
        return super(SignUpRequestView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            email = form.cleaned_data['email']

            if SignUpRequest.objects.filter(email=email).exists():
                messages.error(request, _("Sign up request for specified "
                                          "email already exists."))
                return self.form_invalid(form)

            UserModel = get_user_model() # pylint: disable=C0103
            if UserModel.objects.filter(email=email).exists():
                messages.error(
                    request, _("Specified email is already in use."))
                return self.form_invalid(form)

            signup_request = SignUpRequest.objects.create_from_email(email)
            email_confirm_sign_up(signup_request,
                                  language_code=request.LANGUAGE_CODE)
            context = {
                'signup_request': signup_request,
            }
            return render(request, self.template_success_name, context)
        else:
            return self.form_invalid(form)


class SignUpView(FormView):
    """
    View for sign up.
    """
    form_class = SignUpForm
    template_name = 'auth_custom/pages/sign-up.html'

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    @method_decorator(anonymous_required())
    def dispatch(self, *args, **kwargs):
        return super(SignUpView, self).dispatch(*args, **kwargs)
