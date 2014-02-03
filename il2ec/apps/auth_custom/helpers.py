# -*- coding: utf-8 -*-
"""
Authentication-related helpers.
"""
import logging

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from misc.tasks import send_mail


LOG = logging.getLogger(__name__)


def email_confirm_sign_up(email, context, language_code,
        template_name='auth_custom/emails/confirm-sign-up.html',
        from_email=None):
    """
    Send email with sign up confirmation instructions.
    """
    subject = unicode(_("Confirmation instructions"))
    to_emails = [email, ]

    # Execute Celery task directly as normal function
    return send_mail(subject, template_name, context, from_email, to_emails,
                     language_code)
