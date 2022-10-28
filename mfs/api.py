# from rest_framework import decorators
from django.db  import models
from django.shortcuts import get_object_or_404
from rest_framework import views
from rest_framework import response
from .models import File
from .utils  import *
from . import FSURL


class Download(views.APIView):
    class Meta:
        model = None;

    def get(self, request, id):
        message = "";
        code    = 200;
        assert isinstance(self.Meta.model, models.Model), (
            "The [Meta.model] value must be a django model."
        );
        fileinstance = get_object_or_404(self.Meta.model, pk=id);
        if fileinstance.visibility == File.PUBLIC:
            url = fileinstance.url;
            return response.Response({"download": url}, status=code);

        message = "Access denied !";
        code    = 403;
        return response.Response({"message": message}, status=code);

