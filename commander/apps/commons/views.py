# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.views.generic import TemplateView
from coffin.shortcuts import render

from website.config import get_project_title

LOG = logging.getLogger(__name__)

class BaseView(TemplateView):
    """
    Like the built in TemplateView, but adds self.extra_context dictionary
    and sets request to self.request
    """
    def __init__(self, *args, **kwargs):
        self.extra_context = {}
        super(BaseView, self).__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        return super(BaseView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.extra_context.update({
            'PROJ_TITLE': get_project_title(request.LANGUAGE_CODE),
        })
        return render(request, self.template_name, self.extra_context)
