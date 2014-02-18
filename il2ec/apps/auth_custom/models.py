# -*- coding: utf-8 -*-
"""
Authentication models.
"""
import datetime
import logging
import warnings

from django.conf import settings

from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
    UserManager as BaseUserManager, )
from django.contrib.auth.signals import user_logged_in

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from django.db import models
from django.dispatch import receiver

from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _

from auth_custom.helpers import sign_up_confirmation, update_current_language
from auth_custom.settings import EMAIL_CONFIRMATION_DAYS
from auth_custom.validators import validate_username

from misc.exceptions import ObjectAlreadyExistsError


LOG = logging.getLogger(__name__)


class SignUpRequestManager(models.Manager): # pylint: disable=R0904
    """
    Sign-up requests manager.
    """
    def create_from_email(self, email):
        """
        Create and return sign up request for specified email address.
        Raise 'AlreadyExists' exception, if unexpired sign up request already
        exists for specified email.
        """
        now = timezone.now()

        if self.filter(email=email, expiration_date__gt=now).exists():
            raise self.model.AlreadyExists(
                _("Sign up request for {email} already exists.").format(
                  email=email))

        expiration_date = now + datetime.timedelta(
                                    days=EMAIL_CONFIRMATION_DAYS)
        confirmation_key = sign_up_confirmation.generate_key(email,
                                                             unicode(now))

        return self.model(email=email, confirmation_key=confirmation_key,
                          created=now, expiration_date=expiration_date)

    def get_unexpired(self, email, confirmation_key):
        """
        Get unexpired sign up request for specified email and confirmation key
        or 'None'.
        """
        now = timezone.now()
        try:
            return self.filter(email=email, confirmation_key=confirmation_key,
                               expiration_date__gt=now)[:1].get()
        except self.model.DoesNotExist:
            return None

    def delete_expired(self):
        """
        Delete all expired sign up requests.
        """
        self.filter(expiration_date__lt=timezone.now()).delete()


class SignUpRequest(models.Model):
    """
    Model for storing sign-up requests. There can be several requests for one
    email, but there can be only one unexpired request.
    """
    AlreadyExists = ObjectAlreadyExistsError

    email = models.EmailField(
        verbose_name=_("email"),
        unique=False)
    confirmation_key = models.CharField(
        verbose_name=_("confirmation key"),
        max_length=40)
    created = models.DateTimeField(
        verbose_name=_("created"),
        default=timezone.now)
    expiration_date = models.DateTimeField(
        verbose_name=_("expiration date"))

    objects = SignUpRequestManager()

    class Meta:
        verbose_name = _("sign up request")
        verbose_name_plural = _("sign up requests")
        ordering = ['-expiration_date', 'email']

    def __unicode__(self):
        return _("Sign up request for {email}").format(email=self.email)


class UserManager(BaseUserManager):
    """
    Custom menager for User model.
    """
    def get_by_username_or_email(self, username_email):
        """
        Try to get user instance by username or email.
        """
        try:
            validate_email(username_email)
            kwargs = {'email': username_email}
        except ValidationError:
            try:
                validate_username(username_email)
                kwargs = {'username': username_email}
            except ValidationError:
                raise ValueError(_("Invalid username or email."))

        return self.get(**kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom users model. Username, password and email are required.
    Other fields are optional.
    """
    username = models.CharField(
        verbose_name=_("username"),
        max_length=30,
        unique=True,
        help_text=validate_username.message,
        validators=[
            validate_username,
        ])
    first_name = models.CharField(
        verbose_name=_("first name"),
        max_length=30,
        blank=True)
    last_name = models.CharField(
        verbose_name=_("last name"),
        max_length=30,
        blank=True)
    email = models.EmailField(
        verbose_name=_("email address"),
        unique=True,
        blank=False)
    is_staff = models.BooleanField(
        verbose_name=_("staff status"),
        default=False,
        help_text=_("Designates whether the user can sign into this admin "
                    "site."))
    is_active = models.BooleanField(
        verbose_name=_("active"),
        default=True,
        help_text=_("Designates whether this user should be treated as "
                    "active. Unselect this instead of deleting accounts. "
                    "Inactive users can sign in to reactivate their "
                    "accounts."))
    is_blocked = models.BooleanField(
        verbose_name=_("blocked"),
        default=False,
        help_text=_("Designates whether this user is blocked. Blocked users "
                    "can not sign in without intervention of administration."))
    date_joined = models.DateTimeField(
        verbose_name=_("date joined"),
        default=timezone.now)
    language = models.CharField(
        verbose_name=_("preferred language"),
        blank=False,
        max_length=5,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
        help_text=_("Language in which messages will be shown to user in game"
                    "chat and at this website."))

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.username)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name (if present).
        """
        if self.last_name:
            full_name = '%s %s' % (self.first_name, self.last_name)
            return full_name.strip()
        else:
            return self.first_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def get_profile(self):
        """
        Returns site-specific profile for this user. Raises
        SiteProfileNotAvailable if this site does not allow profiles.
        """
        warnings.warn("The use of AUTH_PROFILE_MODULE to define user profiles "
                      "has been deprecated.", DeprecationWarning, stacklevel=2)
        if not hasattr(self, '_profile_cache'):
            from django.conf import settings
            if not getattr(settings, 'AUTH_PROFILE_MODULE', False):
                raise SiteProfileNotAvailable(
                    "You need to set AUTH_PROFILE_MODULE in your project "
                    "settings")
            try:
                app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
            except ValueError:
                raise SiteProfileNotAvailable(
                    "app_label and model_name should be separated by a dot in "
                    "the AUTH_PROFILE_MODULE setting")
            try:
                model = models.get_model(app_label, model_name)
                if model is None:
                    raise SiteProfileNotAvailable(
                        "Unable to load the profile model, check"
                        "AUTH_PROFILE_MODULE in your project settings")
                self._profile_cache = model._default_manager.using(
                                   self._state.db).get(user__id__exact=self.id)
                self._profile_cache.user = self
            except (ImportError, ImproperlyConfigured):
                raise SiteProfileNotAvailable
        return self._profile_cache


@receiver(user_logged_in)
def set_preferred_language(sender, **kwargs):
    """
    Called when a user signs in. Sets current language to preferred.
    """
    update_current_language(request=kwargs['request'],
                            language=kwargs['user'].language)
