# -*- coding: utf-8 -*-
"""
Main project views.
"""
import logging

from coffin.shortcuts import render
from django.views.generic import TemplateView


LOG = logging.getLogger(__name__)


class BaseView(TemplateView):
    """
    Extended TemplateView which provides self.extra_context dictionary and
    stores request at self.request.
    """
    def __init__(self, *args, **kwargs):
        self.extra_context = {}
        super(BaseView, self).__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        return super(BaseView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.extra_context)


class IndexView(BaseView):
    """
    View for the site frontpage.
    """
    template_name = "website/pages/index.html"
