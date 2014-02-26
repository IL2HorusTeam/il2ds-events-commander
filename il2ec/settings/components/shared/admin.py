# -*- coding: utf-8 -*-
"""
Base settings for admin panel shared by all environments.
"""
from django.utils.translation import ugettext_lazy as _


GRAPPELLI_ADMIN_TITLE = _("{0} admin").format(PROJECT_NAME)
GRAPPELLI_INDEX_DASHBOARD = 'website.dashboard.CustomIndexDashboard'
