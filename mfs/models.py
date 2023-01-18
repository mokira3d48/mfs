"""Model definition module

"""

import os
import logging as log
import shutil

from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.db import models
from guardian.shortcuts import assign_perm
from . import FSDIR
from . import ERRO, SUCC, INFO, WARN
from . import UPLOAD_PERMISSION, DOWNLOAD_PERMISSION
from .exceptions import try_to_exec
from .exceptions import PathNotDefinedError
from .exceptions import OperatingError


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

    def __init__(self, *args, **kwargs):
        """Constructor of the file model.

        Args:
            *args: Variable length arguments list.
            **kwargs: Additional keyword arguments.

        Raises:
            ValueError: The `path` string value is None.
        """
        path = ''
        if len(args) > 0 and type(args[0]) is str:
            path = args[0]
            args = [*args]
            del args[0]

        super(Folder, self).__init__(*args, **kwargs)
        self._path = self.set_path(path)
        self._instance = None

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

                self.path_defined()
                # Raises PathNotDefinedError if the path is not defined.

                rel_path_split = self.relpath.split(dirname)
                self._path = rel_path_split[1] if len(rel_path_split) > 1 \
                    else rel_path_split[0]
        return self._path

    @path.setter
    def path(self, value: str):
        self._path = self.set_path(value)

    @property
    def abspath(self):
        """str: Returns the full path to the parent folder of this. """
        self.path_defined()
        # Raises PathNotDefinedError if the path is not defined.

        return os.path.join(FSDIR, self.relpath[1:])

    def get_default_dir_name(self) -> str:
        """str: Returns the default directory name. """
        dirname = ''
        if self.DEFAULT_DIR_NAME is not None:
            dirname = self.DEFAULT_DIR_NAME.strip()

        return dirname \
            if dirname.startswith('/') \
            else "/{}".format(dirname)

    def get_parent_dir(self):
        """Get parent directory of this folder.

        Function that is used to retreive the parent directory
        of this folder.

        Returns:
            :obj:`Dir`: A Dir instance built from the parent
                directory.
        """
        if (isinstance(self, Dir) or isinstance(self, File)) \
                and self.path_defined():
            # As a precautionary measure, we verify self instance.
            self_relpath = self.relpath
            if self_relpath.endswith('/'):
                self_relpath = self_relpath[:-1]

            if self_relpath != '':
                parent_dir_path = (os.path.split(self_relpath))[0]
                return Dir(parent_dir_path)

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
                ERRO + "The path string value must not be None."
            )

        if type(value) is str:
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
        #    INFO + "This function must be implemented in the sub class"
        #    " and must return a boolean value."
        #    )
        return os.path.exists(self.abspath)

    def open(self, **kwargs):
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

    @try_to_exec()
    def rename(self, new_name: str):
        """Function that allows to rename this folder.

        Returns:
            Folder: Returns this instance after to rename it.

        Raises:
            ValueError: If `new_name` value is None.
        """
        if new_name is None:
            raise ValueError(
                ERRO + "The variable of `new_name` must not be None."
            )
        if new_name == '/':
            raise OperatingError(
                ERRO + "Impossible to rename this folder to '/'."
            )
        if self.relpath == '/':
            raise OperatingError(
                ERRO + "Impossible to rename the root server directory."
            )

        self.path_defined()
        # Raises PathNotDefinedError if the path is not defined.

        self_relpath = self.relpath
        if self_relpath.endswith('/'):
            self_relpath = self_relpath[:-1]

        if new_name.endswith('/'):
            new_name = new_name[:-1]

        parent_dir = os.path.split(self_relpath)[0]
        new_relpath = os.path.join(parent_dir, new_name)
        new_abspath = os.path.join(FSDIR, new_relpath[1:])

        # We test if the folder to rename is a file
        # and if another file does not already have the same name
        # if it is the case.
        is_file = isinstance(self, File)\
                  and not os.path.isfile(new_abspath)

        # We test if the folder to rename is a folder
        # and if another folder does not already have the same name
        # if it is the case.
        is_dir = isinstance(self, Dir)\
                 and not os.path.isdir(new_abspath)

        if is_file or is_dir:
            # If the old folder is exists in file system, then
            # we rename it in file system.
            folder_isexists = os.path.exists(self.abspath)
            if folder_isexists:
                os.rename(self.abspath, new_abspath)

            self.relpath = new_relpath
            if bool(self.pk):
                super(Folder, self).save()
            return self
        elif os.path.isfile(new_abspath):
            log.debug(WARN + "Another file has already named {}." \
                      .format(new_name))
        elif os.path.isdir(new_abspath):
            log.debug(WARN + "Another directory has already named {}." \
                      .format(new_name))

    @try_to_exec()
    def move_to(self, dest):
        """Function to move a folfer to `dest` path.

        Args:
            dest (:obj:`str|Dir`): The dest path or directory 
                where you want to move this folder.

        Returns:
            Folder: Returns this instance after to move it.

        Raises:
            ValueError: If `new_name` value is None.
        """
        if dest is None:
            raise ValueError(
                ERRO + "The destination path (dest) must not be None."
            )

        if type(dest) is not str and not isinstance(dest, Dir):
            raise TypeError(
                ERRO + "The destination path (dest) must be"
                       " a string or Dir type."
            )
        if self.relpath == '/':
            raise OperatingError(
                ERRO + "Impossible to move the root server directory"
                       " to any directory."
            )

        if dest == '':
            return False

        self.path_defined()
        # Raises PathNotDefinedError if the path is not defined.

        self_relpath = self.relpath
        is_done = False
        if self_relpath.endswith('/'):
            self_relpath = self_relpath[:-1]
        filename = (os.path.split(self_relpath))[1]

        dest_relpath = ''
        if isinstance(dest, Dir) and dest.path_defined():
            dest_relpath = dest.relpath
        elif type(dest) is str:
            dest_relpath = dest

        new_relpath = os.path.join(dest_relpath, filename)
        folder_isexists = os.path.exists(self.abspath)
        if folder_isexists:
            new_abspath = os.path.join(FSDIR, new_relpath[1:])
            if not os.path.exists(new_abspath):
                shutil.move(self.abspath, new_abspath)
                is_done = True
            else:
                log.debug(WARN + "The destination path '{}' is already exists." \
                          .format(dest))

        is_done = is_done or (not folder_isexists)
        if is_done:
            self.relpath = new_relpath
            if isinstance(self, Dir):
                self.relpath += '/'

            is_saved = bool(self.pk)
            if is_saved:
                self.__class__.save(self)
                is_done = is_done and True
            is_done = is_done or (not is_saved)

        return self if is_done else False

    def delete(self):
        """Function of folder deletion.

        This function is abstract. Must be reimplemented
        by the subclasses.
        """
        raise NotImplemented(
            INFO + "This function must be implemented in the subclasss."
        )

    def path_defined(self):
        """Function to check if the folder path is defined.

        Returns:
            bool: Return True, if the path of this folder is defined.

        Raises:
            PathNotDefinedError: If the path of this folder
                is not defined.
        """
        if not self.relpath:
            raise PathNotDefinedError(
                ERRO + "The path of this directory is not defined."
                       " You can define it using set_path() function or"
                       " my_dir.path = 'your_relative_path'."
            )
        return True

    def save(self, *args, **kwargs):
        self.path_defined()
        # Raises PathNotDefinedError if the path is not defined.

        is_saved = bool(self.pk)
        if not is_saved:
            model = self.__class__
            try:
                instance = model.objects.get(relpath=self.relpath)
                if instance:
                    # self = instance
                    self.__dict__ = instance.__dict__
            except:
                pass

        return super(Folder, self).save(*args, **kwargs)

    def allows(self, permission: int, /, to):
        """Function of permission admin.
        This function give a specific permission to an user on this folder.
        
        Args:
            permission (int): The permission value between the following
                constant: DOWNLOAD_PERMISSION, UPLOAD_PERMISSION.
            to (:obj:`django.contrib.auth.models.User`): The target user
                will receive the permission.

        Returns:
            Folder: Returns this folder instance.

        Raises:
            ValueError: If the value `permission` variable not in
                the following constante:
                    - DOWNLOAD_PERMISSION,
                    - UPLOAD_PERMISSION.
            TypeError: If the user instance is not a object of
                django.contrib.auth.models.User.
        """
        if permission not in (UPLOAD_PERMISSION,
                              DOWNLOAD_PERMISSION):
            raise ValueError(
                ERRO + "The value of the permission must be between:\n"
                "\t - UPLOAD_PERMISSION;\n"
                "\t - DOWNLOAD_PERMISSION."
            )
        if not isinstance(to, User):
            raise TypeError(
                ERRO + "The content of `to` must be an instance of"
                " django.contrib.auth.models.User."
            )

        try:
            # perm = Permission.objects.get(codename=permission)
            # assign_perm(f'mfs.{perm.codename}', to, self)
            assign_perm(f'mfs.{permission}', to, self)
            return self
        except Permission.DoesNotExist:
            raise OperatingError(
                ERRO + "You forgot to execute the following command line to"
                " create the basic initial permissions for file management:\n",
                " ~$ python manage.py mfsinit"
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
        null=True,
        related_name='subdirectories',
        verbose_name=_('Parent directory')
    )

    class Meta:
        verbose_name = _("directory")
        verbose_name_plural = _("directories")
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
        path = super(Dir, self).set_path(value)
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
                log.debug(SUCC + "Directory at -> {} is created." \
                          .format(self.relpath))
            else:
                log.debug(WARN + "Directory at -> {} is already exists." \
                          .format(self.relpath))
            return True
        else:
            log.debug(ERRO + "The fs directory -> {} is not exists." \
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

        log.debug(ERRO + "Unable to save this directory at -> {} !" \
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
            log.debug(SUCC + "Directory at -> {} is deleted." \
                      .format(self.relpath))
            return True

        log.debug(ERRO + "Directory of {} is not exists." \
                  .format(self.relpath))
        return False

    def subfolders(self):
        """Generator of the sub-folders contained in this directory.
        
        Yield:
            Folder: The next folder.
        """
        for directory in self.subdirectories:
            yield directory

        for f in self.files:
            yield f

        raise StopIteration(INFO + "End of directory!")

    def __truediv__(self, f):
        """Function of / operator.

        This function will be called when we make the following operation
        example: new_file_instance = dir1 / file_instance 
            or dir1 = dir1 / "my_directory_path"

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

        self.path_defined()
        # Raises PathNotDefinedError if the path is not defined.

        self_relpath = self.relpath

        # If the argument is a string, then the following
        # string processing is done:
        if type(f) is str:
            if f != '':
                path = ''  # The variable will contains the final path.
                if f.startswith('/'):
                    f = f[1:]

                path = os.path.join(self_relpath, f)
                if not path.endswith('/'):
                    path = "{}/".format(path)

                return Dir(path)
            else:
                # If the string to concatenate is empty then a new folder 
                # with the path to that folder is returned.
                return Dir(self_relpath)
        elif isinstance(f, Dir):
            if not f.relpath:
                raise PathNotDefinedError(
                    ERRO + "The path of `f` directory passed in argument"
                           " is not defined."
                )
            path = os.path.join(self_relpath, f.relpath[1:])
            return Dir(path)
        elif isinstance(f, File):
            if not f.relpath:
                raise PathNotDefinedError(
                    ERRO + "The path of `f` file passed in argument"
                           " is not defined."
                )
            path = os.path.join(self_relpath, f.relpath[1:])
            return f.__class__(path)

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
        self.path_defined()
        # Raises PathNotDefinedError if the path is not defined.

        if issubclass(f.__class__, Folder):
            if hasattr(self, 'subdirectories') and hasattr(self, 'files'):
                f_moved = f.move_to(self)
                if f_moved:
                    if isinstance(f, Dir):
                        self.subdirectories.add(f_moved)
                    elif isinstance(f, File):
                        self.files.add(f_moved)
                else:
                    log.debug(ERRO + "Unable to move {} to {}" \
                              .format(f, self))
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
        null=True,
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
                log.debug(SUCC + "Directory at -> {} is created." \
                          .format(self.parent_dir_path))
            return True
        else:
            log.debug(INFO + "The fs directory -> {} is not exists." \
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
                log.info(SUCC + "File at -> {} is created." \
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
    def open(self, mode='rt'):
        """Function to open a file.

        Args:
            mode (str): Openning mode.

        Returns:
            IOBase: Returns the instance of open file.
            bool: Returns False if the file openning is field.
        
        Raises:
            PathNotDefinedError: The `path` string value is None.
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
            PathNotDefinedError: The `path` string value is None.
        """
        created = self.touch()
        if created:
            # We calculate file size before to save its data
            # into database.
            self.size = os.path.getsize(self.abspath)
            return super(File, self).save(*args, **kwargs)

        log.info(ERRO + "Unable to save this file at -> {} !" \
                 .format(self.relpath))

    @try_to_exec()
    def delete(self):
        """Function to delete a file.

        Returns:
            bool: Returns True if this file is removed.
                Else, returns False.

        Raises:
            PathNotDefinedError: The `path` string value is None.
        """
        if self.exists():
            os.remove(self.abspath)
            self.delete()
            log.info(SUCC + "File at -> {} is deleted.".format(self.relpath))
            return True
        else:
            log.info(WARN + "File of {} is not exists.".format(self.relpath))
        return False
