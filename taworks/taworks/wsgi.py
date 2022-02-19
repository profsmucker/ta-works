"""
WSGI config for taworks project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

import sys 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Calculate the path based on the location of the WSGI script.
apache_configuration= os.path.dirname(__file__)
project = os.path.dirname(apache_configuration)
workspace = os.path.dirname(project)
sys.path.append(workspace)
sys.path.append(project)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taworks.settings")

application = get_wsgi_application()
