import enum
import os
from django.db       import models
from . import FSDIR
from . import FSURL
from .utils import utils


class File(models.Model):
    DEFAULT_DIR_NAME = None;
    DEFAULT_FILE_EXT = None;
    PROTECTED = 0x01;
    PRIVATE   = 0x02;
    PUBLIC    = 0x00;
    VISIBILITIES = [
        (PUBLIC, 'Public'),
        (PROTECTED, 'Protected'),
        (PRIVATE, 'Private')
    ];
    created_at = models.DateTimeField(auto_now_add=True, editable=False);
    updated_at = models.DateTimeField(auto_now=True);
    visibility = models.PositiveIntegerField(choices=VISIBILITIES, default=PUBLIC);
    filedir    = models.CharField(max_length=255, null=True, blank=True);
    name = models.CharField(max_length=255);
    size = models.PositiveBigIntegerField(default=0);
    ext  = models.CharField(max_length=255, null=True, blank=True);

    class Meta:
        unique_together = ('filedir', 'name', 'ext');
        abstract = True;
        ordering = ['name'];

    @property
    def dirpath(self):
        if self.filedir or self.DEFAULT_DIR_NAME:
            if not self.filedir: self.filedir = self.DEFAULT_DIR_NAME;
            return os.path.join(FSDIR, self.filedir);
        else:
            return FSDIR;

    @property
    def filepath(self):
        if self.ext or self.DEFAULT_FILE_EXT:
            if not self.ext: self.ext = self.DEFAULT_FILE_EXT;
            return os.path.join(self.dirpath, "{}.{}".format(self.name, self.ext));
        else:
            return os.path.join(self.dirpath, self.name);

    def url(self, host='/'):
        filedir = self.filedir or self.DEFAULT_DIR_NAME;
        fileext = self.ext     or self.DEFAULT_FILE_EXT;
        fileurl = FSURL[1:];

        if filedir: fileurl += f"{filedir}/";
        fileurl += self.name;
        if fileext: fileurl += "." + fileext;
        return f"{host}{fileurl}";

    def __init__(self, *args, **kwargs):
        super(File, self).__init__(*args, **kwargs);
        self._instance = None;

    def mkdir(self):
        """ Function to create the fildir for this file """
        # we check if the uploading directory is exists
        if os.path.isdir(FSDIR):
            if not os.path.isdir(self.dirpath):
                os.makedirs(self.dirpath);
                utils.printsucc("Directory at -> {} is created.".format(self.dirpath));

            return True;

        utils.printerr("The fs directory -> {} is not exists.".format(FSDIR));
        return False;

    def touch(self):
        """ Function to create this file in the dirpath. """
        # create dir if not existe
        created = self.mkdir();
        if created:
            # if the dir is created, then we can create this file.
            if not os.path.isfile(self.filepath):
                f = open(self.filepath, 'x');
                f.close();
                utils.printsucc("File at -> {} is created.".format(self.filepath));

            return True;
        return False;

    def exists(self):
        """ Function to check if this file is exists. """
        return os.path.exists(self.filepath);

    def open(self,  mode='rt'):
        if type(self.path) is str:
            try:
                isfile = self.touch();
                if isfile:
                    self._instance = open(self.path, mode);
                    return self._instance;
            except Exception as e:
                utils.printerr("This error is detected: {}".format(e.args[0]));

        return False;

    def read(self, *args, **kwargs):
        if self._instance is not None:
            try:
                return self._instance.read(*args, **kwargs);
            except Exception as e:
                utils.printerr("This error is detected: {}".format(e.args[0]));
        else:
            utils.printerr(f"{self.name} is not open.");

        return False;

    def readline(self, *args, **kwargs):
        if self._instance is not None:
            try:
                return self._instance.readline(*args, **kwargs);
            except Exception as e:
                utils.printerr("This error is detected: {}".format(e.args[0]));
        else:
            utils.printerr(f"{self.name} is not open.");
            return False;

    def write(self, data):
        if self._instance is not None:
            try:
                self._instance.write(data);
                return data;
            except Exception as e:
                utils.printerr("This error is detected: {}".format(e.args[0]));
        else:
            utils.printerr(f"{self.name} is not open.");

        return False;

    def close(self):
        if self._instance is not None:
            try:
                self._instance.close();
                self._instance = None;
                return True;
            except Exception as e:
                utils.printerr("This error is detected: {}".format(e.args[0]));
        else:
            utils.printerr(f"{self.name} is not open.");

        return False;

    def save(self, *args, **kwargs):
        created = self.touch();
        if created:
            self.size = os.path.getsize(self.filepath);
            return super(File, self).save(*args, **kwargs);

        utils.printerr("Unable to save this file at -> {} !".format(self.filepath));
        return False;

    def delete(self):
        try:
            if self.exists():
                os.remove(self.filepath);
                utils.printsucc("File at -> {} is deleted.".format(self.filepath));
                return True;
        except:
            utils.printerr("Deleting error of {} file.".format(self.filepath));
        utils.printerr("File of {} is not exists.".format(self.filepath));

