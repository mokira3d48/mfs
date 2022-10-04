from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models  import Permission
from mfs.utils import utils


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """ Function of module initialization. """
        utils.printinfo("MFS System init ...");

        # Permission creation
        try:
            ct = None;
            p1 = None;
            p2 = None;

            if not ContentType.objects.filter(app_label="mfs").exists():
                utils.printinfo("Content type creation ...");
                ct = ContentType();
                ct.app_label = "mfs";
                ct.model     = "File";
                ct.save();
                utils.printsucc("Content type of the following permissions is created.");
            
            if not Permission.objects.filter(codename="download").exists():
                utils.printinfo("Permission creation ...");
                p1 = Permission();
                p1.content_type = ct;
                p1.codename = "download";
                p1.name     = "Can download";
                p1.save();
                utils.printsucc("Downloading permission is created for files.");

            if not Permission.objects.filter(codename="upload").exists():
                p2 = Permission();
                p2.content_type = ct;
                p2.codename = "upload";
                p2.name     = "Can upload";
                p2.save();
                utils.printsucc("Uploading permission is created for files.");

        except Exception as e:
            utils.printerr(f"This following error is detected : {e.args[0]}");


