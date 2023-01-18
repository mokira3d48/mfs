from rest_framework import serializers
from . import ERRO
from .core import get_file_uploaded
from .models import File


class FileField(serializers.FileField):
    """Field class of MFS file serializer.

    """
    def __init__(self, **kwargs):
        if 'type' in kwargs:
            self._file_type = kwargs.pop('type')
        else:
            raise ValueError(ERRO + "Type of file missing.")

        if not issubclass(self._file_type, File):
            raise TypeError(ERRO\
                + "The type of the file must be a subclass"
                " of mfs.models.File."
                )

        super().__init__(**kwargs)

    def to_internal_value(self, data):
        """
        The return value of this method will be shown to 
        the API views which will be received by the client.
        """
        file_object = super().to_internal_value(data)
        file_t = self._file_type
        mfile = get_file_uploaded(file_object, file_t)
        # print(type(mfile))
        return mfile

