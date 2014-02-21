# -*- coding: utf-8 -*-
"""
Additional web responses.
"""
import itertools
import logging
import simplejson as json

from django.http import HttpResponse
from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)


class JSONResponse(HttpResponse):
    """
    Http response with JSON inside used foremost for AJAX requests.
    """

    def __init__(self, data, mimetype="application/json"):
        super(JSONResponse, self).__init__(content=json.dumps(data),
                                           mimetype=mimetype)

    @classmethod
    def success(cls, message=None, payload=None):
        """
        Create a response for succeeded operation.
        """
        data = {
            'status': 'success',
            'message': message or _("Success")
        }
        if isinstance(payload, dict):
            data.update(payload)
        return cls(data)

    @classmethod
    def error(cls, code=None, message=None, payload=None):
        """
        Create a response for failed operation.
        """
        data = {
            'status': 'fail',
            'error': {
                'code': code or -1,
                'message': message or _("Failure"),
            }
        }
        if isinstance(payload, dict):
            data.update(payload)
        return cls(data)

    @classmethod
    def form_error(cls, form, code=None, payload=None):
        """
        Create a response for invalid form with non-field errors.
        """
        msg = ' '.join(itertools.chain(*form.errors.values()))
        return cls.error(message=unicode(msg), code=code, payload=payload)

    @classmethod
    def form_field_errors(cls, form, message=None, code=None, payload=None):
        """
        Create a response for invalid form with field errors.
        """
        errors = {
            field_name: ' '.join([unicode(e) for e in error_list])
                        for field_name, error_list in form.errors.items()
        }
        payload = payload or {}
        payload.update({
            'errors': errors,
        })
        return cls.error(message=message, code=code, payload=payload)
