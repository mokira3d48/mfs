import logging as log
import mfs


class PathNotDefinedError(Exception):
    """Error class of path not defined

    This exception is used when the path of the 
    folder is not defined.
    """
    pass


class FolderConcatenationError(Exception):
    """Error of folder concatanation with / operator. """
    pass


class OperatingError(Exception):
    """Logical error of operation. """
    pass


def try_to_exec():
    """Try to execute.

    Function that is used to try to execute
    a decorated function.

    Returns:
        callable: Returns a customised function with try..catch
            close.
    """
    def inner(f):
        def wrapper(*args, **kwargs):
            """ The wrapping function.

            Args:
                *args: Variable length arguments list.
                **kwargs: Additional keyword arguments.

            Returns:
                mixed: We return the function return.
            """
            try:
                return f(*args, **kwargs)
            except (PathNotDefinedError,
                    OperatingError,
                    FolderConcatenationError) as e:
                raise e
            except Exception as e:
                log.debug(mfs.ERRO + "Error type [{}]: {}".\
                    format(e.__class__.__name__, str(e)))

        return wrapper
    return inner
