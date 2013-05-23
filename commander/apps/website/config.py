# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from xlivesettings import (
    config_register_list,
    ConfigurationGroup, LocalizedStringValue
)

#-------------------------------------------------------------------------------
# Config keys
#-------------------------------------------------------------------------------

PROJECT_GROUP_KEY = 'PROJ'

TITLE_KEY = 'TITLE'
DESCR_KEY = 'DESCR'

#-------------------------------------------------------------------------------
# Groups
#-------------------------------------------------------------------------------

PROJECT_GROUP = ConfigurationGroup(
    PROJECT_GROUP_KEY,
    _(u"Project settings"),
    ordering = 0,
)

#-------------------------------------------------------------------------------
# Configs
#-------------------------------------------------------------------------------

config_register_list(
    LocalizedStringValue(
        PROJECT_GROUP,
        TITLE_KEY,
        description = _(u"Project title"),
        help_text = _(u"Name of your server and site"),
        default = (
            ('en', u"My IL-2 FB project"),
            ('ru', u"Мой проект Ил-2 ЗС"),
        ),
        ordering = 0,
    ),
    LocalizedStringValue(
        PROJECT_GROUP,
        DESCR_KEY,
        description = _(u"Short project description"),
        help_text = _(u"Short description of your server and site"),
        default = (
            ('en', u"Nice IL-2 FB project powered by Horus Commander"),
            ('ru', u"Хороший проект Ил-2 ЗС, управляемый с помощью Хорус Коммандера"),
        ),
        ordering = 1,
    ),
)
