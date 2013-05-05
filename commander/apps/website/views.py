# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from commons.views import BaseView

class IndexView(BaseView):
    """
    A view for a frontpage of the website.
    """
    template_name = "website/index.html"
