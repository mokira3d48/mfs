from rest_framework import serializers
from .utils import printinfo as info


class FileUploadedSerializer(serializers.Serializer):
    """ 
    Serialiseur de fichier uploade.
    """
    file_uploaded = serializers.FileField();

    class Meta:
        fields = ['file_uploaded'];


