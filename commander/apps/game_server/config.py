# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from xlivesettings import (
    config_register_list,
    ConfigurationGroup, PositiveIntegerValue, StringValue
)

#-------------------------------------------------------------------------------
# Config keys
#-------------------------------------------------------------------------------

SERVER_GROUP_KEY = 'SERVER'

PATH_KEY = 'PATH'
RESTART_DELAY_KEY = 'RESTART_DELAY'

#-------------------------------------------------------------------------------
# Groups
#-------------------------------------------------------------------------------

SERVER_GROUP = ConfigurationGroup(
    SERVER_GROUP_KEY,
    _(u"Server settings"),
    ordering = 1,
)

#-------------------------------------------------------------------------------
# Configs
#-------------------------------------------------------------------------------

config_register_list(
    StringValue(
        SERVER_GROUP,
        PATH_KEY,
        description = _(u"Path to server"),
        help_text = _(u"Local path to your IL-2 FB server"),
        default = "/opt/games/il2/server",
        ordering = 0,
    ),
    PositiveIntegerValue(
        SERVER_GROUP,
        RESTART_DELAY_KEY,
        description = _(u"Restart delay, ms"),
        help_text = _(u"Delay in milliseconds before server restart after crash (if happenned)"),
        default = 5000,
        min_value = 1000,
        ordering = 1,
    ),
)
