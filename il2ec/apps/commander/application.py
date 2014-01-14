# -*- coding: utf-8 -*-
"""
Commander as twisted application.
"""
from twisted.application import service
from commander.service import Commander


application = service.Application("IL-2 Events Commander")
commander = Commander()
commander.setServiceParent(application)
