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
        self.update_context(request, *args, **kwargs)
        return render(request, self.template_name, self.extra_context)

    def update_context(self, request, *args, **kwargs):
        # Get path to current page without leading language code
        full_path = request.get_full_path()
        self.extra_context.update({
            'current_path': full_path[full_path.index('/', 1):],
        })


class IndexView(BaseView):
    """
    View for the site frontpage.
    """
    template_name = "website/pages/index.html"

