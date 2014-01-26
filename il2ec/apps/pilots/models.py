# -*- coding: utf-8 -*-
"""
Pilot database models.
"""
from celery.decorators import task

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext_lazy as _


User = get_user_model()


class Pilot(models.Model):
    user = models.OneToOneField(User)
    language = models.CharField(_("preferred language"),
        blank=False,
        max_length=2,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
        help_text=_("language in which messages in game and on the site will "
                    "be shown to user"))


@task
def create_pilot(sender, instance, created, **kwargs):
    """
    Create pilot instance when user is created.
    """
    if created:
        Pilot.objects.create(user=instance)


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
