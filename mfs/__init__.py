import os
from django.conf import settings
from .utils import *
# from .core  import *

FSDIR = None;
FSURL = None;

if not hasattr(settings, 'FSDIR'):
    FSDIR = os.path.join(settings.BASE_DIR, "fsdir");
else:
    FSDIR = settings.FSDIR;

if not os.path.isdir(FSDIR):
    os.mkdir(FSDIR);
    printsucc("{} is created.".format(FSDIR));


if not hasattr(settings, 'FSURL'):
    FSURL = "/file/";
else:
    FSURL = settings.FSURL;

