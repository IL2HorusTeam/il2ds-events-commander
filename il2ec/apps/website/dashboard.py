# -*- coding: utf-8 -*-
"""
Admin dashboard configuration.
"""
from django.utils.translation import ugettext_lazy as _

from grappelli.dashboard import modules, Dashboard


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for admin.
    """
    def init_with_context(self, context):
        self.children.append(modules.AppList(
            _("Applications"),
            collapsible=True,
            column=1,
            css_classes=('collapse closed',),
            exclude=('django.contrib.*',),
        ))

        self.children.append(modules.ModelList(
            _("Users"),
            column=1,
            collapsible=False,
            models=(
                'django.contrib.auth.models.Group',
                'django.contrib.auth.models.User',
                'auth_custom.models.SignUpRequest',
            ),
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(
            _("Recent Actions"),
            limit=5,
            collapsible=False,
            column=3,
        ))


