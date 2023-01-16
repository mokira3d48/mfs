import logging as log
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from mfs import ERRO, INFO, SUCC


class Command(BaseCommand):
    """Command line of the database initialization. """

    def handle(self, *args, **kwargs):
        """ Function of module initialization. """
        log.debug(INFO + "MFS System init ...")

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
                log.debug(SUCC\
                    + "Content type of the following permissions is created."
                )
            
            if not Permission.objects.filter(codename="download").exists():
                log.debug(INFO + "Permission creation ...")
                p1 = Permission()
                p1.content_type = ct
                p1.codename = "download"
                p1.name = "Can download"
                p1.save()
                log.debug(SUCC\
                    + "Downloading permission is created for files.")

            if not Permission.objects.filter(codename="upload").exists():
                p2 = Permission()
                p2.content_type = ct
                p2.codename = "upload"
                p2.name = "Can upload"
                p2.save()
                log.debug(SUCC\
                    + "Uploading permission is created for files.")
        except Exception as e:
            log.debug(ERRO\
                + f"This following error is detected : {e.args[0]}")


