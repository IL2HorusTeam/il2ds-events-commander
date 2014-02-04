# -*- coding: utf-8 -*-
"""
Authentication models.
"""
import datetime
import hashlib
import logging
import random

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from auth_custom.settings import EMAIL_CONFIRMATION_DAYS
from misc.exceptions import ObjectAlreadyExistsError


LOG = logging.getLogger(__name__)


class SignUpRequestManager(models.Manager): # pylint: disable=R0904
    """
    Sign-up requests manager.
    """
    def create_from_email(self, email):
        """
        Create and return sign up request for specified email address.
        Raise 'AlreadyExists' exception, if unexpired sign up request already
        exists for specified email.
        """
        now = timezone.now()

        if SignUpRequest.objects.filter(email=email,
                                        expiration_date__gt=now).exists():
            raise SignUpRequest.AlreadyExists(
                _("Sign up request for {email} already exists.").format(
                  email=email))

        expiration_date = now + datetime.timedelta(
            days=EMAIL_CONFIRMATION_DAYS)

        salt = hashlib.sha1(unicode(random.random())).hexdigest()[:5]
        activation_key = hashlib.sha1(
            ''.join([salt, email, unicode(now)])).hexdigest()

        return SignUpRequest(
            email=email,
            activation_key=activation_key,
            created=now,
            expiration_date=expiration_date)

    def delete_expired(self):
        """
        Delete all expired sign up requests.
        """
        self.filter(expiration_date__lt=timezone.now()).delete()


class SignUpRequest(models.Model):
    """
    Model for storing sign-up requests. There can be several requests for one
    email, but there can be only one unexpired request.
    """
    AlreadyExists = ObjectAlreadyExistsError

    email = models.EmailField(_("email address"), unique=False)
    activation_key = models.CharField(_("activation key"),
        max_length=40)
    created = models.DateTimeField(_("created"))
    expiration_date = models.DateTimeField(_("expiration date"))

    objects = SignUpRequestManager()

    class Meta:
        verbose_name = _("sign up request")
        verbose_name_plural = _("sign up requests")
        ordering = ['-expiration_date', 'email']

    def __unicode__(self):
        return _("Sign up request for {email}").format(email=self.email)
