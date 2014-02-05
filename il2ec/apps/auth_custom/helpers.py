# -*- coding: utf-8 -*-
"""
Authentication-related helpers.
"""
import hashlib
import logging
import random

from coffin.shortcuts import resolve_url
from django.utils.translation import activate, deactivate, ugettext_lazy as _

from misc.tasks import send_mail
from website.helpers import get_project_name


LOG = logging.getLogger(__name__)


class email_confirmation(object):
    """
    Provides helpers for generating and checking confirmation keys, sending
    email confirmation messages.
    """
    template_name = 'auth_custom/emails/confirm-sign-up.html'

    @staticmethod
    def generate_key(*args):
        """
        Generate confirmation key from salted input arguments.
        """
        salt = hashlib.sha1(unicode(random.random())).hexdigest()[:5]

        chunks = map(unicode, args)
        chunks.append(salt)
        data = ''.join(chunks)

        return hashlib.sha1(data).hexdigest()

    @staticmethod
    def send_email(http_request, signup_request):
        language_code = http_request.LANGUAGE_CODE

        activate(language_code)
        home_url = http_request.build_absolute_uri(resolve_url(
            'website-index'))
        confirmation_url = http_request.build_absolute_uri(resolve_url(
            'auth-custom-sign-up',
            signup_request.email, signup_request.confirmation_key))
        deactivate()

        context = {
            'host_address': home_url,
            'host_name': get_project_name(language_code),
            'confirmation_url': confirmation_url,
            'creation_date': signup_request.created,
            'expiration_date': signup_request.expiration_date,
        }
        subject = unicode(_("Confirmation instructions"))
        to_emails = [signup_request.email, ]

        # Execute Celery task directly as normal function
        return send_mail(subject, email_confirmation.template_name, context,
                         to_emails=to_emails, language_code=language_code)
