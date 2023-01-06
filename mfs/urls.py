# from django.conf.urls.static import static
# from django.conf import settings
from django import urls
from rest_framework import routers
from . import views
from . import FSDIR
from . import FSURL
from .utils import *


router = routers.DefaultRouter()
router.register(r'fupload', views.FileUploadingAPI, basename="upload")


urlpatterns = [
    urls.path('api/', urls.include(router.urls), name="api"),
]

printinfo(f"FSDIR = {FSDIR}")
printinfo(f"FSURL = {FSURL}")

# define an URL for file directory.
# urlpatterns += static(FSURL, document_root=FSDIR);
