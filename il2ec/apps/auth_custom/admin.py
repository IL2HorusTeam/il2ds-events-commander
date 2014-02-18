# -*- coding: utf-8 -*-
"""
Authentication admin classes.
"""
import logging

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _

from auth_custom.forms import UserCreationForm, UserChangeForm
from auth_custom.models import SignUpRequest, User


LOG = logging.getLogger(__name__)


class SignUpRequestAdmin(admin.ModelAdmin):
    """
    Description of admin for sign up requests.
    """
    search_fields = ('email', 'confirmation_key', )
    list_display = ('email', 'expiration_date', )
    fields = ('email', 'confirmation_key', 'created', 'expiration_date', )
    readonly_fields = ('email', 'confirmation_key', 'created', )


admin.site.register(SignUpRequest, SignUpRequestAdmin)


class UserAdmin(BaseUserAdmin):
    """
    Description of admin for custom users model.
    """
    fieldsets = (
        (None, {'fields': (
            'username', 'email', 'password',
        )}),
        (_('Personal info'), {'fields': (
            'first_name', 'last_name', 'language',
        )}),
        (_('Permissions'), {'fields': (
            'is_active', 'is_blocked', 'is_staff', 'is_superuser', 'groups',
            'user_permissions',
        )}),
        (_('Important dates'), {'fields': (
            'last_login', 'date_joined',
        )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': ('username', 'email', 'password1', 'password2')}
        ),
    )
    form = UserChangeForm
    add_form = UserCreationForm


admin.site.register(User, UserAdmin)
