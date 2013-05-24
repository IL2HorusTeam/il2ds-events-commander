# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

from game_server import process_manager

LOG = logging.getLogger(__name__)

@csrf_protect
def server_admin_index(request, template="game_server/admin/index.html"):
    if request.method == 'POST':
        if request.POST.has_key("_start"):
            process_manager.start()
        elif request.POST.has_key("_stop"):
            process_manager.stop()
        elif request.POST.has_key("_restart"):
            process_manager.restart()
        messages.add_message(request, *process_manager.get_message())

    data = {
        'title': _(u"Server management"),
    }
    fill_server_status(data)
    return render_to_response(template, data, context_instance=RequestContext(request))

def server_status(request):
    if not request.is_ajax():
        return HttpResponseBadRequest()

    last_update_time = request.GET.get('l_upd_time', '0')

    current_update_time = process_manager.get_status_update_time()
    if current_update_time:
        current_update_time = current_update_time.strftime('%s')
    else:
        current_update_time = '0'

    if last_update_time == current_update_time:
        data = {
            'result': 'error',
        }
    else:
        data = {
            'result': 'success',
            'l_upd_time': current_update_time
        }
        fill_server_status(data)
    json = simplejson.dumps(data)
    return HttpResponse(json, mimetype="application/json")

def fill_server_status(data):
    status = process_manager.get_status()
    worktime = process_manager.get_worktime()
    data.update(
        {
            'status_code': status,
            'status_verb': unicode(process_manager.PROCESS_STATUSES[status]),
            'crashes': process_manager.get_crash_count(),
            'starting': 1 if status == process_manager.PROCESS_STATUS_STARTING else 0,
            'waiting': 1 if status == process_manager.PROCESS_STATUS_WAITING else 0,
            'worktime': worktime.seconds if worktime else 0,
        }
    )
