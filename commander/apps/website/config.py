# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from livesettings import config_register, ConfigurationGroup, StringValue
from django.utils.translation import ugettext_lazy as _

GENERIC_GROUP = ConfigurationGroup(
    'Generic',
    _("Generic Settings"),
    ordering=0
)

config_register(StringValue(
    GENERIC_GROUP,
    'PROJ_TITLE',
    description = _("Project title"),
    help_text = _("Name of your server and site."),
    default = _("My IL-2 FB project"),
    ordering = 0,
))

config_register(StringValue(
    GENERIC_GROUP,
    'PROJ_DESCR',
    description = _("Short project description"),
    help_text = _("Short description of your server and site."),
    default = _("Nice IL-2 FB project powered by Horus Commander"),
    ordering = 1,
))

config_register(StringValue(
    GENERIC_GROUP,
    'SERVER_PATH',
    description = _("Path to server"),
    help_text = _("Local path to your IL-2 FB server."),
    default = _("/opt/games/il2/server"),
    ordering = 2,
))
