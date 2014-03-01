# -*- coding: utf-8 -*-
"""
Commander's pilots service.
"""
from django.utils.translation import ugettext_lazy as _

from il2ds_middleware.service import PilotBaseService

from commander import log
from commander.service import CommanderServiceMixin

from pilots.models import Pilot


LOG = log.get_logger(__name__)


class PilotService(PilotBaseService, CommanderServiceMixin):
    """
    Custom service for managing in-game pilots.
    """
    def __init__(self):
        pass

    def user_joined(self, info):
        username = info['callsign']
        LOG.debug("{username} joined server".format(username=username))

        try:
            pilot = Pilot.objects.get(user__username=username)
        except Pilot.DoesNotExist:
            self.cl_client.chat_user(
                _("You are not registered. Please, register first."), username)
            self._delayed_kick(username)
            return

    def user_left(self, info):
        username = info['callsign']
        LOG.debug("{username} left server".format(username=username))
        # TODO:

    def _delayed_kick(self, callsign, delay=5):
        from twisted.internet import reactor
        reactor.callLater(delay, self.cl_client.kick_callsign, callsign)
