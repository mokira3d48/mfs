import os
from django.utils.translation import gettext as _
from django.db import models
from . import FSDIR
from . import FSURL
from .utils import *


class File(models.Model):
    """
    Model DB abstract of a file
    """
    DEFAULT_DIR_NAME = None
    DEFAULT_FILE_EXT = None

    PROTECTED = 0x01
    PRIVATE = 0x02
    PUBLIC = 0x00

    VISIBILITIES = [
        (PUBLIC, 'Public'),
        (PROTECTED, 'Protected'),
        (PRIVATE, 'Private')
    ]

    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("Creation date")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updating date")
    )
    visibility = models.PositiveIntegerField(
        choices=VISIBILITIES,
        default=PUBLIC,
        verbose_name=_("Visibility / Access level")
    )
    filedir = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Parent directory")
    )
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    size = models.PositiveBigIntegerField(default=0,
                                          verbose_name=_("Size (byte)"))
    ext = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Extension")
    )

    class Meta:
        unique_together = ('filedir', 'name', 'ext')
        abstract = True
        ordering = ['name']

    @property
    def dirpath(self):
        """ 
        Returns the full path to the parent folder
        of this file.
        """
        if self.filedir or self.DEFAULT_DIR_NAME:
            if not self.filedir: self.filedir = self.DEFAULT_DIR_NAME
            return os.path.join(FSDIR, self.filedir)
        else:
            return FSDIR

    @property
    def filepath(self):
        """ Returns the full path to this file """
        self._fix_filename()
        return os.path.join(self.dirpath, self.name)

    def url(self, host='/'):
        """ Function to build a URL to this file """
        filedir = self.filedir or self.DEFAULT_DIR_NAME
        # fileext = self.ext     or self.DEFAULT_FILE_EXT;
        fileurl = FSURL[1:]
        if filedir:
            fileurl += f"{filedir}/"
        fileurl += self.name
        # if fileext: fileurl += "." + fileext;
        return f"{host}{fileurl}"

    def __init__(self, *args, **kwargs):
        """ Constructor of the file model """
        super(File, self).__init__(*args, **kwargs)
        self._instance = None

        # correction of the file name passed in argument
        self._fix_filename()

    def _fix_filename(self):
        """ File name correction function. """
        # if the file name contains an extension
        # then we separate the name from the extension
        """
        filename = self.name;
        name_splited = filename.split('.')
        if  len(name_splited) == 1 and name_splited[0]:
            self.name = name_splited[0]
        elif len(name_splited) == 2 and name_splited[1]:
            self.name = name_splited[1]

        if self.ext or self.DEFAULT_FILE_EXT:
            if not self.ext: self.ext = self.DEFAULT_FILE_EXT
            self.name += '.{}'.format(self.ext)
        """
        ext = self.DEFAULT_FILE_EXT.strip()
        name = self.name.strip()
        namesplit = name.split('.')
        if len(namesplit) == 1 or (len(namesplit) == 2 and not namesplit[0]):
            if ext:
                self.name = "{name}.{ext}".format(name=name, ext=ext)
                self.ext  = ext
                return self.name
        if (len(namesplit) == 2 and namesplit[1]):
            self.ext = namesplit[1]

    def mkdir(self):
        """ Function to create the fildir for this file """
        # we check if the uploading directory is exists
        if os.path.isdir(FSDIR):
            if not os.path.isdir(self.dirpath):
                os.makedirs(self.dirpath)
                printsucc("Directory at -> {} is created."\
                    .format(self.dirpath))
            return True
        printerr("The fs directory -> {} is not exists.".format(FSDIR))
        return False

    def touch(self):
        """ Function to create this file in the dirpath. """
        # create dir if not existe
        created = self.mkdir()
        if created:
            # if the dir is created, then we can create this file.
            if not os.path.isfile(self.filepath):
                f = open(self.filepath, 'x')
                f.close()
                printsucc("File at -> {} is created.".format(self.filepath))
            return self
        return False

    def exists(self):
        """ Function to check if this file is exists. """
        return os.path.exists(self.filepath)

    def open(self,  mode='rt'):
        """ Function to open a file """
        if type(self.filepath) is str:
            try:
                isfile = self.touch()
                if isfile:
                    self._instance = open(self.filepath, mode)
                    return self._instance
            except Exception as e:
                printerr("This error is detected: {}".format(e.args[0]))
        return False

    def read(self, *args, **kwargs):
        """ Function to read a whole file """
        if self._instance is not None:
            try:
                return self._instance.read(*args, **kwargs)
            except Exception as e:
                printerr("This error is detected: {}".format(e.args[0]))
        else:
            printerr(f"{self.name} is not open.")
        return False

    def readline(self, *args, **kwargs):
        """ Function to read a line of data from a file """
        if self._instance is not None:
            try:
                return self._instance.readline(*args, **kwargs)
            except Exception as e:
                printerr("This error is detected: {}".format(e.args[0]))
        else:
            printerr(f"{self.name} is not open.")
            return False

    def write(self, data):
        """ Function of writing data to a file """
        if self._instance is not None:
            try:
                self._instance.write(data)
                return data
            except Exception as e:
                printerr("This error is detected: {}".format(e.args[0]))
        else:
            printerr(f"{self.name} is not open.")
        return False

    def close(self):
        """ Function to close a file. """
        if self._instance is not None:
            try:
                self._instance.close()
                self._instance = None
                return True
            except Exception as e:
                printerr("This error is detected: {}".format(e.args[0]))
        else:
            printerr(f"{self.name} is not open.")
        return False

    def save(self, *args, **kwargs):
        """ 
        Function to save information about a file
        in the database.
        """
        created = self.touch()
        if created:
            self.size = os.path.getsize(self.filepath)
            return super(File, self).save(*args, **kwargs)

        printerr("Unable to save this file at -> {} !".format(self.filepath))
        return False

    def delete(self):
        """ Function to delete a file. """
        try:
            if self.exists():
                os.remove(self.filepath)
                printsucc("File at -> {} is deleted.".format(self.filepath))
                return True
        except:
            printerr("Deleting error of {} file.".format(self.filepath))
        printerr("File of {} is not exists.".format(self.filepath))

    def __str__(self):
        """
        Function to represent a file as a of a string of characters.
        """
        return f"{self.filepath}"

