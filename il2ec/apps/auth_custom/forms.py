# -*- coding: utf-8 -*-
"""
Forms for authentication-related views.
"""
import logging

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import (UserChangeForm as BaseUserChangeForm,
    UserCreationForm as BaseUserCreationForm, )
from django.utils.translation import ugettext_lazy as _

from auth_custom.helpers import sign_up_confirmation
from auth_custom.models import User
from auth_custom.validators import validate_callsign


LOG = logging.getLogger(__name__)


class SignInForm(forms.Form):
    """
    Form class for authenticating users.
    """
    callsign_email = forms.CharField(
        label=_("Callsign or email"),
        help_text=_("Data to identify account"),
        max_length=254,
        required=True)
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput)
    remember_me = forms.BooleanField(
        label=_('Remember me'),
        initial=False,
        required=False)

    error_messages = {
        'invalid_data': _("Invalid credentials."),
        'blocked': _("Account is blocked."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The form data comes in via the standard 'data' kwarg.
        """
        self.user_cache = None
        super(SignInForm, self).__init__(request, *args, **kwargs)

    def clean(self):
        callsign_email = self.cleaned_data.get('callsign_email')
        password = self.cleaned_data.get('password')

        if callsign_email and password:
            self.user_cache = authenticate(username=callsign_email,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_data'], code='invalid_data')
            elif self.user_cache.is_blocked:
                raise forms.ValidationError(
                    self.error_messages['blocked'], code='blocked')
        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class UserCreationForm(BaseUserCreationForm):
    """
    A form that creates a user, with no privileges, from the given callsign,
    email and password. Used in admin.
    """
    error_messages = {
        'duplicate_email': _("This email is already used."),
        'duplicate_callsign': _("This callsign is already used."),
        'password_mismatch': _("The two password fields didn't match."),
    }

    callsign = forms.RegexField(
        label=_("Callsign"),
        help_text=_("Name which is used in game"),
        max_length=30,
        regex=validate_callsign.regex.pattern,
        required=True,
        error_messages={
            'invalid': validate_callsign.message,
        })
    email = forms.EmailField(
        label=_("Email"),
        required=True)

    class Meta:
        model = User
        fields = ('callsign', 'email', )

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        del self.fields['username']

    def clean_callsign(self):
        callsign = self.cleaned_data['callsign']
        if User.objects.filter(callsign=callsign).exists():
            raise forms.ValidationError(
                self.error_messages['duplicate_callsign'],
                code='duplicate_callsign')
        return callsign

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                self.error_messages['duplicate_email'], code='duplicate_email')
        return email


class UserChangeForm(BaseUserChangeForm):
    """
    A form for updating users. Includes all the fields on the user, but
    replaces the password field with admin's password hash display field.
    Used in admin.
    """
    callsign = forms.RegexField(
        label=_("Callsign"),
        help_text=_("Name which is used in game"),
        max_length=30,
        regex=validate_callsign.regex.pattern,
        required=True,
        error_messages={
            'invalid': validate_callsign.message,
        })

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        del self.fields['username']


class SignUpRequestForm(forms.Form):
    """
    Form for getting data to create a request for sign up.
    """
    email = forms.EmailField(
        label=_("Email"),
        help_text=_("Email to send your sign up instructions to"),
        required=True)


class SignUpForm(forms.Form):
    """
    A form that creates a user with no privileges from the given first name,
    last name, callsign, password, language. Sign up request data (email and
    confirmation_key) must be provided.
    """
    FATAL_ERROR_CODE = 1

    error_messages = {
        'duplicate_email': _("This email is already used."),
        'duplicate_callsign': _("This callsign is already used."),
    }

    ridb64 = forms.CharField(
        required=True,
        widget=forms.HiddenInput)
    confirmation_key = forms.CharField(
        required=True,
        validators=[
            sign_up_confirmation.validate_key,
        ],
        widget=forms.HiddenInput)

    callsign = forms.RegexField(
        label=_("Callsign"),
        help_text=_("Name which is used in game"),
        max_length=30,
        regex=validate_callsign.regex.pattern,
        required=True,
        error_messages={
            'invalid': validate_callsign.message,
        })
    name = forms.CharField(
        label=_("Name"),
        help_text=_("Optional, but we won't have to say, \"Hey you!\""),
        max_length=50,
        required=False)
    password = forms.CharField(
        label=_("Password"),
        help_text=_("Password for website"),
        max_length=128,
        required=True,
        widget=forms.PasswordInput)
    language = forms.ChoiceField(
        label=_("Language"),
        help_text=_("Language to use on website and in game chat"),
        choices=settings.LANGUAGES,
        required=True,
        widget=forms.Select)
    remember_me = forms.BooleanField(
        label=_("Remember me"),
        required=False,
        help_text=_("Stay signed in on website"))

    def clean_callsign(self):
        callsign = self.cleaned_data['callsign']
        if User.objects.filter(callsign=callsign).exists():
            raise forms.ValidationError(
                self.error_messages['duplicate_callsign'],
                code='duplicate_callsign')
        return callsign

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                self.error_messages['duplicate_email'], code='duplicate_email')
        return email


class RemindMeForm(forms.Form):
    """
    Form for getting data to create a request for reminding callsign and
    resetting password.
    """
    error_messages = {
        'invalid_data': _("Invalid callsign or email."),
        'not_found': _("User not found."),
        'blocked': _("Account is blocked."),
    }

    callsign_email = forms.CharField(
        label=_("Callsign or email"),
        help_text=_("Data to identify account"),
        max_length=254,
        required=True)

    def __init__(self, *args, **kwargs):
        """
        Add 'user_cache' attribute for storing user, obtained from form data.
        """
        self.user_cache = None
        super(RemindMeForm, self).__init__(*args, **kwargs)

    def clean(self):
        value = self.cleaned_data.get('callsign_email')
        if value:
            try:
                self.user_cache = User.objects.get_by_callsign_or_email(value)
            except ValueError:
                raise forms.ValidationError(
                    self.error_messages['invalid_data'], code='invalid_data')
            except User.DoesNotExist:
                raise forms.ValidationError(
                    self.error_messages['not_found'], code='not_found')
            if self.user_cache.is_blocked:
                raise forms.ValidationError(
                    self.error_messages['blocked'], code='blocked')
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class GeneralSettingsForm(forms.Form):
    """
    Form for displaying and changing general user settings.
    """
    error_messages = {
        'duplicate_email': _("This email is already used."),
    }

    name = forms.CharField(
        label=_("Name"),
        help_text=_("Optional, but we won't have to say, \"Hey you!\""),
        max_length=50,
        required=False)
    email = forms.EmailField(
        label=_("Email"),
        help_text=_("Email for contacting you"),
        required=True)
    language = forms.ChoiceField(
        label=_("Language"),
        help_text=_("Language to use on website and in game chat"),
        choices=settings.LANGUAGES,
        required=True,
        widget=forms.Select)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(GeneralSettingsForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        if (email != self.user.email
            and User.objects.filter(email=email).exists()):
            raise forms.ValidationError(
                self.error_messages['duplicate_email'], code='duplicate_email')
        return email

    def save(self, commit=True):
        self.user.name = self.cleaned_data['name']
        self.user.email = self.cleaned_data['email']
        self.user.language = self.cleaned_data['language']

        if commit:
            self.user.save()
        return self.user


class ChangeCallsignForm(forms.Form):
    """
    Form for changing current callsign.
    """
    error_messages = {
        'duplicate_callsign': _("This callsign is already used."),
    }

    callsign = forms.RegexField(
        label=_("Callsign"),
        help_text=_("Name which is used in game"),
        max_length=30,
        regex=validate_callsign.regex.pattern,
        required=True,
        error_messages={
            'invalid': validate_callsign.message,
        })

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangeCallsignForm, self).__init__(*args, **kwargs)

    def clean_callsign(self):
        callsign = self.cleaned_data['callsign']
        if (callsign != self.user.callsign
            and User.objects.filter(callsign=callsign).exists()):
            raise forms.ValidationError(
                self.error_messages['duplicate_callsign'],
                code='duplicate_callsign')
        return callsign

    def save(self, commit=True):
        self.user.callsign = self.cleaned_data['callsign']
        if commit:
            self.user.save()
        return self.user
