# -*- coding: utf-8 -*-
"""
Main project views.
"""
import logging

from celery.result import AsyncResult

from coffin.shortcuts import render, resolve_url
from coffin.views.generic import TemplateView

from django.conf import settings
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext as _

from misc.tasks import send_mail

from website.forms import AnonymousContactForm, ContactForm
from website.decorators import ajax_api
from website.responses import JSONResponse


LOG = logging.getLogger(__name__)


class BaseView(TemplateView):
    """
    Extended TemplateView which provides self.extra_context dictionary and
    stores request at self.request.
    """
    def __init__(self, *args, **kwargs):
        self.request = None
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


class PageNotFoundView(BaseView):
    """
    View for not existing page.
    """
    template_name = "404.html"

    def get(self, request, *args, **kwargs):
        response = super(PageNotFoundView, self).get(request, *args, **kwargs)
        response.status_code = 404
        return response


class ServerErrorView(BaseView):
    """
    View for reporting about internal server error.
    """
    template_name = "500.html"

    def get(self, request, *args, **kwargs):
        response = super(ServerErrorView, self).get(request, *args, **kwargs)
        response.status_code = 500
        return response


@ajax_api(method='GET')
def api_task_result(request, task_id):
    """
    View which handles AJAX GET requests for getting results of Celery tasks.
    """
    result = AsyncResult(task_id)
    if result.status == 'PENDING':
        return JSONResponse.error(message=_("Unknown task ID."))
    else:
        return JSONResponse.success(payload={
            'ready': result.ready(),
            'result': result.get(),
        })


def contact(request, template_name="website/pages/contact.html"):
    """
    A view for sending messages to support team.
    """
    if not request.method == 'GET':
        return HttpResponseBadRequest()

    form_class = AnonymousContactForm if request.user.is_anonymous() else \
                 ContactForm
    context = {
        'form': form_class(),
    }
    return render(request, template_name, context)


@ajax_api()
@csrf_protect
def api_contact(request, template_name='website/emails/contact.html'):
    """
    Handles AJAX POST requests for sending messages to support team.
    """
    form_class = AnonymousContactForm if request.user.is_anonymous() else \
                 ContactForm
    form = form_class(data=request.POST)

    if form.is_valid():
        if request.user.is_anonymous():
            email, name = form.cleaned_data['email'], form.cleaned_data['name']
        else:
            email, name = request.user.email, request.user.get_full_name()

        subject = u"[{prefix}] {subject}".format(
                  prefix=_("support"), subject=form.cleaned_data['subject'])
        to_emails = [address for (_name, address) in settings.SUPPORTERS]

        if form.cleaned_data['send_copy']:
            to_emails.append(email)

        home_url = request.build_absolute_uri(resolve_url('website-index'))
        context = {
            'host_address': home_url,
            'host_name': settings.PROJECT_NAME,
            'body': form.cleaned_data['body'],
            'name': name,
            'email': email,
        }

        async_result = send_mail.delay(subject, template_name, context,
                                       to_emails=to_emails,
                                       language_code=request.LANGUAGE_CODE)

        return JSONResponse.success(payload={
            'task_id': async_result.id,
        })
    else:
        return JSONResponse.form_field_errors(form)
