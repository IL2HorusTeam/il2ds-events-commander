# -*- coding: utf-8 -*-
"""
Different authentication backends.
"""
import logging

from django.contrib.auth.backends import ModelBackend
from auth_custom.models import User


LOG = logging.getLogger(__name__)


class CustomModelBackend(ModelBackend):
    """
    Custom model authentication backend with support of using email as
    username.
    """
    def authenticate(self, username=None, password=None, **kwargs):
        """
        Redefine method of the base class. Username can contain email address.
        """
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)

        try:
            user = User.objects.get_by_callsign_or_email(username)
            if user.check_password(password):
                return user
        except ValueError:
            pass
        except User.DoesNotExist:
            pass

        # Run the default password hasher once to reduce the timing
        # difference between an existing and a non-existing user (#20760).
        User().set_password(password)
