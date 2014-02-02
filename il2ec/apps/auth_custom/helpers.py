# -*- coding: utf-8 -*-
"""
Authentication-related helpers.
"""
import logging

from django.utils.translation import ugettext_lazy as _

from misc.tasks import send_mail


LOG = logging.getLogger(__name__)


def email_confirm_sign_up(
        sign_up_request,
        language_code=None,
        template_name='auth_custom/emails/confirm-sign-up.html',
        from_email=None):
    """
    Send email with sign up confirmation instructions.
    """
    subject = unicode(_("Confirmation instructions"))
    context = {
        'host_address': 'foo',
        'host_name': 'bar',
        'confirm_link': 'baz',
        'creation_date': sign_up_request.created,
        'expiration_date': sign_up_request.expiration_date,
    }
    to_emails = [sign_up_request.email, ]

    # Execute Celery task directly as normal function
    return send_mail(subject, template_name, context, from_email, to_emails,
                     language_code)
