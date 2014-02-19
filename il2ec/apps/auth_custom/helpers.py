# -*- coding: utf-8 -*-
"""
Helpers for authentication.
"""
import hashlib
import logging
import random

from coffin.shortcuts import resolve_url

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator

from django.utils.translation import activate, deactivate, ugettext_lazy as _
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


from misc.tasks import send_mail
from misc.validators import SHA1Validator


LOG = logging.getLogger(__name__)


class SignUpConfirmationHelper(object):
    """
    Bound helpers for email confirmation.
    """
    validate_key = SHA1Validator(
        message=_("Enter a valid email confirmation key."))

    def generate_key(self, *args):
        """
        Generate confirmation key from salted input arguments.
        """
        salt = hashlib.sha1(unicode(random.random())).hexdigest()[:5]

        chunks = map(unicode, args)
        chunks.append(salt)
        data = ''.join(chunks)

        return hashlib.sha1(data).hexdigest()


sign_up_confirmation = SignUpConfirmationHelper()
del SignUpConfirmationHelper


def send_remind_me_email(http_request, user,
                         template_name='auth_custom/emails/remind-me.html',
                         token_generator=default_token_generator):
    """
    Send username reminding email message with instructions for pasword
    resetting. Return 'True' if succeeded, 'False' otherwise.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)

    activate(user.language)
    home_url = http_request.build_absolute_uri(resolve_url(
        'website-index'))
    reset_password_url = http_request.build_absolute_uri(resolve_url(
        'auth-custom-password-reset', uid, token))
    deactivate()

    context = {
        'host_address': home_url,
        'host_name': settings.PROJECT_NAME,
        'reset_password_url': reset_password_url,
        'user': user,
    }
    subject = unicode(_("Remind data"))
    to_emails = [user.email, ]

    # Execute Celery task directly as normal function
    return send_mail(subject, template_name, context,
                     to_emails=to_emails, language_code=user.language)


def update_current_language(request, language):
    """
    Update current language for web user.
    """
    request.session['django_language'] = language
