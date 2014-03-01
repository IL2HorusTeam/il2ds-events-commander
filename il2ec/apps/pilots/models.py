# -*- coding: utf-8 -*-
"""
Pilot database models.
"""
from celery.task import task

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext_lazy as _

from auth_custom.models import User


class Pilot(models.Model):
    """
    Adds pilot-related fields to User model.
    """
    user = models.OneToOneField(User)
    password = models.CharField(
        verbose_name=_("password"),
        max_length=128,
        help_text=_("one time password for connecting to game server"))


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
