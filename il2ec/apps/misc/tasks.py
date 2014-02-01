# -*- coding: utf-8 -*-
"""
Miscellaneous Celery tasks.
"""
import logging

from celery.task import task
from coffin.shortcuts import render_to_string

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.utils.translation import activate, deactivate


LOG = logging.getLogger(__name__)


@task(ignore_result=True)
def send_mail(subject, template_name, context_dict, from_email=None,
              to_emails=None, language_code=None):
    """
    Send email with specified template and context.
    """
    if not to_emails:
        LOG.warning("Email will not be sent: no recipients were specified")
        return
    from_email = from_email or settings.DEFAULT_FROM_EMAIL

    if language_code:
        activate(language_code)
        html_part = render_to_string(template_name, context_dict)
        deactivate()
    else:
        html_part = render_to_string(template_name, context_dict)
    text_part = strip_tags(html_part).strip()

    msg = EmailMultiAlternatives(subject, text_part, from_email, to_emails)
    msg.attach_alternative(html_part, "text/html")

    try:
        msg.send(fail_silently=False)
        return True
    except Exception as e:
        LOG.error('Failed to send message to {to}: {err}'.format(
            to=repr(to_emails), err=unicode(e)))
        return False
