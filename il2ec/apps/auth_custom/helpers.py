# -*- coding: utf-8 -*-
"""
Authentication-related Celery tasks.
"""
import logging

from django.utils.translation import ugettext_lazy as _

from auth_custom.tasks import on_email_confirm_sign_up
from misc.tasks import send_mail


LOG = logging.getLogger(__name__)


def email_confirm_sign_up(
        sign_up_request,
        template_name='auth_custom/emails/confirm-sign-up.html',
        from_email=None):
    """
    Send email with sign up confirmation instructions.
    """
    if sign_up_request.message_sent:
        LOG.warning("Sign up request confirmation instructions for "
                    "{id}:{email} were already sent.".format(
                    id=sign_up_request.id, email=sign_up_request.email))
        return

    subject = unicode(_("Confirmation instructions"))
    context = {
        'host_address': 'foo',
        'host_name': 'bar',
        'confirm_link': 'baz',
    }
    to_emails = [sign_up_request.email, ]
    send_mail.apply_async(
        (subject, template_name, context, from_email, to_emails),
        link=on_email_confirm_sign_up.s(sign_up_request.id))
