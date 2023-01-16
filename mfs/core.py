import os
import logging as log
import jwt
import datetime as dt
from django.contrib.auth.models import User
from django.conf import settings
from . import FSDIR
from . import ERRO, INFO, SUCC
import mfs.models as models
from .utils  import *


def hasperm(file: models.File, user):
    """ Function of checking the user permissions.
    
    Args:
        file (:obj:`File`): The file object.
        user (:obj:`django.contrib.auth.models.User`): The user object.
    
    Returns:
        bool: If the user has the permission to access to the file,
            then this function return True. Overrise, it returns False.
    """
    if file.visibility == models.File.PUBLIC:
        log.debug(INFO + "Public file recovering ...")
        return True
    elif file.visibility == models.File.PROTECTED:
        log.debug(INFO + "Protected file recovering ...")
        log.debug(INFO + f"User info {user}")
        return user.is_authenticated and user.has_perm('mfs.download', file)
    else:
        log.debug(INFO + "Private file recovering ...")
        return user.is_authenticated\
                and (user.is_staff or user.is_superuser)\
                and user.has_perm('mfs.download', file)


def get_client_ip(request):
    """ Retreiving of IP address.

    Function of retreiving of IP address of
    the client machine.
    
    Args:
        request (:obj:`HTTPRequest`): The HTTP request received
            via the view.

    Returns:
        str: Returns IP address.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def userinfo(user):
    """ Function that is used to get some user infos.

    Args:
        user (:obj:`django.contrib.auth.models.User`): The user.

    Returns:
        dict: The dictionary of user information.
    """
    return {
        "username": user.username,
        "first_name": user.first_name,
        "last_name":  user.last_name,
    } if user.is_authenticated\
        else "__anonymous__"


def get_access_url(request, file: models.File, duration=dt.timedelta(minutes=1)):
    """ Function to get URL file.

    Args:
        request (:obj:`HTTPRequest`): The HTTP request received
            via the view.
        file (:obj:`File`): The file object.
        duration (:obj:`timedelta`): The duration of the token.
            Default set to 1 min (dt.timedelta(minutes=1)).

    Returns:
        tuple: Returns the tuple of access URL and the string
            of the access token.
        bool: Returns False, if the access to this file is not
            allowed to this request.user.
    """
    user = request.user
    url = None
    tok = None
    if hasperm(file, user):
        ipc = get_client_ip(request)
        url = file.url(request.build_absolute_uri('/'))
        tok = jwt.encode({
                'user': userinfo(user),
                'ipc':  ipc,
                'exp':  dt.datetime.utcnow() + duration
        }, settings.SECRET_KEY, algorithm='HS256')
        return url, tok
    else:
        return False


def getfile(filename, fclass, dirname=FSDIR):
    """Function to retrieve a file from the server's file system.
    
    Args:
    
    Returns:
    
    """
    # if we check if the class indicated
    # to contain the information about the file
    # that we want to index is indeed a subclass
    # of the class mfs.models.File
    if issubclass(fclass, models.File):
        # we check if the path to the file is valid 
        # and that the file exists in the location 
        # indicated in this path
        abspath = os.path.join(dirname, filename)
        if os.path.exists(abspath):
            # we then instantiate a new object of type fclass
            # to contain the information about the latter
            instance = fclass()
            instance.path = filename
            instance.size = os.path.getsize(abspath)
            return instance


def find(filename, fclass, dirname=FSDIR):
    """
    Search function for a file in the server's file system.
    of the server.
    
    Args:
    
    
    Returns:
    
    """
    # if we check if the class indicated
    # to contain the information about the file
    # that we want to index is indeed a subclass
    # of the class mfs.models.File
    if issubclass(fclass, models.File):
        if filename:
            absfilename = os.path.join(dirname, filename)
            result = None

            # we list the folders and files contained
            # in the current folder (dirname)
            if os.path.exists(dirname):
                filenames = os.listdir(dirname)
                for f in filenames:
                    absf = os.path.join(dirname, f)

                    # for each file name found
                    # it is compared to the file searched
                    if str(absfilename) == str(absf):
                        # the file you are looking for is found, 
                        # then you create the instance 
                        # of the specified class
                        return getfile(f, fclass, dirname)
                    elif os.path.isfile(absf):
                        # if it is a file, then
                        # we continue the search.
                        continue
                    else:
                        # in this case, it is a folder
                        # so we call again the function
                        result = find(filename, fclass, absf)
                        if not result:
                            # if there are no results, then
                            # we continue the search
                            continue
                        else:
                            # if a result is found, then
                            # stop the search and return
                            # the result
                            return result


def get_file_uploaded(file_uploaded, file_model, filedir=''):
    """Function to retrieve an uploaded file.

    Args:
        file_uploaded (mixed): File uploaded info.
        file_model (:class:`mfs.models.File`): The subclass of a File.
        filedir
    """
    # info(request.FILES);
    if file_uploaded:
        instance = file_model(path=str(file_uploaded)).touch()
        moved = handle_uploaded_file(file_uploaded, instance.filepath)
        if moved:
            log.debug(INFO + "{}".format(file_uploaded))
            log.debug(INFO + "{}".format(file_uploaded.content_type))
            ctsplited = file_uploaded.content_type.split('/')
            if len(ctsplited) >= 2:
                instance.ext = ctsplited[1]
            return instance
        else:
            log.debug(ERRO + "Moving of file uploaded is failed.")
    return 0

