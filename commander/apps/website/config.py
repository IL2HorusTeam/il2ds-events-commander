# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from livesettings import config_register, ConfigurationGroup, StringValue
from django.utils.translation import ugettext_lazy as _

GENERIC_GROUP = ConfigurationGroup(
    'Generic',
    _(u"Generic settings"),
    ordering=0
)

config_register(StringValue(
    GENERIC_GROUP,
    'PROJ_TITLE',
    description = _(u"Project title"),
    help_text = _(u"Name of your server and site"),
    default = _(u"My IL-2 FB project"),
    ordering = 0,
))

config_register(StringValue(
    GENERIC_GROUP,
    'PROJ_DESCR',
    description = _(u"Short project description"),
    help_text = _(u"Short description of your server and site"),
    default = _(u"Nice IL-2 FB project powered by Horus Commander"),
    ordering = 1,
))

config_register(StringValue(
    GENERIC_GROUP,
    'SERVER_PATH',
    description = _(u"Path to server"),
    help_text = _(u"Local path to your IL-2 FB server"),
    default = "/opt/games/il2/server",
    ordering = 2,
))
