# -*- coding: utf-8 -*-
"""
Authentication Celery tasks.
"""
import logging

from celery.task import task

from auth_custom.models import SignUpRequest


LOG = logging.getLogger(__name__)


@task(ignore_result=True)
def delete_expired_sign_up_requests():
    """
    Task which is called periodically and cleans up expired sign up requests.
    """
    SignUpRequest.objects.delete_expired()
