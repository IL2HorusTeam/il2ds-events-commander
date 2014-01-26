# -*- coding: utf-8 -*-
"""
Authentication Celery tasks.
"""
import logging

from celery.task import task

from auth_custom.models import SignUpRequest


LOG = logging.getLogger(__name__)


@task
def on_email_confirm_sign_up(successfully_sent, request_id):
    if not successfully_sent:
        return

    try:
        r = SignUpRequest.objects.get(pk=request_id)
    except SignUpRequest.DoesNotExist:
        LOG.error("No sign up request with id={id}".format(id=request_id))
    else:
        r.message_sent = True
        r.save()
