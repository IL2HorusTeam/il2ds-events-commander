# -*- coding: utf-8 -*-
"""
Pilot views.
"""
import logging

from django.contrib.auth.decorators import login_required

from commander.constants import UserCommand

from website.decorators import ajax_api
from website.responses import JSONResponse


LOG = logging.getLogger(__name__)


@ajax_api(method='GET')
@login_required
def api_request_connection(request):
    password = request.user.pilot.create_password(update=True)
    return JSONResponse.success(payload={
        'command': UserCommand.CONNECTION_INSTRUCTIONS.render(password),
    })
