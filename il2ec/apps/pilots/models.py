# -*- coding: utf-8 -*-
"""
Pilot database models.
"""
import logging

from celery.task import task

from django.contrib.auth.hashers import (check_password, make_password,
    is_password_usable, )

from django.db import models
from django.db.models.signals import post_save, post_delete

from django.utils.translation import ugettext_lazy as _, activate, deactivate

from auth_custom.models import User
from misc.helpers import Translator, random_string
from pilots.settings import PILOTS_PASSWORD_LENGTH


LOG = logging.getLogger(__name__)


class Pilot(models.Model):
    """
    Adds pilot-related fields to User model.
    """
    user = models.OneToOneField(User)
    password = models.CharField(
        verbose_name=_("password"),
        max_length=128,
        help_text=_("one time password for connecting to game server"))

    @property
    def callsign(self):
        return self.user.username

    @property
    def translator(self):
        """
        Return an object which can be used to set current language for
        translation of lazy strings in language preferred by user.

        Usage:
            with pilot.translator:
                s = ugettext("some string")
        """
        if not hasattr(self, '__translator'):
            self.__translator = Translator(self.user.language)
        return self.__translator

    def create_password(self):
        """
        Sets and returns new password for connecting to game server.
        """
        password = random_string(PILOTS_PASSWORD_LENGTH)
        self.set_password(password)
        return password

    def set_password(self, raw_password):
        """
        Sets given password.
        """
        self.password = make_password(raw_password)

    def clear_password(self):
        """
        Clear current password, so pilot can not use it again.
        """
        self.password = make_password(None)

    def check_password(self, raw_password):
        """
        Tells whether given password matches real password.
        """
        return check_password(raw_password, self.password)

    def can_connect(self):
        """
        Tells whether pilot has permision to connect to game server.
        """
        return is_password_usable(self.password)

    def __unicode__(self):
        return self.user.username


@task
def create_pilot(sender, instance, created, **kwargs):
    """
    Create pilot instance when user is created.
    """
    if created:
        pilot, created = Pilot.objects.get_or_create(user=instance)


@task
def delete_user(sender, instance=None, **kwargs):
    """
    Delete user instance after deleting pilot.
    """
    try:
        instance.user
    except User.DoesNotExist:
        pass
    else:
        instance.user.delete()


post_save.connect(create_pilot, sender=User)
post_delete.connect(delete_user, sender=Pilot)
