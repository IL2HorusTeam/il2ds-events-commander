# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import (AuthenticationForm as
    BaseAuthenticationForm)
from django.utils.translation import ugettext_lazy as _


class AuthenticationForm(BaseAuthenticationForm):
    """
    Add a 'remember me' checkbox to default form
    """
    remember_me = forms.BooleanField(label=_('Remember Me'),
        initial=False,
        required=False)
