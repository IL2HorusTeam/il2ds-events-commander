# -*- coding: utf-8 -*-
"""
Miscellaneous validators.
"""
import re

from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _


class SHA1Validator(RegexValidator):
    """
    SHA1 HEX digests validator.
    """
    regex = re.compile(r'^[a-f0-9]{40}$')
    message = _("Enter a valid SHA1 HEX digest.")
