# -*- coding: utf-8 -*-
"""
Common forms.
"""
import logging

from django import forms
from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)


class BaseContactForm(forms.Form):
    """
    Base form for sending email messages to support team.
    """
    subject = forms.CharField(
        label=_("Subject"),
        help_text=_("What is your message about?"),
        max_length=50,
        required=True)
    body = forms.CharField(
        label=_("Message body"),
        help_text=_("Write your message here. "
                    "Be succinct, we'll ask if we need more info."),
        widget=forms.widgets.Textarea(),
        max_length=500,
        required=True)
    send_copy = forms.BooleanField(
        label=_('Send me a copy'),
        initial=False,
        required=False)


class AnonymousContactForm(BaseContactForm):
    """
    Concact form for anonymous users.
    """
    name = forms.CharField(
        label=_("Your name"),
        help_text=_("How should we appeal to you?"),
        max_length=50,
        required=True)
    email = forms.EmailField(
        label=_("Your email"),
        help_text=_("Where should we send our answer?"),
        required=True)


class AuthenticatedContactForm(BaseContactForm):
    """
    Concact form for authenticated users.
    """
