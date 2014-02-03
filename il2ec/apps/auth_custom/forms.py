# -*- coding: utf-8 -*-
"""
Forms for authentication-related views.
"""
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import (AuthenticationForm as
    BaseAuthenticationForm)
from django.utils.translation import ugettext_lazy as _


class AuthenticationForm(BaseAuthenticationForm):
    """
    Add a 'remember me' checkbox to default form.
    """
    error_messages = {
        'invalid_login': _("Wrong login or password."),
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
                    self.error_messages['invalid_login'],
                    code='invalid_login',
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
    email = forms.EmailField(required=True)


class SignUpForm(forms.Form):
    """
    Form for getting data to create a new user.
    """