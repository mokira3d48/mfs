

class PathNotDefinedError(ValueError):
    """Error class of path not defined

    This exception is used when the path of the 
    folder is not defined.
    """
    pass


class FolderConcatenationError(ValueError):
    """Error of folder concatanation with / operator. """
    pass
