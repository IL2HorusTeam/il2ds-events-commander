# -*- coding: utf-8 -*-
"""
Different authentication backends.
"""
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


LOG = logging.getLogger(__name__)
UserModel = get_user_model() # pylint: disable=C0103


class CustomModelBackend(ModelBackend):
    """
    Custom model authentication backend with support of using email as
    username.
    """

    def authenticate(self, username=None, password=None, **kwargs):
        """
        Redefine mathod of the base class. Username can contain email address.
        """
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        kwargs = {
            'email': username,
        } if '@' in username else {
            'username': username,
        }
        try:
            user = UserModel.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
