import os
from django.utils.translation import gettext_lazy as _
from django.db       import models
from . import FSDIR
from . import FSURL
from .utils import *


class File(models.Model):
    """
    Model DB abstraite d'un fichier
    """
    DEFAULT_DIR_NAME = None;
    DEFAULT_FILE_EXT = None;
    PROTECTED = 0x01;
    PRIVATE   = 0x02;
    PUBLIC    = 0x00;
    VISIBILITIES = [
        (PUBLIC,    'Public'),
        (PROTECTED, 'Protected'),
        (PRIVATE,   'Private')
    ];

    CREATED_AT_VBN      = _("Creation date");
    UPDATED_AT_VBN      = _("Updating date");
    VISIBILITY_VBN      = _("Visibility / Access level");
    FILEDIR_VBN         = _("Parent directory");
    NAME_VBN            = _("Name");
    SIZE_VBN            = _("Size (byte)");
    EXT_VBN             = _("Extension");

    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=CREATED_AT_VBN);
    updated_at = models.DateTimeField(auto_now=True, verbose_name=UPDATED_AT_VBN);
    visibility = models.PositiveIntegerField(choices=VISIBILITIES, default=PUBLIC, verbose_name=VISIBILITY_VBN);
    filedir    = models.CharField(max_length=255, null=True, blank=True, verbose_name=FILEDIR_VBN);
    name = models.CharField(max_length=255, verbose_name=NAME_VBN);
    size = models.PositiveBigIntegerField(default=0, verbose_name=SIZE_VBN);
    ext  = models.CharField(max_length=255, null=True, blank=True, verbose_name=EXT_VBN);

    class Meta:
        unique_together = ('filedir', 'name', 'ext');
        abstract = True;
        ordering = ['name'];

    @property
    def dirpath(self):
        """ 
        Retourne le chemin complet vers le dossier parent
        de ce fichier. 
        """
        if self.filedir or self.DEFAULT_DIR_NAME:
            if not self.filedir: self.filedir = self.DEFAULT_DIR_NAME;
            return os.path.join(FSDIR, self.filedir);
        else:
            return FSDIR;

    @property
    def filepath(self):
        """ Retourne le chemin complet vers ce fichier """
        self._fix_filename();
        return os.path.join(self.dirpath, self.name);

    def url(self, host='/'):
        """ Fonction de construction d'un URL vers ce fichier """
        filedir = self.filedir or self.DEFAULT_DIR_NAME;
        # fileext = self.ext     or self.DEFAULT_FILE_EXT;
        fileurl = FSURL[1:];

        if filedir: fileurl += f"{filedir}/";
        fileurl += self.name;
        # if fileext: fileurl += "." + fileext;
        return f"{host}{fileurl}";

    def __init__(self, *args, **kwargs):
        """ Constructeur du modele de fichier """
        super(File, self).__init__(*args, **kwargs);
        self._instance = None;

        # correction du nom de fichier passe en argument
        self._fix_filename();

    def _fix_filename(self):
        """ Fonction de correction du nom de fichier. """
        # si le nom du fichier contient une extension
        # alors on separe le nom de l'extenstion
        """
        filename     = self.name;
        name_splited = filename.split('.');
        if  len(name_splited) == 1 and name_splited[0]:
            self.name = name_splited[0];
        elif len(name_splited) == 2 and name_splited[1]:
            self.name = name_splited[1];

        if self.ext or self.DEFAULT_FILE_EXT:
            if not self.ext: self.ext = self.DEFAULT_FILE_EXT;
            self.name += '.{}'.format(self.ext);
        """
        ext  = self.DEFAULT_FILE_EXT.strip();
        name = self.name.strip();
        namesplit = name.split('.');
        if len(namesplit) == 1 or (len(namesplit) == 2 and not namesplit[0]):
            if ext:
                self.name = "{name}.{ext}".format(name=name, ext=ext);
                self.ext  = ext;

    def mkdir(self):
        """ Function to create the fildir for this file """
        # we check if the uploading directory is exists
        if os.path.isdir(FSDIR):
            if not os.path.isdir(self.dirpath):
                os.makedirs(self.dirpath);
                printsucc("Directory at -> {} is created.".format(self.dirpath));
            return True;

        printerr("The fs directory -> {} is not exists.".format(FSDIR));
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
                printsucc("File at -> {} is created.".format(self.filepath));

            return self;
        return False;

    def exists(self):
        """ Function to check if this file is exists. """
        return os.path.exists(self.filepath);

    def open(self,  mode='rt'):
        """ Fonction d'ouverture d'un fichier """
        if type(self.filepath) is str:
            try:
                isfile = self.touch();
                if isfile:
                    self._instance = open(self.filepath, mode);
                    return self._instance;
            except Exception as e:
                printerr("This error is detected: {}".format(e.args[0]));

        return False;

    def read(self, *args, **kwargs):
        """ Fonction de lecture entiere d'un fichier """
        if self._instance is not None:
            try:
                return self._instance.read(*args, **kwargs);
            except Exception as e:
                printerr("This error is detected: {}".format(e.args[0]));
        else:
            printerr(f"{self.name} is not open.");

        return False;

    def readline(self, *args, **kwargs):
        """ Fonction de lecture d'une ligne de donnees d'un fichier """
        if self._instance is not None:
            try:
                return self._instance.readline(*args, **kwargs);
            except Exception as e:
                printerr("This error is detected: {}".format(e.args[0]));
        else:
            printerr(f"{self.name} is not open.");
            return False;

    def write(self, data):
        """ Fonction d'ecriture de donnees dans un fichier """
        if self._instance is not None:
            try:
                self._instance.write(data);
                return data;
            except Exception as e:
                printerr("This error is detected: {}".format(e.args[0]));
        else:
            printerr(f"{self.name} is not open.");

        return False;

    def close(self):
        """ Fonction de fermetture d'un fichier. """
        if self._instance is not None:
            try:
                self._instance.close();
                self._instance = None;
                return True;
            except Exception as e:
                printerr("This error is detected: {}".format(e.args[0]));
        else:
            printerr(f"{self.name} is not open.");

        return False;

    def save(self, *args, **kwargs):
        """ 
        Fonction de sauvegarde des informations sur un fichier
        dans la base de donnees.
        """
        created = self.touch();
        if created:
            self.size = os.path.getsize(self.filepath);
            return super(File, self).save(*args, **kwargs);

        printerr("Unable to save this file at -> {} !".format(self.filepath));
        return False;

    def delete(self):
        """ Fonction de suppression d'un fichier. """
        try:
            if self.exists():
                os.remove(self.filepath);
                printsucc("File at -> {} is deleted.".format(self.filepath));
                return True;
        except:
            printerr("Deleting error of {} file.".format(self.filepath));
        printerr("File of {} is not exists.".format(self.filepath));

    def __str__(self):
        """
        Fonction de representation d'un fichier sous formme
        de chaine de caracteres.
        """
        return f"{self.filepath}";




