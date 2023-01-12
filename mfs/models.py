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
    PROTECTED = 'O'
    PRIVATE = 'I'
    PUBLIC = 'B'
    VISIBILITIES = [
        (PUBLIC, _('Public')),
        (PROTECTED, _('Protected')),
        (PRIVATE, _('Private'))
    ]

    path = models.TextField(unique=True, verbose_name=_("Path file"))
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("Creation date")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updating date")
    )
    visibility = models.CharField(
        max_length=1,
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
    def abspath(self):
        """str: Returns the full path to the parent folder of this. """
        return os.path.join(FSDIR, self.path)
    
    @classmoethod
    def get_default_dir_name(cls):
        dir_name = self.DEFAULT_DIR_NAME
        if dir_name.startswith('/'):
            dir_name = dir_name[1:]
        return dir_name

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

    def exists(self):
        """Function allows to check if this directory is exists.

        Returns:
            bool: Returns True, if this directory is exists
                returns False, else.
        """
        return os.path.isdir(self.abspath)

    def mkdir(self):
        """Function to create the fildir for this file.

        Returns:
            bool: Returns True if the directory specified to
            `self.dirpath`. Else, returns False.
        """
        '''
        if os.path.isdir(FSDIR):
            try:
                if not self.exists():
                    os.makedirs(self.dirpath)
                    print(SUCC + "Directory at -> {} is created."\
                        .format(self.dirpath))
                return True
            except Exception as e:
                print(ERRO + "This error is detected: {}".format(e))
        else:
            print(ERRO + "The fs directory -> {} is not exists."\
                .format(FSDIR))
        return False
        '''
        if os.path.isdir(FSDIR):
            path = self.path
            if path.startswith('/'):
                path = path[1:]

            relpath = os.path.join(self.get_default_dir_name(), path)
            path = relpath
            try:
                if path.endswith('/'):
                    path = path[:-1]

                path_split = path.split('/')
                directory = None
                subdirectory = None
                rel_string_path = ''
                for dirname in path_split[:-1]:
                    rel_string_path += os.path.join(dirname, '')
                    abs_string_path = os.path.join(FSDIR, rel_string_path)
                    os.makedirs(abs_string_path)
                    subdirectory = Dir(path=rel_string_path)
                    subdirectory.save()
                    if directory:
                        directory.subdirectories.add(subdirectory)
                        directory.save()
                        directory = subdirectory
                
                abs_string_path = os.path.join(FSDIR, path)
                os.makedirs(abs_string_path)
                self.parent_dir = directory
                self.path = relpath
                return self
            except Exception as e:
                print(ERRO + "This error is detected: {}".format(e))

    def open(self, **kwargs):
        """Function that is used to open this directory.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            :obj:`list` of :obj:`str`: Returns the instance of open
                directory.
            bool: Returns False if the directory openning is field.
        """
        created = self.mkdir()
        if created:
            # If the dir is created, then we can open it.
            if os.path.isdir(self.dirpath):
                try:
                    self._instance = os.listdir(self.dirpath)
                    return self._instance
                except Exception as e:
                    print(ERRO + "{}: {}".format(e.__class__.__name__,
                                                 str(e)))
        return False

    def save(self, *args, **kwargs):
        """Function of directory model saving.

        Function to save information about a file
        in the database.

        Args:
            *args: Variable length arguments list.
            **kwargs: Additional keyword arguments.
        """
        is_exists = self.exists()
        if is_exists:
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
            print(ERRO + "Error type [{}]: {}".format(e.__class__.__name__,
                                                       str(e)))

        print(ERRO + "Directory of {} is not exists.".format(self.dirpath))
        return False
    
    def _add(self, x):
        """Function to add a folder into this directory.

        Args:
            x (:obj:`Folder`): The folder will be added into this
                directory.
        """
        if issubclass(x.__class__, Folder):
            if isinstance(x, Dir):
                self.subdirectories.add(x)
            elif isinstance(x, File):
                self.files.add(x)
    
    def __truediv__(self, f):
        """ Function of / operator.

        This function will be called when we make the following operation
        example: dir1 = dir1 / file1 or dir1 = dir1 / "my_folder_path"
        
        Args:
            f (mixed): Represent the folder path or folder instance.
        
        Returns:
            Dir: Returns this directory instance.
        """
        try:
            if type(f) is str:
                # if the specified folder is a string
                folder_path = f
                if f.find(FSDIR) == -1:
                    folder_path = os.path.join(FSDIR, f)

                if os.path.isdir(folder_path):
                    folder = Dir(path=folder_path)
                    folder.save()
                    self._add(folder)
                elif os.path.isfile(folder_path):
                    filei = File(path=folder_path)
                    filei.save()
                    self._add(filei)
            else:
                self._add(f)
        except Exception as error:
            print(ERRO + "Error type [{}]: {}".format(e.__class__.__name__,
                                                       str(e)))
        return self


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
        if not self._tmp:
            if self.path:
                if self.path.startswith('/'):
                    self.path = self.path[1:]
                self.path = os.path.join(self.dirpath, self.path)
            else:
                raise PathNotDefinedError(ERRO\
                    + "The path of this folder ({}) is not defined."\
                        .format(self.__class__.__name__)
                    )
            self._tmp = self.path
        return self._tmp

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
            except Exception as e:
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
        return os.path.exists(self.filepath)

    def open(self,  mode='rt'):
        """Function to open a file.

        Args:
            mode (str): Openning mode.

        Returns:
            IOBase: Returns the instance of open file.
            bool: Returns False if the file openning is field.
        """
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

