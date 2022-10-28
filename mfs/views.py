import os
from django.shortcuts import render
from rest_framework  import response
from rest_framework  import generics
from rest_framework  import viewsets
from .serializers    import FileUploadedSerializer
from .utils import printinfo as info
from .utils import printerr  as erro
from .utils import handle_uploaded_file
from . import FSDIR
from .models import File


class FileUploadingAPI(viewsets.ViewSet):
    serializer_class = FileUploadedSerializer;
    filedir = '';

    def get_file_uploaded(self, request, FileModel):
        """
        Fonction de recuperation d'un fichier uploadee """
        # info(request.FILES);
        file_uploaded = request.FILES.get('file_uploaded');
        if file_uploaded:
            instance = FileModel(name=str(file_uploaded), filedir=self.filedir).touch();
            moved    = handle_uploaded_file(file_uploaded, instance.filepath);
            if moved:
                info(file_uploaded);
                info(file_uploaded.content_type);
                ctsplited = file_uploaded.content_type.split('/');
                if len(ctsplited) >= 2:
                    instance.ext = ctsplited[1];
                return instance;
            else:
                erro("Moving of file uploaded is failed.");
        else:
            return 0;

    def create(self, request):
        """
        Redefinition de la fonction de creation du 
        fichier uploadee.
        """
        self.filedir = 'Mes documents';
        self.get_file_uploaded(request);
        return response.Response("OK");


