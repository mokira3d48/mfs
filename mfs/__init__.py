import os
from django.conf import settings
from .utils import *
# from .core  import *


# constantes d'etat
ERRO = '[ \033[91mERRO\033[0m ]  '
WARN = '[ \033[93mWARN\033[0m ]  '
INFO = '[ \033[94mINFO\033[0m ]  '
SUCC = '[ \033[32mSUCC\033[0m ]  '

FSDIR = None
FSURL = None

if not hasattr(settings, 'FSDIR'):
    FSDIR = os.path.join(settings.BASE_DIR, "fsdir")
else:
    FSDIR = settings.FSDIR

if not os.path.isdir(FSDIR):
    os.mkdir(FSDIR)
    printsucc("{} is created.".format(FSDIR))

if not hasattr(settings, 'FSURL'):
    FSURL = "/file/"
else:
    FSURL = settings.FSURL

