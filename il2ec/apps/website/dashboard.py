# -*- coding: utf-8 -*-
"""
Admin dashboard configuration.
"""
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for admin.
    """
    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

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
            models=('django.contrib.auth.*',),
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(
            _("Recent Actions"),
            limit=5,
            collapsible=False,
            column=3,
        ))


