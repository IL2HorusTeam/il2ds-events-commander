# -*- coding: utf-8 -*-
"""
Path settings for staging environment.
"""
import os


VAR_ROOT = os.path.join(
    os.path.expanduser('~'), '.virtualenvs', 'il2ec', 'var')
LOG_ROOT = os.path.join(VAR_ROOT, 'log')

try:
    if not os.path.exists(VAR_ROOT):
        os.mkdir(VAR_ROOT)
    if not os.path.exists(LOG_ROOT):
        os.mkdir(LOG_ROOT)
except OSError:
    pass
