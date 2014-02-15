# -*- coding: utf-8 -*-
"""
Views which handle authentication-related requests.
"""
import itertools
import logging

from coffin.shortcuts import redirect, render, render_to_string, resolve_url
from coffin.views.generic import FormView

from django.conf import settings as dj_settings

from django.contrib.auth import (authenticate, login, logout, get_user_model,
    REDIRECT_FIELD_NAME, )
from django.contrib.auth.decorators import login_required

from django.core.exceptions import ValidationError
from django.core.validators import  validate_email

from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.template import RequestContext

from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.utils.timesince import timeuntil
from django.utils.translation import activate, deactivate, ugettext as _

from auth_custom import settings
from auth_custom.helpers import sign_up_confirmation, send_remind_me_email
from auth_custom.decorators import anonymous_required
from auth_custom.forms import (SignInForm, SignUpForm, SignUpRequestForm,
    RemindMeForm, )
from auth_custom.models import SignUpRequest, User

from website.responses import JSONResponse


LOG = logging.getLogger(__name__)


def _remember_me(request, form):
    """
    Prolong session expiration date if 'Remember me' was checked on form.
    """
    if form.cleaned_data.get('remember_me'):
        request.session.set_expiry(settings.REMEMBER_ME_AGE)


class SignInView(FormView):
    """
    Displays the 'sign in' and 'remind me' forms, handles the login action
    with AJAX support.
    """
    form_class = SignInForm
    template_name = 'auth_custom/pages/sign-in.html'
    redirect_field_name = REDIRECT_FIELD_NAME

    @method_decorator(never_cache)
    @method_decorator(anonymous_required())
    def dispatch(self, *args, **kwargs):
        return super(SignInView, self).dispatch(*args, **kwargs)

    @method_decorator(csrf_protect)
    @method_decorator(sensitive_post_parameters())
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checking it for validity.
        """
        if not request.is_ajax():
            return HttpResponseBadRequest()

        form_class = self.get_form_class()
        form = form_class(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            _remember_me(request, form)
            return JSONResponse.success()
        else:
            msg = ' '.join(itertools.chain(*form.errors.values()))
            return JSONResponse.error(message=unicode(msg))

    def get(self, request, *args, **kwargs):
        """
        Handles sign in GET request.
        """
        redirect_to = request.REQUEST.get(self.redirect_field_name, '')
        context = {
            'sign_in_page': True,
            'sign_in_next': redirect_to,
        }
        return render(request, self.template_name, context)


@never_cache
@login_required
def sign_out(request, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Handle 'sign out' action and redirect to proper page if needed.
    """
    logout(request)
    referer = request.GET.get(redirect_field_name) or \
              resolve_url('website-index')
    return redirect(referer)


class SignUpRequestView(FormView):
    """
    View for sign up request.
    """
    form_class = SignUpRequestForm
    template_name = 'auth_custom/pages/sign-up-request.html'

    @method_decorator(never_cache)
    @method_decorator(anonymous_required())
    def dispatch(self, *args, **kwargs):
        return super(SignUpRequestView, self).dispatch(*args, **kwargs)

    @method_decorator(csrf_protect)
    @method_decorator(sensitive_post_parameters())
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checking it for validity.
        """
        if not request.is_ajax():
            return HttpResponseBadRequest()

        form_class = self.get_form_class()
        form = form_class(data=request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            UserModel = get_user_model() # pylint: disable=C0103
            if UserModel.objects.filter(email=email).exists():
                return JSONResponse.error(
                    message=_("Specified email is already in use."))

            try:
                sign_up_request = SignUpRequest.objects.create_from_email(
                                    email)
            except SignUpRequest.AlreadyExists as e:
                return JSONResponse.error(message=unicode(e))

            if sign_up_confirmation.send_email(request, sign_up_request):
                sign_up_request.save()
            else:
                return JSONResponse.error(
                    message=_("Sorry, we failed to send an email to you. "
                              "Please, try again a bit later."))

            activate(request.LANGUAGE_CODE)
            time_left = timeuntil(sign_up_request.expiration_date,
                                  sign_up_request.created)
            deactivate()

            return JSONResponse.success(payload={
                'email': email,
                'time_left': time_left,
            })
        else:
            msg = ' '.join(itertools.chain(*form.errors.values()))
            return JSONResponse.error(message=msg)


@never_cache
@anonymous_required()
def sign_up(request, email, confirmation_key,
            form_class=SignUpForm,
            template_name='auth_custom/pages/sign-up.html'):
    """
    Handles sign up GET requests with 'email' and 'key' parameters.
    """
    if settings.SESSION_SIGN_UP_INFO_KEY in request.session:
        del request.session[settings.SESSION_SIGN_UP_INFO_KEY]

    if not request.method == "GET":
        return HttpResponseBadRequest()

    context = {
        'errors': [],
    }

    def _render():
        return render(request, template_name, context)

    try:
        validate_email(email)
    except ValidationError as e:
        context['errors'].append(unicode(e.message))
    try:
        sign_up_confirmation.validate_key(confirmation_key)
    except ValidationError as e:
        context['errors'].append(unicode(e.message))

    if context['errors']:
        return _render()

    sign_up_request = SignUpRequest.objects.get_unexpired(email,
                                                          confirmation_key)
    if sign_up_request is None:
        context['errors'].append(_("Sign up request with specified parameters "
                                   "does not exist."))
        return _render()

    data = {
        'email': email,
        'confirmation_key': confirmation_key,
    }
    form = form_class(initial=data)
    context.update({
        'email': email,
        'form': form,
    })

    info = {
        'request_id': sign_up_request.id,
    }
    info.update(data)
    request.session[settings.SESSION_SIGN_UP_INFO_KEY] = info

    return _render()


@never_cache
@csrf_protect
@anonymous_required()
@sensitive_post_parameters()
def sign_up_invoke(request, form_class=SignUpForm):
    """
    Handles sign up AJAX POST requests.
    """
    if not (request.method == "POST" and request.is_ajax()):
        return HttpResponseBadRequest()

    def _security_error():
        return JSONResponse.error(
            code=form_class.FATAL_ERROR_CODE,
            message=_("Sign up security error."))

    # Ensure existance of sign up info from previous GET
    if not settings.SESSION_SIGN_UP_INFO_KEY in request.session:
        return _security_error()

    form = form_class(request.POST)
    if form.is_valid():
        # Check that sign up data from POST equals data from previous GET -----
        info = request.session[settings.SESSION_SIGN_UP_INFO_KEY]

        email = form.cleaned_data['email']
        confirmation_key = form.cleaned_data['confirmation_key']

        if (email != info['email'] or
            confirmation_key != info['confirmation_key']):
            return _security_error()

        # Ensure sign up request still exists and it's ID equals to known ID --
        sign_up_request = SignUpRequest.objects.get_unexpired(email,
                                                              confirmation_key)
        if sign_up_request is None:
            return JSONResponse.error(
                code=form_class.FATAL_ERROR_CODE,
                message=_("Sign up request with specified parameters does not "
                          "exist."))
        if sign_up_request.id != info['request_id']:
            return _security_error()

        # Fulfil registration -------------------------------------------------
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        user = User.objects.create_user(
            email=email,
            password=password,
            username=username,
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            language=form.cleaned_data['language'])
        sign_up_request.delete()
        del request.session[settings.SESSION_SIGN_UP_INFO_KEY]

        # Sign in user --------------------------------------------------------
        user = authenticate(username=username, password=password)
        login(request, user)
        _remember_me(request, form)

        activate(user.language)
        redirect_url = resolve_url('website-index')
        deactivate()

        return JSONResponse.success(payload={
            'redirect_url': redirect_url,
        })
    else:
        errors = {
            field_name: ' '.join([unicode(e) for e in error_list])
                        for field_name, error_list in form.errors.items()
        }
        return JSONResponse.error(payload={
            'errors': errors
        })


@never_cache
@csrf_protect
@anonymous_required()
@sensitive_post_parameters()
def remind_me_request(request, form_class=RemindMeForm):
    """
    Handles AJAX POST requests for reminding username and resetting password.
    Username and link for password resetting will be sent to user by email.
    """
    if not (request.method == "POST" and request.is_ajax()):
        return HttpResponseBadRequest()

    form = form_class(data=request.POST)
    if form.is_valid():
        user = form.get_user()
        if send_remind_me_email(request, user):
            return JSONResponse.success(payload={
                'email': user.email,
            })
        else:
            return JSONResponse.error(
                message=_("Sorry, we failed to send an email to you. "
                          "Please, try again a bit later."))
    else:
        msg = ' '.join(itertools.chain(*form.errors.values()))
        return JSONResponse.error(message=unicode(msg))


# Doesn't need csrf_protect since no-one can guess the URL
@never_cache
@anonymous_required()
def password_reset(request, uidb64, token,
                   template_name='auth_custom/pages/password-reset.html'):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    LOG.info("Password reset request: '{uid}', '{token}'".format(
             uid=uidb64, token=token))

    # TODO:

    context = {}
    return render(request, template_name, context)
