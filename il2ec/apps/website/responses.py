# -*- coding: utf-8 -*-
import simplejson as json

from django.http import HttpResponse
from django.utils.translation import ugettext as _


class JSONResponse(HttpResponse):
    """
    Http response with JSON inside used foremost for AJAX requests.
    """
    def __init__(self, data, mimetype="application/json"):
        super(JSONResponse, self).__init__(content=json.dumps(data),
                                           mimetype=mimetype)

    @classmethod
    def success(cls, message=None, payload=None):
        data = {
            'status': 'success',
            'message': message or _("Success")
        }
        if isinstance(payload, dict):
            data.update(payload)
        return cls(data)

    @classmethod
    def error(cls, code=None, message=None):
        data = {
            'status': 'fail',
            'error': {
                'code': code or -1,
                'message': message or _("Failure"),
            }
        }
        return cls(data)
