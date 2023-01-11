"""Model definition module 

"""

import os
from django.utils.translation import gettext as _
from django.db import models
from . import FSDIR
from . import FSURL
from . import ERRO, SUCC, INFO
from .utils import *
from .exceptions import PathNotDefinedError


class Folder(models.Model):
    """Model DB abstract of a folder.

    Attributs:
        created_at (datetime): The datetime of file creation.
        updated_at (datetime): The datetime of file updating.
        visibility (int): The file visibility.
        path (str): The file path.
    """
    DEFAULT_DIR_NAME = ''
    PROTECTED = 0x01
    PRIVATE = 0x02
    PUBLIC = 0x00
    VISIBILITIES = [
        (PUBLIC, 'Public'),
        (PROTECTED, 'Protected'),
        (PRIVATE, 'Private')
    ]

    path = models.TextField(
        unique=True,
        verbose_name=_("Path file")
    )
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

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        """Constructor of the file model.

        Args:
            *args: Variable length arguments list.
            **kwargs: Additional keyword arguments.
        """
        super(Folder, self).__init__(*args, **kwargs)
        self._instance = None
        self._tmp = None

    @property
    def i_(self):
        """:obj:`IOBase`: Return instance of the python file. """
        return self._instance

    @property
    def dirpath(self):
        """str: Returns the full path to the parent folder of this file. """
        # if self.path.find(FSDIR) == -1:
        if not self._tmp:
            if not self.pk:
                if self.path:
                    dir_name = self.DEFAULT_DIR_NAME
                    if dir_name.startswith('/'):
                        self.DEFAULT_DIR_NAME = dir_name[1:]

                    if self.path.startswith('/'):
                        self.path = self.path[1:]

                    self.path = os.path.join(FSDIR, 
                                            self.DEFAULT_DIR_NAME,
                                            self.path)
                else:
                    raise PathNotDefinedError(
                        ERRO + "The path of this folder ({}) is not defined."\
                            .format(self.__class__.__name__)
                        )
            self._tmp = self.path
        return self._tmp

    def exists(self):
        """Function to check if this file is exists.

        This function is abstract. Must be reimplemented
        by the subclasses.

        Returns:
            bool: Returns True if this file is exists.
        """
        raise NotImplemented(
            INFO + "This function must be implemented in the subclasss"
            " and must return an boolean value."
            )

    def open(self,  **kwargs):
        """Function of folder openning.

        This function is abstract. Must be reimplemented
        by the subclasses.

        Args:
            **kwargs: Additional given arguments for opening file.

        Returns:
            :obj:`IOBase`: Must returns an instance of the python file.
        """
        raise NotImplemented(
            INFO + "This function must be implemented in the subclasss."
            )

    def delete(self):
        """Function of folder deletion.

        This function is abstract. Must be reimplemented
        by the subclasses.
        """
        raise NotImplemented(
            INFO + "This function must be implemented in the subclasss."
            )

    def __str__(self):
        """Function to represent a file as a of a string of characters.

        Returns:
            str: Returns the string of file instance.
        """
        return f"{self.path}"


class Dir(Folder):
    """Django model for managing directories.

    Attributs:
        parent_dir (:obj:`Dir`): The parent directory of this directory.
    """

    parent_dir = models.ForeignKey(
        'Dir',
        on_delete=models.CASCADE,
        related_name='subdirectories',
        verbose_name=_('Parent directory')
        )

    class Meta:
        verbose_name = _("Directory")
        verbose_name_plural = _("Directories")
        ordering = ['updated_at']

    def mkdir(self):
        """Function to create the fildir for this file.

        Returns:
            bool: Returns True if the directory specified to `self.dirpath`.
                Else, returns False.
        """
        if os.path.isdir(FSDIR):
            try:
                # We check if the uploading directory is exists.
                os.makedirs(self.dirpath)
                print(SUCC + "Directory at -> {} is created."\
                    .format(self.dirpath))
                return True
            except Exception as e:
                print(ERRO + "This error is detected: {}".format(e))

        print(ERRO + "The fs directory -> {} is not exists."\
            .format(FSDIR))
        return False

    def save(self, *args, **kwargs):
        """Function of directory model saving.

        Function to save information about a file
        in the database.

        Args:
            *args: Variable length arguments list.
            **kwargs: Additional keyword arguments.
        """
        created = self.mkdir()
        if created:
            return super(Dir, self).save(*args, **kwargs)

        print(ERRO + "Unable to save this directory at -> {} !"\
            .format(self.dirpath))

    def delete(self):
        """Function to delete a file.

        Returns:
            bool: Returns True if this file is removed.
                Else, returns False.
        """
        try:
            if self.exists():
                os.rmdir(self.dirpath)
                self.delete()
                print(SUCC + "Directory at -> {} is deleted."\
                    .format(self.dirpath))
                return True
        except Exception as e:
            print(ERRO + "Deleting error of {} directory."\
                .format(self.dirpath))
            print(ERRO + "Error type: [{}]: {}".format(e.__class__.__name__,
                                                       str(e)))

        print(ERRO + "Directory of {} is not exists.".format(self.dirpath))
        return False


class File(Folder):
    """Model DB abstract of a file.

    Attributs:
        parent_dir (:obj:`Dir`): The parent directory of this file.
        size (int): The file size.
    """
    parent_dir = models.ForeignKey(
        Dir,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name=_('Parent directory')
        )

    size = models.PositiveBigIntegerField(null=True,
                                          verbose_name=_("Size (byte)"))

    class Meta:
        abstract = True

    @property
    def filepath(self):
        """str: Returns the full path to this file. """
        self.path = self.path[1:] if self.path.startswith('/')\
            else self.path
        return os.path.join(self.dirpath, self.path)

    def mkdir(self):
        """Function to create the fildir for this file.

        Returns:
            bool: Returns True if the directory specified to `self.dirpath`.
                Else, returns False.
        """
        if os.path.isdir(FSDIR):
            try:
                # We check if the uploading directory is exists.
                os.makedirs(self.dirpath)
                print(SUCC + "Directory at -> {} is created."\
                    .format(self.dirpath))
            except Exception as e:
                print(ERRO + "This error is detected: {}".format(e))
                return False

            try:
                # Creating and saving the dir into database.
                parent_dir = Dir(path=self.dirpath)
                parent_dir.save()
            except Exception as e
                print(ERRO + "This error is detected: {}".format(e))
            return True
        else:
            print(ERRO + "The fs directory -> {} is not exists."\
                .format(FSDIR))
            return False

    def touch(self):
        """Function to create this file in the dirpath.

        Returns:
            File: Returns the instance of this file, if this
                file is created successfully.
            bool: Returns False, if creation of this file is failed.
        """
        # Create dir if not exists.
        created = self.mkdir()
        if created:
            # if the dir is created, then we can create this file.
            if not os.path.isfile(self.filepath):
                f = open(self.filepath, 'x')
                f.close()
                print(SUCC + "File at -> {} is created."\
                    .format(self.filepath))
                return self
        return False

    def exists(self):
        """Function to check if this file is exists.

        Returns:
            bool: Returns True if this file is exists.
        """
        return os.path.exists(self.path)

    def open(self,  mode='rt'):
        """Function to open a file.

        Args:
            mode (str): Openning mode.

        Returns:
            IOBase: Returns the instance of open file.
            bool: Returns False if the file openning is field.
        """
        if type(self.filepath) is str:
            try:
                isfile = self.touch()
                if isfile:
                    self._instance = open(self.filepath, mode)
                    return self._instance
            except Exception as e:
                print(ERRO + "This error is detected: {}".format(e))
        return False

    def save(self, *args, **kwargs):
        """Function of file model saving.

        Function to save information about a file
        in the database.

        Args:
            *args: Variable length arguments list.
            **kwargs: Additional keyword arguments.
        """
        created = self.touch()
        if created:
            # We calculate file size before to save its data
            # into database.
            self.size = os.path.getsize(self.filepath)
            return super(File, self).save(*args, **kwargs)

        print(ERRO + "Unable to save this file at -> {} !"\
            .format(self.filepath))

    def delete(self):
        """Function to delete a file.

        Returns:
            bool: Returns True if this file is removed.
                Else, returns False.
        """
        try:
            if self.exists():
                os.remove(self.filepath)
                self.delete()
                print(SUCC + "File at -> {} is deleted."\
                    .format(self.filepath))
                return True
        except Exception as e:
            print(ERRO + "Deleting error of {} file.".format(self.filepath))
            print(ERRO + "Error type: [{}]: {}".format(e.__class__.__name__,
                                                   str(e)))

        print(ERRO + "File of {} is not exists.".format(self.filepath))
        return False

