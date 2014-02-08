# -*- coding: utf-8 -*-
"""
Forms for authentication-related views.
"""
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import (AuthenticationForm as
    BaseAuthenticationForm)
from django.utils.translation import ugettext_lazy as _


from auth_custom import signup_confirmation


class AuthenticationForm(BaseAuthenticationForm):
    """
    Add a 'remember me' checkbox to default form.
    """
    error_messages = {
        'invalid_username': _("Wrong username or password."),
        'inactive': _("Account is inactive."),
    }

    remember_me = forms.BooleanField(
        label=_('Remember Me'),
        initial=False,
        required=False)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_username'],
                    code='invalid_username',
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.error_messages['inactive'],
                    code='inactive',
                )
        return self.cleaned_data


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
    email = forms.EmailField(
        required=True,
        widget=forms.HiddenInput)
    confirmation_key = forms.CharField(
        required=True,
        validators=[signup_confirmation.validate_key, ],
        widget=forms.HiddenInput)

    first_name = forms.CharField(
        label=_("First name"),
        help_text=_("Your first name"),
        required=True)
    last_name = forms.CharField(
        label=_("Last name"),
        help_text=_("Your last name (optional)"))
    username = forms.RegexField(
        label=_("Username"),
        help_text=_("Your in-game name"),
        max_length=30,
        regex=r'^[\w.@+-=()\[\]{}]+$',
        required=True,
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/=/_/(/)/[/]/{/} characters.")
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
