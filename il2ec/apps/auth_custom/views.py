# -*- coding: utf-8 -*-
"""
Views which handle authentication-related requests.
"""
import itertools
import logging

from coffin.shortcuts import render, render_to_string
from coffin.views.generic import FormView

from django.conf import settings as dj_settings
from django.contrib.auth import (REDIRECT_FIELD_NAME, login as auth_login,
    get_user_model, )
from django.contrib.sites.models import get_current_site

from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url

from django.template import RequestContext

from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.utils.timesince import timeuntil
from django.utils.translation import activate, deactivate, ugettext as _

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
                msg = ' '.join(itertools.chain(*form.errors.values()))
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
        if not request.is_ajax():
            return self.get(request, *args, **kwargs)
        form_class = self.get_form_class()
        form = form_class(data=request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            if SignUpRequest.objects.filter(email=email).exists():
                return JSONResponse.error(
                    message=_("Sign up request for specified email already "
                              "exists."))

            UserModel = get_user_model() # pylint: disable=C0103
            if UserModel.objects.filter(email=email).exists():
                return JSONResponse.error(
                    message=_("Specified email is already in use."))

            signup_request = SignUpRequest.objects.create_from_email(email)
            lang_code = request.LANGUAGE_CODE

            activate(lang_code)
            home_url = request.build_absolute_uri(resolve_url('website-index'))
            time_left = timeuntil(signup_request.expiration_date,
                                  signup_request.created)
            deactivate()

            context = {
                'host_address': home_url,
                'host_name': dj_settings.PROJECT_NAME.get(lang_code),
                'confirm_link': 'baz',
                'creation_date': signup_request.created,
                'expiration_date': signup_request.expiration_date,
            }
            sent = email_confirm_sign_up(email, context, lang_code)
            if not sent:
                return JSONResponse.error(
                    message=_("Sorry, we are failed to send an email to you. "
                              "Please, try again a bit later."))

            signup_request.save()
            return JSONResponse.success(payload={
                'email': email,
                'time_left': time_left,
            })
        else:
            msg = ' '.join(itertools.chain(*form.errors.values()))
            return JSONResponse.error(message=msg)


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