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
from auth_custom.validators import validate_username


LOG = logging.getLogger(__name__)


class SignInForm(forms.Form):
    """
    Form class for authenticating users.
    """
    email_username = forms.CharField(
        label=_("Username or email"),
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
        'inactive': _("Account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The form data comes in via the standard 'data' kwarg.
        """
        self.user_cache = None
        super(SignInForm, self).__init__(*args, **kwargs)

    def clean(self):
        email_username = self.cleaned_data.get('email_username')
        password = self.cleaned_data.get('password')

        if email_username and password:
            self.user_cache = authenticate(username=email_username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_data'], code='invalid_data')
            elif not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.error_messages['inactive'], code='inactive')
        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class UserCreationForm(BaseUserCreationForm):
    """
    A form that creates a user, with no privileges, from the given username,
    email and password. Used in admin.
    """
    error_messages = dict(BaseUserCreationForm.error_messages, **{
        'duplicate_email': _("This email is already used."),
    })

    username = forms.RegexField(
        label=_("Username"),
        help_text=_("Name which is used in game"),
        max_length=30,
        regex=validate_username.regex.pattern,
        required=True,
        error_messages={
            'invalid': validate_username.message,
        })
    email = forms.EmailField(
        label=_("Email"),
        required=True)

    class Meta:
        model = User
        fields = ('username', 'email', )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                self.error_messages['duplicate_username'],
                code='duplicate_username')
        return username

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
    username = forms.RegexField(
        label=_("Username"),
        help_text=_("Name which is used in game"),
        max_length=30,
        regex=validate_username.regex.pattern,
        required=True,
        error_messages={
            'invalid': validate_username.message,
        })

    class Meta:
        model = User
        fields = '__all__'


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
    last name, username, password, language. Sign up request data (email and
    confirmation_key) must be provided.
    """
    FATAL_ERROR_CODE = 1

    error_messages = {
        'duplicate_email': _("This email is already used."),
        'duplicate_username': _("A user with that username already exists."),
    }

    email = forms.EmailField(
        required=True,
        widget=forms.HiddenInput)
    confirmation_key = forms.CharField(
        required=True,
        validators=[
            sign_up_confirmation.validate_key,
        ],
        widget=forms.HiddenInput)

    first_name = forms.CharField(
        label=_("First name"),
        help_text=_("Your first name"),
        max_length=30,
        required=True)
    last_name = forms.CharField(
        label=_("Last name"),
        help_text=_("Your last name (optional)"),
        max_length=30,
        required=False)
    username = forms.RegexField(
        label=_("Username"),
        help_text=_("Name which is used in game"),
        max_length=30,
        regex=validate_username.regex.pattern,
        required=True,
        error_messages={
            'invalid': validate_username.message,
        })
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

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                self.error_messages['duplicate_username'],
                code='duplicate_username')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                self.error_messages['duplicate_email'], code='duplicate_email')
        return email


class RemindMeForm(forms.Form):
    """
    Form for getting data to create a request for reminding username and
    resetting password.
    """
    error_messages = {
        'invalid_data': _("Invalid username or email."),
        'not_found': _("User not found."),
        'inactive': _("Account is inactive."),
    }

    email_username = forms.CharField(
        label=_("Username or email"),
        help_text=_("Data for identifying your account"),
        max_length=254,
        required=True)

    def __init__(self, request=None, *args, **kwargs):
        """
        Add 'user_cache' attribute for storing user, obtained from form data.
        """
        self.user_cache = None
        super(RemindMeForm, self).__init__(*args, **kwargs)

    def clean(self):
        value = self.cleaned_data.get('email_username')
        if value:
            try:
                self.user_cache = User.objects.get_by_username_or_email(value)
            except ValueError:
                raise forms.ValidationError(
                    self.error_messages['invalid_data'], code='invalid_data')
            except User.DoesNotExist:
                raise forms.ValidationError(
                    self.error_messages['not_found'], code='not_found')
            if not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.error_messages['inactive'], code='inactive')
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

    first_name = forms.CharField(
        label=_("First name"),
        help_text=_("Your first name"),
        max_length=30,
        required=True)
    last_name = forms.CharField(
        label=_("Last name"),
        help_text=_("Your last name (optional)"),
        max_length=30,
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
        self.user.first_name = self.cleaned_data['first_name']
        self.user.last_name = self.cleaned_data['last_name']
        self.user.email = self.cleaned_data['email']
        self.user.language = self.cleaned_data['language']

        if commit:
            self.user.save()
        return self.user


class ChangeUsernameForm(forms.Form):
    """
    Form for changing current username.
    """
    error_messages = {
        'duplicate_username': _("A user with that username already exists."),
    }

    username = forms.RegexField(
        label=_("Username"),
        help_text=_("Name which is used in game"),
        max_length=30,
        regex=validate_username.regex.pattern,
        required=True,
        error_messages={
            'invalid': validate_username.message,
        })

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangeUsernameForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']
        if (username != self.user.username
            and User.objects.filter(username=username).exists()):
            raise forms.ValidationError(
                self.error_messages['duplicate_username'],
                code='duplicate_username')
        return username

    def save(self, commit=True):
        self.user.username = self.cleaned_data['username']
        if commit:
            self.user.save()
        return self.user
