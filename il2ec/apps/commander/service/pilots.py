# -*- coding: utf-8 -*-
"""
Commander's pilots service.
"""
import tx_logging

from django.utils.translation import ugettext as _

from twisted.internet import defer
from twisted.internet.task import LoopingCall

from il2ds_middleware.service import MutedPilotsService

from commander.constants import UserCommand as Commands
from commander.service import ClientServiceMixin

from auth_custom.models import User
from auth_custom.settings import (CONNECTION_PASSWORD_REQUESTS_COUNT,
    CONNECTION_PASSWORD_REQUESTS_PERIOD, )


LOG = tx_logging.getLogger(__name__)


class Pilot(object):
    """
    Base class for online pilots.
    """
    def __init__(self, user, client):
        self.user = user
        self.client = client


class PendingPilot(Pilot):
    """
    Represents a pilot who still need to confirm connection password and will
    be kicked from the server after certain timeout.
    """
    def __init__(self, user, client):
        super(PendingPilot, self).__init__(user, client)
        self.calls_left = CONNECTION_PASSWORD_REQUESTS_COUNT
        self.caller = LoopingCall(self.callback)

    def start(self):
        self.caller.start(CONNECTION_PASSWORD_REQUESTS_PERIOD)

    def stop(self):
        if self.caller.running:
            self.caller.stop()

    def callback(self):
        if self.calls_left:
            LOG.debug("Ask {0} for password".format(self.user.callsign))
            with self.user.translator:
                msg = _("{callsign}, please enter your password or you will "
                        "be kicked.").format(callsign=self.user.callsign)
            self.client.chat_user(msg, self.user.callsign)
            self.calls_left -= 1
        else:
            self.stop()
            LOG.debug("{0} has not entered password and will be kicked"
                     .format(self.user.callsign))
            self.client.kick_callsign(self.user.callsign)


class ConfirmedPilot(Pilot):
    """
    Represents a pilot who has successfully confirmed connection password.
    """
    def __init__(self, user, client):
        super(ConfirmedPilot, self).__init__(user, client)

        self.ping = 0
        self.score = 0
        self.army = None
        self.weapons = {}
        self.aircraft = {}
        self.position = {}

    @classmethod
    def from_pilot(cls, instance):
        return cls(instance.user, instance.client)


class PilotsService(MutedPilotsService, ClientServiceMixin):
    """
    Custom service for managing online pilots.
    """
    # Dictionary which maps callsign to confirmed pilots
    confirmed = {}
    # Dictionary which maps callsign to pending pilots
    pending = {}

    def __init__(self):
        # Mapping of user commands to handlers
        self.command_handlers = {
            Commands.CONNECTION_INSTRUCTIONS: self.on_connection_instructions,
        }
        self.info_collector = LoopingCall.withCount(self.collect_info)

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

        # Check whether user is registered ------------------------------------
        try:
            user = User.objects.get(callsign=callsign)
        except User.DoesNotExist:
            LOG.debug(
                "{0} is not registered and will be kicked".format(callsign))
            self.cl_client.chat_user(
                _("You are not registered. Please, create an account first."),
                callsign)
            self._delayed_kick(callsign)
            return

        # Kick user if connection is not allowed ------------------------------
        if not user.can_connect():
            LOG.debug("{0} hasn't requested connection and will be kicked"
                    .format(callsign))
            with user.translator:
                msg = _("{callsign}, you are not allowed to connect. Please, "
                        "request connection on the website.").format(
                         callsign=callsign)
            self.cl_client.chat_user(msg, callsign)
            self._delayed_kick(callsign)
            return

        # Create a pending pilot and kick user if no password was given during
        # certain period of time
        pending = PendingPilot(user, self.cl_client)
        self.pending[callsign] = pending
        pending.start()

    def is_callsign_used(self, callsign):
        return callsign in self.confirmed or callsign in self.pending

    def _delayed_kick(self, callsign, delay=10):
        from twisted.internet import reactor
        reactor.callLater(delay, self.cl_client.kick_callsign, callsign)

    @ClientServiceMixin.radar_refresher
    def user_left(self, info):
        callsign = info['callsign']
        LOG.debug("{0} has left".format(callsign))

        if callsign in self.pending:
            LOG.debug("Removing pending pilot {0}".format(callsign))
            self.pending[callsign].stop()
            del self.pending[callsign]

        elif callsign in self.confirmed:
            LOG.debug("Removing confirmed pilot {0}".format(callsign))
            del self.confirmed[callsign]
            if not self.confirmed:
                self.info_collector.stop()

    def user_chat(self, (callsign, message)):
        pilot = self.get_pilot(callsign)

        if pilot is None:
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
            with pilot.user.translator:
                self.cl_client.chat_user(_("Unknown command."), callsign)
            return

        if command:
            try:
                self.command_handlers[command](pilot, *args)
            except TypeError:
                LOG.debug("Invalid arguments for command '{0}' from {1}: '{2}'"
                          .format(command.value, callsign, ', '.join(args)))
                with pilot.user.translator:
                    self.cl_client.chat_user(
                        _("Invalid arguments for command '{command}'.").format(
                          command=command.value), callsign)
                return

    def get_pilot(self, callsign):
        if callsign in self.confirmed:
            return self.confirmed[callsign]
        elif callsign in self.pending:
            return self.pending[callsign]
        else:
            return None

    def on_connection_instructions(self, pilot, password):
        if isinstance(pilot, PendingPilot):
            self._process_password(pilot, password)
        elif isinstance(pilot, ConfirmedPilot):
            with pilot.user.translator:
                self.cl_client.chat_user(
                    _("Your password was already accepted. Happy flying!"),
                    pilot.user.callsign)

    def _process_password(self, pilot, password):
        user = pilot.user

        if user.check_connection_password(password):
            LOG.debug("Activate {0}".format(user.callsign))
            user.clear_connection_password(update=True)

            self.pending[user.callsign].stop()
            del self.pending[user.callsign]

            confirmed = ConfirmedPilot.from_pilot(pilot)
            self.confirmed[user.callsign] = confirmed

            with user.translator:
                self.cl_client.chat_user(
                    _("Password accepted. Welcome to server!"), user.callsign)

            if not self.info_collector.running:
                self.info_collector.start(3)
        else:
            with user.translator:
                self.cl_client.chat_user(
                    _("Wrong password. Try again please."), user.callsign)

    @defer.inlineCallbacks
    def collect_info(self, count):
        """
        `count` - the number of calls since last callback was invoked.
        """
        if count > 1:
            return

        all_infos = yield self.cl_client.users_common_info()
        all_statistics = yield self.cl_client.users_statistics()
        all_positions = yield self.dl_client.all_pilots_pos()
        all_positions = {
            data['callsign']: data['pos'] for data in all_positions
        }

        callsigns = set(all_infos.keys()).intersection(
                    set(all_statistics.keys())).intersection(
                    set(self.confirmed.keys()))

        for callsign in callsigns:
            pilot, info = self.confirmed[callsign], all_infos[callsign]

            pilot.ping = info['ping']
            pilot.score = info['score']

            if 'aircraft_code' in info:
                pilot.aircraft['code'] = info['aircraft_code']
                pilot.aircraft['designation'] = info['designation']
            else:
                pilot.aircraft.clear()

            pilot.weapons.update(all_statistics[callsign]['weapons'])

            if callsign in all_positions:
                pilot.position.update(all_positions[callsign])
            else:
                pilot.position.clear()

    @ClientServiceMixin.radar_refresher
    def weapons_loaded(self, info):
        pass

    @ClientServiceMixin.radar_refresher
    def was_killed(self, info):
        pass

    @ClientServiceMixin.radar_refresher
    def was_killed_by_user(self, info):
        pass

    @ClientServiceMixin.radar_refresher
    def shot_down_self(self, info):
        pass

    @ClientServiceMixin.radar_refresher
    def was_shot_down_by_user(self, info):
        pass

    @ClientServiceMixin.radar_refresher
    def was_shot_down_by_static(self, info):
        pass

    @ClientServiceMixin.radar_refresher
    def bailed_out(self, info):
        pass

    @ClientServiceMixin.radar_refresher
    def went_to_menu(self, info):
        pass

    def stopService(self):
        if self.info_collector.running:
            self.info_collector.stop()
        self.confirmed.clear()
        self.pending.clear()
