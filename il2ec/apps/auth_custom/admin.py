# -*- coding: utf-8 -*-
"""
Authentication admin classes.
"""
import logging

from django.contrib import admin

from auth_custom.models import SignUpRequest


LOG = logging.getLogger(__name__)


class SignUpRequestAdmin(admin.ModelAdmin):
    """
    Pass
    """
    search_fields = ('email', 'confirmation_key', )
    list_display = ('email', 'expiration_date', )
    fields = ('email', 'confirmation_key', 'created', 'expiration_date', )
    readonly_fields = ('email', 'confirmation_key', 'created', )


admin.site.register(SignUpRequest, SignUpRequestAdmin)
