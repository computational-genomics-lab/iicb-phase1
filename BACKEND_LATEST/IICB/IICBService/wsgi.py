"""
WSGI config for IICBService project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os,sys

from django.core.wsgi import get_wsgi_application

path='/home/azure/PycharmProjects/IICB_DJango'


if path not in sys.path:
    sys.path.insert(0, path)


os.environ['DJANGO_SETTINGS_MODULE'] = 'IICBService.settings'

#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "IICBService.settings")




application = get_wsgi_application()
