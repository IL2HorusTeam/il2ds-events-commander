# -*- coding: utf-8 -*-
import logging

from coffin.shortcuts import render
from coffin.views.generic import FormView

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (REDIRECT_FIELD_NAME, authenticate,
    login as auth_login, get_user_model, )
from django.contrib.sites.models import get_current_site

from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.template.defaultfilters import timeuntil

from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.utils.translation import ugettext as _

from auth_custom.decorators import anonymous_required
from auth_custom.forms import AuthenticationForm, SignUpForm, SignUpRequestForm
from auth_custom.helpers import email_confirm_sign_up
from auth_custom.models import SignUpRequest
from website.responses import JSONResponse


LOG = logging.getLogger(__name__)


@sensitive_post_parameters()
@csrf_protect
@never_cache
@anonymous_required()
def sign_in(request, template_name='auth_custom/pages/sign-in.html',
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

            User = get_user_model()
            if User.objects.filter(email=email).exists():
                messages.error(
                    request, _("Specified email is already in use."))
                return self.form_invalid(form)

            signup_request = SignUpRequest.objects.create_from_email(email)
            LOG.info("YAY")
            LOG.info(signup_request.email)
            LOG.info("HAY")
            email_confirm_sign_up(signup_request)

            context = {
                'email': email,
                'expiration_date': signup_request.expiration_date,
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

    # def get(self, request, *args, **kwargs):
    #     """
    #     Handles GET requests.
    #     """

    # def post(self, request, *args, **kwargs):
    #     """
    #     Handles POST requests, instantiating a form instance with the passed
    #     POST variables and then checked for validity.
    #     """
