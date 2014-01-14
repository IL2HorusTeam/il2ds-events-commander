# -*- coding: utf-8 -*-
"""
Implement 'create_superuser' Django management command.
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    A management command which creates default superuser.
    """
    help = "Create default superuser"

    def handle(self, *args, **kwargs):
        admin = User.objects.create_superuser(
            username="admin",
            password="admin",
            email="admin@foo.bar")
