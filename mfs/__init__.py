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
        and 'BASE_DIR' not in settings.MIDNIGHT_FILE_SYSTEM:
    FSDIR = os.path.join(settings.BASE_DIR, "fsdir")
else:
    FSDIR = settings.MIDNIGHT_FILE_SYSTEM['BASE_DIR']

if not os.path.isdir(FSDIR):
    os.mkdir(FSDIR)
    print(SUCC + "{} is created.".format(FSDIR))

if not hasattr(settings, 'MIDNIGHT_FILE_SYSTEM')\
        and 'BASE_URL' not in settings.MIDNIGHT_FILE_SYSTEM:
    FSURL = "/file/"
else:
    FSURL = settings.MIDNIGHT_FILE_SYSTEM['BASE_URL']

