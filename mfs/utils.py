import socket


def get_hostname() -> str:
    """ Function that is used to retreive the host name.

    Returns:
        The host name.
    """
    try:
        return socket.gethostname()
    except:
        return 'localhost'


def handle_uploaded_file(f, absfilepath):
    """Function of handling the uploaded file.

    Function to copy data from an uploaded file in a file created 
    in binary read/write mode in the file system of the server.

    Args:
        f (:obj:`UploadedFile`): An instance of uploaded file.
        absfilepath (str): The absolute path to the destination file.

    Returns:
        bool: Returns False on error
            Returns True if successful.
    """
    try:
        # opening the file in binary read/write mode
        # with the features of a resource
        with open(absfilepath, "wb+") as filedest:
            for chunk in f.chunks():
                filedest.write(chunk)

            # By looping over UploadedFile.chunks() instead of 
            # calling read(), we can make sure that large files 
            # do not saturate the system memory.

        return True
    except Exception as e:
        # In case of error, we display the error and return False
        print("[ \033[91mERRO\033[0m ]"\
            + f"[e.__class__.__name__] message: {e}")
        return False


def get_random_name(prefix='', size=16, alpha='0123456789'):
    """Random string generation function.

    Args:
        prefix (str): The prefix of generated nonce.
        size (int): The size of the nonce. Default set to 16.
        alpha (str): The string of alphabet. Default set to '0123456789'.

    Returns:
        str: Returns the nonce generated.
    """
    alphalen = len(alpha)  # The length of the alphabet.
    sequence = []  # Randomly generated sequence.
    for i in range(size):
        randidx = random.randint(0, alphalen - 1)
        sequence.append(alpha[randidx])
    return prefix + (''.join(sequence))


def geturl(url, default_dir_name='', filepath=''):
    """Function to build a URL to this file.

    Args:
        url (str): The URL that contains host name.
        default_dir_name (str): The default dir name.
        filepath (str): The path of the file.

    Returns:
        str: Returns the access URL to this file.
    """
    filedir = default_dir_name
    fileurl = url[1:] if url.startswith('/') else url
    if filedir:
        fileurl = os.path.join(fileurl, filedir)

    fileurl = os.path.join(fileurl, filepath)
    return fileurl


