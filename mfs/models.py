"""Model definition module

"""

import os
import logging as log
from django.utils.translation import gettext as _
from django.db import models
from . import FSDIR
from . import FSURL
from . import ERRO, SUCC, INFO
from .utils import try_to_exec
from .exceptions import PathNotDefinedError
from .exceptions import FolderConcatenationError


class Folder(models.Model):
    """Model DB abstract of a folder.

    Attributs:
        created_at (datetime): The datetime of file creation.
        updated_at (datetime): The datetime of file updating.
        visibility (int): The file visibility.
        relpath (str): The file relative path.
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

    relpath = models.TextField(unique=True, verbose_name=_("Path file"))
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("Creation date")
    )
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name=_("Updating date"))
    visibility = models.CharField(
        max_length=1,
        choices=VISIBILITIES,
        default=PUBLIC,
        verbose_name=_("Visibility/Access level")
    )

    class Meta:
        abstract = True

    def __init__(self, path: str = '', *args, **kwargs):
        """Constructor of the file model.

        Args:
            *args: Variable length arguments list.
            **kwargs: Additional keyword arguments.

        Raises:
            ValueError: The `path` string value is None.
        """
        super(Folder, self).__init__(*args, **kwargs)
        self._instance = None
        self._path = self.set_path(path)

    @property
    def i_(self):
        """:obj:`IOBase`: Returns instance of the python file. """
        return self._instance

    @property
    def path(self):
        """str: Returns the relative path. """
        if not self._path:
            dirname = self.get_default_dir_name()
            if dirname:
                if not dirname.endswith('/'):
                    dirname = '{}/'.format(dirname)

                rel_path_split = self.relpath.split(dirname)
                self._path = rel_path_split[1] if len(rel_path_split) > 1\
                    else rel_path_split[0]
        return self._path

    @path.setter
    def path(self, value: str):
        self._path = self.set_path(value)

    @property
    def abspath(self):
        """str: Returns the full path to the parent folder of this. """
        if not self.relpath:
            raise PathNotDefinedError(
                ERRO + "The path of this directory is not defined."
                " You can define it using set_path() function or"
                " my_dir.path = 'your_relative_path'."
                )
        return os.path.join(FSDIR, self.relpath[1:])

    def get_default_dir_name(self) -> str:
        """str: Returns the default directory name. """
        dirname = ''
        if self.DEFAULT_DIR_NAME is None:
            dirname = ''
        else:
            dirname = self.DEFAULT_DIR_NAME.strip()

        return dirname\
            if dirname.startedwith('/')\
                else "/{}".format(dirname)

    def set_path(self, value: str) -> str:
        """Function that is used to set path of this folder.

        Args:
            value: The path string value.

        Returns:
            The same value processed.

        Raises:
            PathNotDefinedError: The path string value is None.
        """
        if value is None:
            raise PathNotDefinedError(
                ERRO + "The path string value must not be None"
                )

        value = value.strip()
        if value != '':
            if value.startswith('/'):
                self.relpath = value
            else:
                self_ddn = self.get_default_dir_name()
                self.relpath = os.path.join(self_ddn, value)
            return value
        return None

    def exists(self):
        """Function to check if this file is exists.

        This function is abstract. Must be reimplemented
        by the subclasses.

        Returns:
            bool: Returns True if this file is exists.
        """
        # raise NotImplemented(
        #    INFO + "This function must be implemented in the subclasss"
        #    " and must return an boolean value."
        #    )
        return os.path.exists(self.abspath)

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
        return f"{self.relpath}"


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
    
    def set_path(self, value: str) -> str:
        """Function that is used to set path of this folder.

        Args:
            value: The path string value.

        Returns:
            The same value processed.

        Raises:
            PathNotDefinedError: The path string value is None.
        """
        path = self.set_path(value)
        if type(path) is str and not path.endswith('/'):
            path = "{}/".format(path)
            self.relpath = "{}/".format(self.relpath)
        return path

    def exists(self):
        """Function allows to check if this directory is exists.

        Returns:
            bool: Returns True, if this directory is exists,
                returns False, else.

        Raises:
            ValueError: The `path` string value is None.
        """
        return os.path.isdir(self.abspath)

    @try_to_exec()
    def mkdir(self):
        """Function to create the directory in server file system.

        Returns:
            bool: Returns True if the directory specified to 
            `self.dirpath`. Else, returns False.

        Raises:
            ValueError: The `path` string value is None.
        """
        if os.path.isdir(FSDIR):
            if not self.exists():
                # We check if the uploading directory is exists.
                os.makedirs(self.abspath)
                log.debug(SUCC + "Directory at -> {} is created."\
                    .format(self.relpath))

            log.debug(INFO + "Directory at -> {} is already exists."\
                    .format(self.relpath))
            return True
        else:
            log.debug(ERRO + "The fs directory -> {} is not exists."\
                .format(FSDIR))

        return False

    @try_to_exec()
    def open(self, **kwargs):
        """Function that is used to open this directory.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            :obj:`list` of :obj:`str`: Returns the instance of open
                directory.
            bool: Returns False if the directory openning is field.

        Raises:
            ValueError: The `path` string value is None.
        """
        if self.exists():
            self._instance = os.listdir(self.abspath)
            return self._instance
        return False

    @try_to_exec()
    def save(self, *args, **kwargs):
        """Function of directory model saving.

        Function to save information about a file
        in the database.

        Args:
            *args: Variable length arguments list.
            **kwargs: Additional keyword arguments.
        
        Raises:
            ValueError: The `path` string value is None.
        """
        created = self.mkdir()
        if created:
            return super(Dir, self).save(*args, **kwargs)

        log.debug(ERRO + "Unable to save this directory at -> {} !"\
            .format(self.relpath))

    @try_to_exec()
    def delete(self):
        """Function to delete a file.

        Returns:
            bool: Returns True if this file is removed.
                Else, returns False.

        Raises:
            ValueError: The `path` string value is None.
        """
        if self.exists():
            os.rmdir(self.abspath)
            self.delete()
            log.debug(SUCC + "Directory at -> {} is deleted."\
                .format(self.relpath))
            return True

        log.debug(ERRO + "Directory of {} is not exists.".\
            format(self.relpath))
        return False

    def __truediv__(self, f):
        """Function of / operator.

        This function will be called when we make the following operation
        example: dir1 = dir1 / file1 
            or dir1 = dir1 / "my_folder_path"

        Args:
            f (mixed): Represents the folder path or folder instance.

        Returns:
            Dir: Returns this directory instance.

        Raises:
            TypeError: If `f` type is not string type and directory type.
            FolderConcatenationError: If it is impossible to concatenate
                the two folders.
        """
        if type(f) is not str and not issubclass(f.__class__, Folder):
            raise TypeError(
                ERRO + "{} must be a string or a folder type.".format(str(f))
            )

        self_relpath = self.relpath
        if not self_relpath:
            raise PathNotDefinedError(
                ERRO + "The path of this directory is not defined."
                " You can define it using set_path() function or"
                " my_dir.path = 'your_relative_path'."
                )

        if isinstance(f, File):
            if not f.relpath:
                raise PathNotDefinedError(
                    ERRO + "The path of `f` file passed in argument"
                    " is not defined."
                    )
            f = f.relpath

        # If the argument is a string, then the following
        # string processing is done:
        if type(f) is str:
            if f != '':
                path = ''  # The variable will contains the final path.

                # If at the beginning of the string we have
                # the character '/' then we do a merge.
                # Otherwise, we do a concatenation.
                if f.startswith('/'):
                    startedwith = bool(f.startswith(self_relpath))
                    if not startedwith:
                        raise FolderConcatenationError(
                            ERRO + "Unable to concatenate the following"
                            " two paths: {} and {}".format(self_relpath, f)
                        )

                    path = f
                else:
                    path = os.path.join(self_relpath, f)

                # If f ends in '/' then it is a folder,
                # otherwise it is considered a file.
                folder = None
                if f.endswith('/'):
                    folder = Dir(path=f)
                else:
                    folder = File(path=f)
                return folder
            else:
                # If the string to concatenate is empty then a new folder 
                # with the path to that folder is returned.
                return Dir(path=self.path)
        elif isinstance(f, Dir):
            if not f.relpath:
                raise PathNotDefinedError(
                    ERRO + "The path of `f` directory passed in argument"
                    " is not defined."
                    )
            return os.path.join(self_relpath, f.relpath[1:])


    def __iadd__(self, f: Folder):
        """Implementation of += operator

        This function allows to add a file or directory 
        into this directory.

        Args:
            f (:obj:`Folder`): The folder will be added to this directory.

        Returns:
            Dir: Returns the instance of this directory.

        Raises:
            ValueError: The `path` string value is None.
        """
        if issubclass(x.__class__, Folder):
            if isinstance(x, Dir) and hasattr(self, 'subdirectories'):
                self.subdirectories.add(x)
            elif isinstance(x, File) and hasattr(self, 'files'):
                self.files.add(x)
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
    def parent_dir_path(self):
        """str: Returns the absolute path of the parent directory
            of this file. """
        return os.path.split(self.abspath)[0]

    @try_to_exec()
    def _mkdir(self):
        """Function to create the fildir for this file.

        Returns:
            bool: Returns True if the directory specified 
                to `self.dirpath`. Else, returns False.

        Raises:
            ValueError: The `path` string value is None.
        """
        if os.path.isdir(FSDIR):
            # We check if the parent directory is exists.
            # If it's not exists, then create it.
            if not os.path.exists(self.parent_dir_path):
                os.makedirs(self.parent_dir_path)
                log.debug(SUCC + "Directory at -> {} is created."\
                    .format(self.parent_dir_path))
            return True
        else:
            log.debug(INFO + "The fs directory -> {} is not exists."\
                .format(FSDIR))
            return False

    @try_to_exec()
    def touch(self):
        """Function to create this file in the dirpath.

        Returns:
            File: Returns the instance of this file, if this
                file is created successfully.
            bool: Returns False, if creation of this file is failed.

        Raises:
            ValueError: The `path` string value is None.
        """
        # Create dir if not exists.
        created = self._mkdir()
        if created:
            # If the dir is created, then we can create this file.
            if not os.path.isfile(self.abspath):
                f = open(self.abspath, 'x')
                f.close()
                log.info(SUCC + "File at -> {} is created."\
                    .format(self.abspath))
            return self
        return False

    def exists(self):
        """Function to check if this file is exists.

        Returns:
            bool: Returns True if this file is exists.

        Raises:
            ValueError: The `path` string value is None.
        """
        return os.path.isfile(self.abspath)

    @try_to_exec()
    def open(self,  mode='rt'):
        """Function to open a file.

        Args:
            mode (str): Openning mode.

        Returns:
            IOBase: Returns the instance of open file.
            bool: Returns False if the file openning is field.
        
        Raises:
            ValueError: The `path` string value is None.
        """
        isfile = self.touch()
        if isfile:
            self._instance = open(self.abspath, mode)
            return self._instance
        return False

    @try_to_exec()
    def save(self, *args, **kwargs):
        """Function of file model saving.

        Function to save information about a file
        in the database.

        Args:
            *args: Variable length arguments list.
            **kwargs: Additional keyword arguments.

        Raises:
            ValueError: The `path` string value is None.
        """
        created = self.touch()
        if created:
            # We calculate file size before to save its data
            # into database.
            self.size = os.path.getsize(self.abspath)
            return super(File, self).save(*args, **kwargs)

        log.info(ERRO + "Unable to save this file at -> {} !"\
            .format(self.relpath))

    @try_to_exec()
    def delete(self):
        """Function to delete a file.

        Returns:
            bool: Returns True if this file is removed.
                Else, returns False.

        Raises:
            ValueError: The `path` string value is None.
        """
        if self.exists():
            os.remove(self.abspath)
            self.delete()
            log.info(SUCC + "File at -> {} is deleted.".format(self.relpath))
            return True
        else:
            log.info(INFO + "File of {} is not exists.".format(self.relpath))
        return False

