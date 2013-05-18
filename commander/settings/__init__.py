import os

from django.conf import settings
from django.utils.importlib import import_module

def module_autodiscover(module_name):
    for app in settings.INSTALLED_APPS:
        try:
            import_module('%s.%s' % (app, module_name))
        except:
            continue

module_autodiscover("config")
