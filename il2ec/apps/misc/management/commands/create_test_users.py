# -*- coding: utf-8 -*-
"""
Implement 'create_test_users' Django management command.
"""
from django.conf import settings
from django.core.management.base import BaseCommand

from auth_custom.models import User


class Command(BaseCommand):
    """
    A management command which creates test users.
    """
    help = "Create test users"

    def handle(self, *args, **kwargs): # pylint: disable=W0613
        for i in range(10):
            callsign = "user{0}".format(i + 1)
            email = "{0}@example.com".format(callsign)

            User.objects.create_user(
                first_name=callsign.capitalize(),
                callsign=callsign,
                password=callsign,
                email=email,
                language=settings.LANGUAGE_CODE)
