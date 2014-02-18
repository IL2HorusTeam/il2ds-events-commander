# -*- coding: utf-8 -*-
"""
Views which handle authentication-related requests.
"""
import logging

from coffin.shortcuts import redirect, render, render_to_string, resolve_url
from coffin.views.generic import FormView

from django.conf import settings as dj_settings

from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout, get_user_model,
    REDIRECT_FIELD_NAME, )
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator

from django.core.exceptions import ValidationError
from django.core.validators import  validate_email

from django.http import HttpResponseBadRequest
from django.template import RequestContext

from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.utils.timesince import timeuntil
from django.utils.translation import activate, deactivate, ugettext as _

from auth_custom import settings
from auth_custom.helpers import (sign_up_confirmation, send_remind_me_email,
    update_current_language, )
from auth_custom.decorators import anonymous_required
from auth_custom.forms import (SignInForm, SignUpForm, SignUpRequestForm,
    RemindMeForm, GeneralSettingsForm, ChangeUsernameForm, )
from auth_custom.models import SignUpRequest, User

from website.decorators import ajax_api
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

    @method_decorator(ajax_api)
    @method_decorator(csrf_protect)
    @method_decorator(sensitive_post_parameters())
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checking it for validity.
        """
        form_class = self.get_form_class()
        form = form_class(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            _remember_me(request, form)
            return JSONResponse.success()
        else:
            return JSONResponse.form_error(form)

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

    @method_decorator(ajax_api)
    @method_decorator(csrf_protect)
    @method_decorator(sensitive_post_parameters())
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checking it for validity.
        """
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
                return JSONResponse.email_error()

            activate(request.LANGUAGE_CODE)
            time_left = timeuntil(sign_up_request.expiration_date,
                                  sign_up_request.created)
            deactivate()

            return JSONResponse.success(payload={
                'email': email,
                'time_left': time_left,
            })
        else:
            return JSONResponse.form_error(form)


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


@ajax_api
@never_cache
@csrf_protect
@anonymous_required()
@sensitive_post_parameters()
def api_sign_up(request, form_class=SignUpForm):
    """
    Handles sign up AJAX POST requests.
    """
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
        return JSONResponse.form_field_errors(form)


@ajax_api
@never_cache
@csrf_protect
@sensitive_post_parameters()
def api_remind_me(request, form_class=RemindMeForm):
    """
    Handles AJAX POST requests for reminding username and resetting password.
    Username and link for password resetting will be sent to user by email.
    """
    user = request.user

    if user.is_anonymous():
        form = form_class(data=request.POST)
        if form.is_valid():
            user = form.get_user()
        else:
            return JSONResponse.form_error(form)

    if send_remind_me_email(request, user):
        return JSONResponse.success(payload={
            'email': user.email,
        })
    else:
        return JSONResponse.email_error()


@csrf_protect
@never_cache
def password_reset(request, uidb64, token,
                   form_class=SetPasswordForm,
                   template_name='auth_custom/pages/password-reset.html',
                   complete_template_name='auth_custom/pages/password-reset-complete.html',
                   token_generator=default_token_generator):
    """
    View that checks the hash in a password reset link and presents a form for
    entering a new password.
    """
    assert uidb64 is not None and token is not None  # checked by URLconf
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    valid_link = user is not None and token_generator.check_token(user, token)

    if valid_link:
        if request.method == 'POST':
            form = form_class(user, request.POST)
            if form.is_valid():
                form.save()
                return render(request, complete_template_name, {})
        else:
            form = form_class(None)
    else:
        form = None

    context = {
        'form': form,
        'valid_link': valid_link,
    }
    return render(request, template_name, context)


@ajax_api
@csrf_protect
@login_required
@never_cache
def api_password_change(request, form_class=PasswordChangeForm):
    """
    Process AJAX request for changing user password.
    """
    user = request.user
    form = form_class(user, data=request.POST)

    if form.is_valid():
        form.save()
        return JSONResponse.success()
    else:
        return JSONResponse.form_field_errors(form)


@login_required
@never_cache
def user_settings(request,
                  general_settings_form_class=GeneralSettingsForm,
                  password_change_form_class=PasswordChangeForm,
                  change_username_form_class=ChangeUsernameForm,
                  template_name='auth_custom/pages/user-settings.html'):
    """
    Display user settings and apply changes.
    """
    if not request.method == "GET":
        return HttpResponseBadRequest()
    context = {
        'form_general': general_settings_form_class(request.user),
        'form_password': password_change_form_class(request.user),
        'form_username': change_username_form_class(request.user),
    }
    return render(request, template_name, context)


@ajax_api
@csrf_protect
@login_required
@never_cache
def api_general_settings(request, form_class=GeneralSettingsForm):
    """
    Process AJAX request for changing user general settings.
    """
    user = request.user
    form = form_class(user, data=request.POST)

    if form.is_valid():
        form.save()
        update_current_language(request, user.language)

        messages.success(request, _("New settings were successfully applied."))
        return JSONResponse.success()
    else:
        return JSONResponse.form_field_errors(form)


@ajax_api
@csrf_protect
@login_required
@never_cache
def api_change_username(request, form_class=ChangeUsernameForm):
    """
    Process AJAX request for changing username.
    """
    user = request.user
    form = form_class(user, data=request.POST)

    if form.is_valid():
        form.save()

        messages.success(request, _("Your username was successfully changed."))
        return JSONResponse.success()
    else:
        return JSONResponse.form_field_errors(form)
