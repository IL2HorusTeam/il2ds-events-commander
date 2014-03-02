# -*- coding: utf-8 -*-
"""
Commander's pilots service.
"""
from django.utils.translation import ugettext as _

from twisted.internet.task import LoopingCall

from il2ds_middleware.service import PilotBaseService

from commander import log
from commander.constants import UserCommand as Commands
from commander.service import CommanderServiceMixin

from pilots.models import Pilot
from pilots.settings import (PILOTS_PASSWORD_REQUESTS_COUNT,
    PILOTS_PASSWORD_REQUESTS_PERIOD, )


LOG = log.get_logger(__name__)


class OnlinePilot(object):
    """
    Base class for online pilots.
    """
    def __init__(self, pilot, client):
        self.pilot = pilot
        self.client = client


class PendingPilot(OnlinePilot):
    """
    Represents a pilot who still need to confirm connection password and will
    be kicked from the server after certain timeout.
    """
    def __init__(self, pilot, client):
        super(PendingPilot, self).__init__(pilot, client)
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
            LOG.debug("{0} has not entered password and will be kicked"
                     .format(self.pilot.callsign))
            self.client.kick_callsign(self.pilot.callsign)


class ActivePilot(OnlinePilot):
    """
    Represents a pilot who has successfully confirmed connection password.
    """
    def __init__(self, pilot, client):
        super(ActivePilot, self).__init__(pilot, client)

    @classmethod
    def from_online_pilot(cls, instance):
        return cls(instance.pilot, instance.client)


class PilotService(PilotBaseService, CommanderServiceMixin):
    """
    Custom service for managing online pilots.
    """
    # Dictionary which maps callsign to active pilots
    active = {}
    # Dictionary which maps callsign to pending pilots
    pending = {}

    def __init__(self):
        # Mapping of user commands to handlers
        self.command_handlers = {
            Commands.CONNECTION_INSTRUCTIONS: self.on_connection_instructions,
        }

    def user_joined(self, info):
        callsign = info['callsign']
        LOG.debug("{0} has joined".format(callsign))

        # Check callsign is free to use ---------------------------------------
        if self.is_callsign_used(callsign):
            LOG.debug(
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
            LOG.debug(
                "{0} is not registered and will be kicked".format(callsign))
            self.cl_client.chat_user(
                _("You are not registered. Please, create an account first."),
                callsign)
            self._delayed_kick(callsign)
            return

        # Kick user if connection is not allowed ------------------------------
        if not pilot.can_connect():
            LOG.debug("{0} hasn't requested connection and will be kicked"
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

    def _delayed_kick(self, callsign, delay=5):
        from twisted.internet import reactor
        reactor.callLater(delay, self.cl_client.kick_callsign, callsign)

    def user_left(self, info):
        callsign = info['callsign']
        LOG.debug("{0} has left".format(callsign))

        if callsign in self.pending:
            LOG.debug("Removing pending pilot {0}".format(callsign))
            pending = self.pending[callsign]
            pending.stop()
            pilot = pending.pilot
            del self.pending[callsign]
        elif callsign in self.active:
            LOG.debug("Removing active pilot {0}".format(callsign))
            # TODO: do all necessary clean up
            pilot = self.active[callsign].pilot
            del self.active[callsign]
        else:
            pilot = None

        if pilot:
            pilot.clear_password(update=True)

    def user_chat(self, (callsign, message)):
        online_pilot = self.get_online_pilot(callsign)

        if online_pilot is None:
            LOG.debug("Chat message from anonymous {0}: '{1}'".format(
                      callsign, message))
            self.cl_client.chat_user(
                _("Sorry, anonymous users are not allowed to use chat."),
                callsign)
            return

        try:
            command, args = Commands.decompose(message)
        except ValueError:
            LOG.debug(
                "Unknown command from {0}: '{1}'".format(callsign, message))
            with online_pilot.pilot.translator:
                self.cl_client.chat_user(_("Unknown command."), callsign)
            return

        if command:
            try:
                self.command_handlers[command](online_pilot, *args)
            except TypeError:
                LOG.debug("Invalid arguments for command '{0}' from {1}: '{2}'"
                          .format(command.value, callsign, ', '.join(args)))
                with online_pilot.pilot.translator:
                    self.cl_client.chat_user(
                        _("Invalid arguments for command '{command}'.").format(
                          command=command.value), callsign)
                return

    def get_online_pilot(self, callsign):
        if callsign in self.active:
            return self.active[callsign]
        elif callsign in self.pending:
            return self.pending[callsign]
        else:
            return None

    def on_connection_instructions(self, online_pilot, password):
        if isinstance(online_pilot, PendingPilot):
            self._process_password(online_pilot, password)
        elif isinstance(online_pilot, ActivePilot):
            pilot = online_pilot.pilot
            with pilot.translator:
                self.cl_client.chat_user(
                    _("Your password was already accepted. Happy flying!"),
                    pilot.callsign)
        else:
            LOG.error("Unknown instance of online pilot: {0}".format(
                       type(online_pilot)))

    def _process_password(self, online_pilot, password):
        pilot = online_pilot.pilot

        if online_pilot.pilot.check_password(password):
            LOG.debug("Activate {0}".format(pilot.callsign))

            self.pending[pilot.callsign].stop()
            del self.pending[pilot.callsign]

            active = ActivePilot.from_online_pilot(online_pilot)
            self.active[pilot.callsign] = active

            with pilot.translator:
                self.cl_client.chat_user(
                    _("Password accepted. Welcome to server!"), pilot.callsign)

            # TODO: process active pilot
        else:
            with pilot.translator:
                self.cl_client.chat_user(
                    _("Password does not match. Try again please."),
                    pilot.callsign)

    def stopService(self):
        # TODO: do all necessary clean up
        self.active.clear()
        self.pending.clear()
