# -*- coding: utf-8 -*-
"""
Pilot database models.
"""
from celery.task import task

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext_lazy as _


UserModel = get_user_model() # pylint: disable=C0103


class Pilot(models.Model):
    """
    Extends user model with custom fields.
    """

    user = models.OneToOneField(UserModel)
    language = models.CharField(_("preferred language"),
        blank=False,
        max_length=2,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
        help_text=_("language in which messages in game and on the site will "
                    "be shown to user"))


@task
def create_pilot(sender, instance, created, **kwargs): # pylint: disable=W0613
    """
    Create pilot instance when user is created.
    """
    if created:
        dummy_pilot, dummy_created = Pilot.objects.get_or_create(user=instance)


@task
def delete_user(sender, instance=None, **kwargs): # pylint: disable=W0613
    """
    Delete user instance after deleting pilot.
    """
    try:
        instance.user
    except UserModel.DoesNotExist:
        pass
    else:
        instance.user.delete()


post_save.connect(create_pilot, sender=UserModel)
post_delete.connect(delete_user, sender=Pilot)
