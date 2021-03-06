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
    actions = ('resend_confirmation', )
    search_fields = ('email', 'confirmation_key', )
    list_display = ('email', 'expiration_date', )
    fields = (
        'email', 'confirmation_key', 'expiration_date', 'base_url',
        'language', )
    readonly_fields = ('email', 'confirmation_key', 'expiration_date', )

    def resend_confirmation(self, request, queryset):
        for sign_up_request in queryset:
            sign_up_request.send_email()
        self.message_user(request, _("Emails queued: {count}.").format(
                                     count=queryset.count()))
    resend_confirmation.short_description = _("Resend confirmation email")


admin.site.register(SignUpRequest, SignUpRequestAdmin)


class UserAdmin(BaseUserAdmin):
    """
    Description of admin for custom users model.
    """
    fieldsets = (
        (None, {'fields': (
            'callsign', 'email', 'password',
        )}),
        (_('Personal info'), {'fields': (
            'name', 'language',
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
            'fields': ('callsign', 'email', 'password1', 'password2', ),
        }),
    )
    list_display = ('callsign', 'email', 'name', 'is_staff')
    search_fields = ('callsign', 'name', 'email', )
    ordering = ('callsign', )

    form = UserChangeForm
    add_form = UserCreationForm


admin.site.register(User, UserAdmin)
