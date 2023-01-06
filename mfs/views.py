import os
from django.db import models
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import response
from rest_framework import views
from rest_framework import generics
from rest_framework import viewsets
from . import FSDIR
from . import FSURL
from .serializers import FileUploadedSerializer
from .utils import printinfo as info
from .utils import printerr as erro
from .utils import handle_uploaded_file
from .models import File


class FileUploadingAPI(viewsets.ViewSet):
    serializer_class = FileUploadedSerializer
    filedir = ''

    def get_file_uploaded(self, request, FileModel):
        """
        Fonction de recuperation d'un fichier uploadee """
        # info(request.FILES);
        file_uploaded = request.FILES.get('file_uploaded')
        if file_uploaded:
            instance = FileModel(name=str(file_uploaded),
                                 filedir=self.filedir).touch()
            moved = handle_uploaded_file(file_uploaded, instance.filepath)
            if moved:
                info(file_uploaded)
                info(file_uploaded.content_type)
                ctsplited = file_uploaded.content_type.split('/')
                if len(ctsplited) >= 2:
                    instance.ext = ctsplited[1]
                return instance
            else:
                erro("Moving of file uploaded is failed.")
        else:
            return 0

    def create(self, request):
        """
        Redefinition de la fonction de creation du 
        fichier uploadee.
        """
        self.filedir = 'Mes documents'
        self.get_file_uploaded(request)
        return response.Response("OK")


class Download(views.APIView):
    class Meta:
        model = None

    def get(self, request, id):
        message = ""
        code = 200
        assert isinstance(self.Meta.model, models.Model), (
            "The [Meta.model] value must be a django model."
        )
        fileinstance = get_object_or_404(self.Meta.model, pk=id)
        if fileinstance.visibility == File.PUBLIC:
            url = fileinstance.url
            return response.Response({"download": url}, status=code)

        message = "Access denied !"
        code = 403
        return response.Response({"message": message}, status=code)

