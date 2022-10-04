from django.conf.urls.static import static
# from django.conf import settings
from . import FSDIR
from . import FSURL
from .utils import utils


urlpatterns = [

];

utils.printinfo(f"FSDIR = {FSDIR}");
utils.printinfo(f"FSURL = {FSURL}");

# define an URL for file directory.
# urlpatterns += static(FSURL, document_root=FSDIR);
