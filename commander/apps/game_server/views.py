# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from game_server import process_manager

def server_admin_index(request, template="game_server/admin/index.html"):
    if request.method == 'POST':
        if request.POST.has_key("_start"):
            process_manager.start()
        elif request.POST.has_key("_stop"):
            process_manager.stop()
        elif request.POST.has_key("_restart"):
            process_manager.restart()
        messages.add_message(request, *process_manager.get_message())

    status = process_manager.get_status()
    data = {
        'title': _(u"Server management"),
        'status_code': status,
        'status_verb': process_manager.PROCESS_STATUSES[status],
        'crashes': process_manager.get_crash_count(),
        'starting': status == process_manager.PROCESS_STATUS_STARTING,
        'waiting': status == process_manager.PROCESS_STATUS_WAITING,
        'workime': process_manager.get_workime(),
    }
    return render_to_response(template, data, context_instance=RequestContext(request))
