# -*- coding: utf-8 -*-
"""
Implement 'create_superuser' Django management command.
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    A management command which creates default superuser.
    """
    help = "Create default superuser"

    def handle(self, *args, **kwargs): # pylint: disable=W0613
        UserModel = get_user_model() # pylint: disable=C0103
        UserModel.objects.create_superuser(
            username="admin",
            password="admin",
            email="admin@foo.bar",
            language=settings.LANGUAGE_CODE)
