# -*- coding: utf-8 -*-
"""
Authentication Celery tasks.
"""
import logging

from celery.task import task

from auth_custom.models import SignUpRequest


LOG = logging.getLogger(__name__)


@task
def on_sign_up_confirm_email_sent(successfully_sent, request_id):
    """
    Task which is called after sign up confirmation mailing task.
    """
    if not successfully_sent:
        return
    try:
        r = SignUpRequest.objects.get(pk=request_id)
    except SignUpRequest.DoesNotExist:
        LOG.error("No sign up request with id={id}".format(id=request_id))
    else:
        r.message_sent = True
        r.save()


@task(ignore_result=True)
def delete_expired_sign_up_requests():
    """
    Task which is called periodically and cleans up expired sign up requests.
    """
    SignUpRequest.objects.delete_expired()
