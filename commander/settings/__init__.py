import os

from django.conf import settings
from django.utils.importlib import import_module

def module_autodiscover(module_name):
    for app in settings.INSTALLED_APPS:
        try:
            import_module('%s.%s' % (app, module_name))
        except:
            continue

def templates_autodiscover():
    for app in settings.INSTALLED_APPS:
        path = os.path.join(settings.APPS_ROOT, app, 'templates')
        if os.path.exists(path):
            settings.TEMPLATE_DIRS += (path,)

templates_autodiscover()
