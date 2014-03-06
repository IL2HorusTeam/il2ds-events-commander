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

from django.http import HttpResponseBadRequest
from django.template import RequestContext

from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.utils.translation import ugettext as _

from auth_custom import settings
from auth_custom.helpers import (sign_up_confirmation, send_remind_me_email,
    update_current_language, )
from auth_custom.decorators import anonymous_required
from auth_custom.forms import (SignInForm, SignUpForm, SignUpRequestForm,
    RemindMeForm, GeneralSettingsForm, ChangeCallsignForm, )
from auth_custom.models import SignUpRequest, User

from commander.constants import UserCommand

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

    @method_decorator(anonymous_required())
    def dispatch(self, *args, **kwargs):
        return super(SignInView, self).dispatch(*args, **kwargs)

    @method_decorator(csrf_protect)
    @method_decorator(ajax_api())
    @method_decorator(sensitive_post_parameters())
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checking it for validity.
        """
        form_class = self.get_form_class()
        form = form_class(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            _remember_me(request, form)

            if not user.is_active:
                user.is_active = True
                user.save()
                messages.success(request, _("Your account was reactivated. "
                                            "Welcome back!"))

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


def sign_out(request, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Handle 'sign out' action and redirect to proper page if needed.
    """
    logout(request)
    next = request.GET.get(redirect_field_name) or \
           resolve_url('website-index')
    return redirect(next)


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
    @method_decorator(ajax_api())
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

            base_url = "{protocol}://{host}".format(
                protocol=('https' if request.is_secure() else 'http'),
                host=request.get_host())
            language = request.LANGUAGE_CODE

            sign_up_request = SignUpRequest.objects.get_or_create_for_email(
                email, base_url, language)
            async_result = sign_up_request.send_email()

            return JSONResponse.success(payload={
                'task_id': async_result.id,
                'email': email,
            })
        else:
            return JSONResponse.form_error(form)


@never_cache
@anonymous_required()
def sign_up(request, ridb64, confirmation_key,
            form_class=SignUpForm,
            template_name='auth_custom/pages/sign-up.html'):
    """
    Handles sign up GET requests with 'ridb64' and 'confirmation_key'
    parameters.
    """
    if not request.method == 'GET':
        return HttpResponseBadRequest()

    context = {}

    def _render(error=None):
        context.update({
            'no_errors': error is None,
        })
        if error:
            messages.error(request, unicode(error))
        return render(request, template_name, context)

    (sign_up_request, error) = \
        SignUpRequest.objects.request_or_error(ridb64, confirmation_key)

    if error:
        return _render(error)

    form = form_class(initial={
        'ridb64': ridb64,
        'confirmation_key': confirmation_key,
    })
    context.update({
        'email': sign_up_request.email,
        'form': form,
    })
    return _render()


@ajax_api()
@csrf_protect
@anonymous_required()
@sensitive_post_parameters()
def api_sign_up(request, form_class=SignUpForm):
    """
    Handles sign up AJAX POST requests.
    """
    form = form_class(request.POST)
    if form.is_valid():
        # Get sign up request -------------------------------------------------
        rid = form.cleaned_data['ridb64']
        confirmation_key = form.cleaned_data['confirmation_key']

        (sign_up_request, error) = \
            SignUpRequest.objects.request_or_error(rid, confirmation_key)
        if error:
            return JSONResponse.error(code=form_class.FATAL_ERROR_CODE,
                                      message=_("Security error."))

        # Fulfil registration -------------------------------------------------
        callsign = form.cleaned_data['callsign']
        password = form.cleaned_data['password']

        user = User.objects.create_user(
            email=sign_up_request.email,
            password=password,
            callsign=callsign,
            name=form.cleaned_data['name'],
            language=form.cleaned_data['language'])
        sign_up_request.delete()

        # Sign in user --------------------------------------------------------
        user = authenticate(username=callsign, password=password)
        login(request, user)
        _remember_me(request, form)

        with user.translator:
            redirect_url = resolve_url('website-index')

        return JSONResponse.success(payload={
            'redirect_url': redirect_url,
        })
    else:
        return JSONResponse.form_field_errors(form)


@ajax_api()
@csrf_protect
@sensitive_post_parameters()
def api_remind_me(request, form_class=RemindMeForm):
    """
    Handles AJAX POST requests for reminding callsign and resetting password.
    Callsign and link for password resetting will be sent to user by email.
    """
    user = request.user

    if user.is_anonymous():
        form = form_class(data=request.POST)
        if form.is_valid():
            user = form.get_user()
        else:
            return JSONResponse.form_error(form)

    async_result = send_remind_me_email(request, user)

    return JSONResponse.success(payload={
        'task_id': async_result.id,
        'email': user.email,
    })


@csrf_protect
@never_cache
def password_reset(request, uidb64, token,
                   form_class=SetPasswordForm,
                   template_name='auth_custom/pages/password-reset.html',
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

                is_anonymous = request.user.is_anonymous()

                message = _("Your password was successfully updated.")
                if is_anonymous:
                    message = message + " " + \
                          _("You can use it to sign in right now!")
                messages.success(request, message)

                next_name = 'auth-custom-sign-in' if is_anonymous else \
                            'website-index'
                return redirect(resolve_url(next_name))
        else:
            form = form_class(None)
    else:
        form = None

    context = {
        'form': form,
        'valid_link': valid_link,
    }
    return render(request, template_name, context)


@csrf_protect
@ajax_api()
@login_required
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
                  change_callsign_form_class=ChangeCallsignForm,
                  template_name='auth_custom/pages/user-settings.html'):
    """
    Display user settings and apply changes.
    """
    if not request.method == 'GET':
        return HttpResponseBadRequest()
    context = {
        'form_general': general_settings_form_class(request.user),
        'form_password': password_change_form_class(request.user),
        'form_callsign': change_callsign_form_class(request.user),
    }
    return render(request, template_name, context)


@ajax_api()
@csrf_protect
@login_required
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


@ajax_api()
@csrf_protect
@login_required
def api_change_callsign(request, form_class=ChangeCallsignForm):
    """
    Process AJAX request for changing callsign.
    """
    user = request.user
    form = form_class(user, data=request.POST)

    if form.is_valid():
        form.save()

        messages.success(request, _("Your callsign was successfully changed."))
        return JSONResponse.success()
    else:
        return JSONResponse.form_field_errors(form)


@ajax_api()
@csrf_protect
@login_required
def api_deactivate_account(request):
    """
    Process AJAX request for deactivating account.
    """
    user = request.user
    user.is_active = False
    user.save()

    logout(request)
    messages.success(request, _("Your account was successfully deactivated. "
                                "Goodbye!"))
    return JSONResponse.success()


@ajax_api(method='GET')
@login_required
def api_request_connection(request):
    password = request.user.create_connection_password(update=True)
    return JSONResponse.success(payload={
        'command': UserCommand.CONNECTION_INSTRUCTIONS.compose(password),
    })
