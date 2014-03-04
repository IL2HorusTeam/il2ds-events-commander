# -*- coding: utf-8 -*-
"""
Implement 'create_superuser' Django management command.
"""
from django.conf import settings
from django.core.management.base import BaseCommand

from auth_custom.models import User


class Command(BaseCommand):
    """
    A management command which creates default superuser.
    """
    help = "Create default superuser"

    def handle(self, *args, **kwargs): # pylint: disable=W0613
        User.objects.create_superuser(
            first_name="Admin",
            callsign="admin",
            password="admin",
            email="admin@example.com",
            language=settings.LANGUAGE_CODE)
