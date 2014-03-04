# -*- coding: utf-8 -*-
"""
Authentication-related validators.
"""
import re

from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _


class CallsignValidator(RegexValidator):
    """
    Checks callsign for validity.
    """
    regex = re.compile(r'^[\w.@()\[\]{}=+-]{2,30}$')
    message = _("Callsign may contain only 2 to 30 letters, numbers and "
                "@/./+/-/=/_/(/)/[/]/{/} characters.")


validate_callsign = CallsignValidator()
