# -*- coding: utf-8 -*-
"""
Different authentication backends.
"""
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from auth_custom.validators import validate_username


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
        UserModel = get_user_model() # pylint: disable=C0103

        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        kwargs = {}

        try:
            validate_email(username)
            kwargs.update({'email': username})
        except ValidationError:
            try:
                validate_username(username)
                kwargs.update({'username': username})
            except ValidationError:
                pass

        if kwargs:
            try:
                user = UserModel.objects.get(**kwargs)
                if user.check_password(password):
                    return user
            except UserModel.DoesNotExist:
                pass

        # Run the default password hasher once to reduce the timing
        # difference between an existing and a non-existing user (#20760).
        UserModel().set_password(password)
