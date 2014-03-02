# -*- coding: utf-8 -*-
"""
Commander's pilots service.
"""
from django.utils.translation import ugettext as _

from twisted.internet.task import LoopingCall

from il2ds_middleware.service import PilotBaseService

from commander import log
from commander.service import CommanderServiceMixin

from pilots.models import Pilot
from pilots.settings import (PILOTS_PASSWORD_REQUESTS_COUNT,
    PILOTS_PASSWORD_REQUESTS_PERIOD, )


LOG = log.get_logger(__name__)


class PendingPilot(object):

    def __init__(self, pilot, client):
        self.pilot = pilot
        self.client = client
        self.calls_left = PILOTS_PASSWORD_REQUESTS_COUNT
        self.caller = LoopingCall(self.callback)

    def start(self):
        self.caller.start(PILOTS_PASSWORD_REQUESTS_PERIOD)

    def stop(self):
        if self.caller.running:
            self.caller.stop()

    def callback(self):
        if self.calls_left:
            LOG.debug("Ask {0} for password".format(self.pilot.callsign))
            with self.pilot.translator:
                msg = _("{callsign}, please enter your password or you will "
                        "be kicked.").format(callsign=self.pilot.callsign)
            self.client.chat_user(msg, self.pilot.callsign)
            self.calls_left -= 1
        else:
            self.stop()
            LOG.info("{0} has not entered password and will be kicked"
                     .format(self.pilot.callsign))
            self.pilot.clear_password()
            self.pilot.save()
            self.client.kick_callsign(self.pilot.callsign)


class PilotService(PilotBaseService, CommanderServiceMixin):
    """
    Custom service for managing online pilots.
    """
    # Dictionary of pilots who has passed connection check and can fly.
    active = {}
    # Dictionary of pilots who has just joined and needs to enter a password.
    pending = {}

    def user_joined(self, info):
        callsign = info['callsign']
        LOG.debug("{0} has joined".format(callsign))

        # Check callsign is free to use ---------------------------------------
        if self.is_callsign_used(callsign):
            LOG.info(
                "Callsign {0} is already used".format(callsign))
            self.cl_client.chat_user(
                _("{callsign}, your callsign is already used.").format(
                   callsign=callsign), callsign)
            self.cl_client.kick_callsign(callsign)
            return

        # Check user is registered --------------------------------------------
        try:
            pilot = Pilot.objects.get(user__username=callsign)
        except Pilot.DoesNotExist:
            LOG.info(
                "{0} is not registered and will be kicked".format(callsign))
            self.cl_client.chat_user(
                _("You are not registered. Please, create an account first."),
                callsign)
            self._delayed_kick(callsign)
            return

        # Kick user if connection is not allowed ------------------------------
        if not pilot.can_connect():
            LOG.info("{0} hasn't requested connection and will be kicked"
                    .format(callsign))
            with pilot.translator:
                msg = _("{callsign}, you are not allowed to connect. Please, "
                        "request connection on the website.").format(
                         callsign=callsign)
                self.cl_client.chat_user(msg, callsign)
            self._delayed_kick(callsign)
            return

        # Create a pending pilot and kick user if no password was given during
        # certain period of time
        pending = PendingPilot(pilot, self.cl_client)
        self.pending[callsign] = pending
        pending.start()

    def is_callsign_used(self, callsign):
        return callsign in self.active or callsign in self.pending

    def _delayed_kick(self, callsign, delay=10):
        from twisted.internet import reactor
        reactor.callLater(delay, self.cl_client.kick_callsign, callsign)

    def user_left(self, info):
        callsign = info['callsign']
        LOG.debug("{0} has left".format(callsign))

        # Check if pilot was in pending state ---------------------------------
        if callsign in self.pending:
            LOG.debug("Removing pending pilot {0}".format(callsign))
            pending = self.pending[callsign]
            pending.stop()
            del pending

    def stopService(self):
        # TODO: do all necessary clean up
        self.active.clear()
        self.pending.clear()
