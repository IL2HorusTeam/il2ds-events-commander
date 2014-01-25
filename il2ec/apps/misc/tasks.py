# -*- coding: utf-8 -*-
"""
Miscellaneous Celery tasks.
"""
import logging

from celery.task import task

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template
from django.utils.html import strip_tags


LOG = logging.getLogger(__name__)


@task(ignore_result=True)
def send_mail(subject, template_name, context_dict, from_email=None,
              to_emails=None):
    if not to_emails:
        LOG.warning("Email will not be sent: no recipients were specified")
        return
    from_email = from_email or settings.DEFAULT_FROM_EMAIL

    template = get_template(template_name)
    context = Context(context_dict)

    html_part = template.render(context)
    text_part = strip_tags(html_part)

    msg = EmailMultiAlternatives(subject, text_part, from_email, to_emails)
    msg.attach_alternative(html_part, "text/html")

    try:
        msg.send(fail_silently=False)
    except Exception as e:
        LOG.error('Failed to send message to {to}: {err}'.format(
            to=repr(to_emails), err=unicode(e)))
