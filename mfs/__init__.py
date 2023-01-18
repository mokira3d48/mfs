import os
import logging
from django.conf import settings
from .utils import *
# from .core  import *


# LOGGER_FORMAT = "[%(asctime)s %(msecs)03dms] %(message)s"
# logging.basicConfig(format=LOGGER_FORMAT,
#                    level=logging.INFO,
#                    datefmt="%I:%M:%S")

# Status constants
ERRO = ' \033[91mERRO\033[0m ] '
WARN = ' \033[93mWARN\033[0m ] '
INFO = ' \033[94mINFO\033[0m ] '
SUCC = ' \033[32mSUCC\033[0m ] '

logging.basicConfig(format='%(asctime)s %(message)s',
                    level=logging.DEBUG,
                    datefmt='[ %y-%m-%d  %H:%M:%S')

FSDIR = None
FSURL = None

if not hasattr(settings, 'MIDNIGHT_FILE_SYSTEM')\
        or 'BASE_DIR' not in settings.MIDNIGHT_FILE_SYSTEM:
    FSDIR = os.path.join(settings.BASE_DIR, "fsdir")
else:
    FSDIR = settings.MIDNIGHT_FILE_SYSTEM['BASE_DIR']

if not os.path.isdir(FSDIR):
    os.mkdir(FSDIR)
    logging.debug(SUCC + "{} is created.".format(FSDIR))

if not hasattr(settings, 'MIDNIGHT_FILE_SYSTEM')\
        or 'BASE_URL' not in settings.MIDNIGHT_FILE_SYSTEM:
    FSURL = "/file/"
else:
    FSURL = settings.MIDNIGHT_FILE_SYSTEM['BASE_URL']


# Permission constants
UPLOAD_PERMISSION = "upload"
DOWNLOAD_PERMISSION = "download"


# Django Guardian module settings
# -------------------------------
#
# Setting application
if not hasattr(settings, 'INSTALLED_APPS'):
    settings.INSTALLED_APPS = []

if 'guardian' not in settings.INSTALLED_APPS:
    if type(settings.INSTALLED_APPS) is tuple:
        installed_apps = settings.INSTALLED_APPS
        settings.INSTALLED_APPS = [*installed_apps]

    settings.INSTALLED_APPS.append('guardian')

# AUTHENTICATION_BACKENDS setting
if not hasattr(settings, 'AUTHENTICATION_BACKENDS'):
    settings.AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',  # this is default
        'guardian.backends.ObjectPermissionBackend',
    )

