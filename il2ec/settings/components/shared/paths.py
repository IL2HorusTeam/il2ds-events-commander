# -*- coding: utf-8 -*-
"""
Path settings shared by all environments.
"""
import os
import sys
import warnings

import il2ec as project_module


PYTHON_BIN = os.path.dirname(sys.executable)
PROJECT_DIR = os.path.dirname(os.path.realpath(project_module.__file__))

APPS_ROOT = os.path.join(PROJECT_DIR, 'apps')
# Add apps root dir to pythonpath
sys.path.append(APPS_ROOT)

LOCALE_PATHS = (
    os.path.join(PROJECT_DIR, 'locale'),
)

VAR_ROOT = os.path.join(PROJECT_DIR, 'var')
LOG_ROOT = os.path.join(VAR_ROOT, 'log')

try:
    if not os.path.exists(VAR_ROOT):
        os.mkdir(VAR_ROOT)
    if not os.path.exists(LOG_ROOT):
        os.mkdir(LOG_ROOT)
except OSError:
    pass


# Disable deprecation warnings for sake of clean output
warnings.filterwarnings("ignore", category=DeprecationWarning)
