import logging as log
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from . import ERRO, INFO, SUCC, WARN
from . import DOWNLOAD_PERMISSION, UPLOAD_PERMISSION


def create_initial_permissions():
    """ Function of module initialization. """
    log.debug(INFO + "MFS System init ...")
    log.debug(INFO + "Creating initial permissions ...")

    # Permission creation
    try:
        ct = None
        p1 = None
        p2 = None

        if not ContentType.objects.filter(app_label="mfs").exists():
            log.debug(INFO + "Content type creation ...")
            ct = ContentType()
            ct.app_label = "mfs"
            ct.model = "File"
            ct.save()
            log.debug(SUCC \
                      + "Content type of the following permissions is created."
                      )
        else:
            ct = ContentType.objects.get(app_label="mfs")
            log.debug(INFO + "`mfs` Content type found.")

        if not Permission.objects.filter(codename=DOWNLOAD_PERMISSION).exists():
            log.debug(INFO + "Permission creation ...")
            p1 = Permission()
            p1.content_type = ct
            p1.codename = "download"
            p1.name = "Can download"
            p1.save()
            log.debug(SUCC \
                      + "Downloading permission is created for files.")
        else:
            log.debug(WARN + "Downloading permission is exists.")

        if not Permission.objects.filter(codename=UPLOAD_PERMISSION).exists():
            p2 = Permission()
            p2.content_type = ct
            p2.codename = "upload"
            p2.name = "Can upload"
            p2.save()
            log.debug(SUCC \
                      + "Uploading permission is created for files.")
        else:
            log.debug(WARN + "Uploading permission is exists.")

    except Exception as e:
        log.debug(ERRO + f"This following error is detected : {e}")

