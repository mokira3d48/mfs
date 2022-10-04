import re
import jwt
from django.conf import settings
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from .utils import utils
from . import FSURL


class FileAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response;
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        # token = jwt.encode( {'user' : usr, 'exp' : dt.datetime.utcnow() + dt.timedelta( minutes=2 ) }, settings.SECRET_KEY, algorithm='HS256' );
        absuri  = request.build_absolute_uri();
        mfsuri  = request.build_absolute_uri(FSURL);
        is_furl = re.match(f"^{mfsuri}", absuri);

        if not is_furl:
            # utils.printinfo(absuri);
            # utils.printinfo(is_furl);
            return self.get_response(request);
        else:
            utils.printinfo(absuri);
            return self.__file_rec(request);

    def __file_rec(self, request):
        message = '';
        token   = '';
        code    = 200;

        # recovery the authentication token
        if 'fid' in request.GET:
            token = request.GET['fid'];
        elif 'F-Id' in request.headers:
            token = request.headers['F-Id'];
        else:
            message = "Oops !";
            code    = 401;

        try:
            if token:
                data = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256']);
                return self.get_response(request);
        except:
            message = "Access denied !";
            code    = 403;

        # Code to be executed for each request/response after
        # the view is called.

        resp = Response({"message": message}, status=code);
        resp.accepted_media_type = "application/json";
        resp.accepted_renderer   = JSONRenderer();
        resp.renderer_context    = {};
        resp.render();
        return resp;

