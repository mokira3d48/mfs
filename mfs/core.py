import os
import jwt
import datetime as dt
from django.contrib.auth.models import User
from django.conf import settings
from .       import FSDIR
from .models import File
from .utils  import utils


def hasperm(file: File, user):
    if file.visibility == File.PUBLIC:
        utils.printinfo("Public file recovering ...");
        return True;

    elif file.visibility == File.PROTECTED:
        utils.printinfo("Protected file recovering ...");
        utils.printinfo(f"User info {user}");
        return user.is_authenticated and user.has_perm('mfs.download', file);

    else:
        utils.printinfo("Private file recovering ...");
        return user.is_authenticated\
                and (user.is_staff or user.is_superuser)\
                and user.has_perm('mfs.download', file);


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR');
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0];
    else:
        ip = request.META.get('REMOTE_ADDR');
    return ip;


def userinfo(user):
    return {
        "username": user.username,
        "first_name": user.first_name,
        "last_name":  user.last_name,
    } if user.is_authenticated\
        else "__anonymous__";


def get_access_url(request, file: File, duration=dt.timedelta(minutes=1)):
    """ Function to get URL file
        ======================== """
    user = request.user;
    url  = None;
    tok  = None;

    if hasperm(file, user):
        ipc = get_client_ip(request);
        url = file.url(request.build_absolute_uri('/'));
        tok = jwt.encode({
                'user': userinfo(user),
                'ipc':  ipc,
                'exp':  dt.datetime.utcnow() + duration
        }, settings.SECRET_KEY, algorithm='HS256');
        return url, tok;
    else:
        return False;


def getfile(filename, fclass, dirname=FSDIR):
    """
    Fonction de récupération d'un fichier depuis le système de
    fichier du serveur.
    """
    # si on verifie si la classe indiqué comme classe
    # pour contenir les informations sur le fichier
    # qu'on veut indexer est belle et bien une sous classe
    # de la classe mfs.models.File
    if issubclass(fclass, File):
        # on verifie si le path vers le fichier est valide 
        # et que le fichier existe belle et bien à l'endroit 
        # indiqué dans cet path
        abspath = os.path.join(dirname, filename);
        if os.path.exists(abspath):
            # on instancie ensuite un nouvel objet de type fclass
            # pour contenir les informations sur ce dernier
            instance = fclass();
            dirn     = os.path.dirname(filename);
            instance.filedir = dirn if dirn else dirname;
            filenamext       = (os.path.basename(filename)).split('.');
            instance.name    = filenamext[0];
            instance.ext     = filenamext[1] if len(filenamext) > 1 else '';
            instance.size    = os.path.getsize(abspath);
            return instance;


def find(filename, fclass, dirname=FSDIR):
    """
    Fonction de recherche d'un fichier dans le système de fichier
    du serveur.
    """
    # si on verifie si la classe indiqué comme classe
    # pour contenir les informations sur le fichier
    # qu'on veut indexer est belle et bien une sous classe
    # de la classe mfs.models.File
    if issubclass(fclass, File):
        if filename:
            absfilename = os.path.join(dirname, filename);
            result      = None;

            # on énumère la liste des dossiers et fichiers contenus
            # dans le dossier courant (dirname)
            if os.path.exists(dirname):
                filenames = os.listdir(dirname);
                for f in filenames:
                    absf = os.path.join(dirname, f);

                    # pour chaque nom de fichier trouvé
                    # on le compare au fichier recherché
                    if str(absfilename) == str(absf):
                        # le fichier recherché est trouvé, alors on crée l'instance 
                        # de la classe spécifiée
                        return getfile(f, fclass, dirname);
                    elif os.path.isfile(absf):
                        # dans le cas où il s'agit d'un fichier, alors
                        # on continue la recherche.
                        continue;
                    else:
                        # dans ce cas, il s'agit d'un dossier
                        # donc on appel encore la fonction
                        result = find(filename, fclass, absf);
                        if not result:
                            # si il n'y a aucun résultat, alors
                            # on continue la recherche
                            continue;
                        else:
                            # s'il y a un résultat est trouvé, alors
                            # on arrête la recherche et on retourne
                            # le résultat
                            return result;


