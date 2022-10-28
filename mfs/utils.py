import socket


# Python program to print
# colored text and background
class color:
    """ Colors class:reset all colors with colors.reset; two
        sub classes fg for foreground
        and bg for background; use as colors.subclass.colorname.
        i.e. colors.fg.red or colors.bg.greenalso, the generic bold, disable,
        underline, reverse, strike through,
        and invisible work with the main class i.e. colors.bold """

    RESET           = '\033[0m';
    BOLD            = '\033[01m';
    DISABLE         = '\033[02m';
    UNDERLINE       = '\033[04m';
    REVERSE         = '\033[07m';
    STRIKETHROUGH   = '\033[09m';
    INVISIBLE       = '\033[08m';

    class FG:
        BLACK       = '\033[30m';
        RED         = '\033[31m';
        GREEN       = '\033[32m';
        ORANGE      = '\033[33m';
        BLUE        = '\033[34m';
        PURPLE      = '\033[35m';
        CYAN        = '\033[36m';
        LIGHTGREY   = '\033[37m';
        DARKGREY    = '\033[90m';
        LIGHTRED    = '\033[91m';
        LIGHTGREEN  = '\033[92m';
        YELLOW      = '\033[93m';
        LIGHTBLUE   = '\033[94m';
        PINK        = '\033[95m';
        LIGHTCYAN   = '\033[96m';

    class BG:
        BLACK       = '\033[40m';
        RED         = '\033[41m';
        GREEN       = '\033[42m';
        ORANGE      = '\033[43m';
        BLUE        = '\033[44m';
        PURPLE      = '\033[45m';
        CYAN        = '\033[46m';
        LIGHTGREY   = '\033[47m';


def log(cl, type, message):
    """ Function to make log in terminal. """
    print("{col}{fgc} {type} {reset} \t{message}".format(col=cl, fgc=color.FG.BLACK, type=type, reset=color.RESET, message=message));


def printinfo(message):
    """ Function that is used to print infos in terminal. """
    log(color.BG.LIGHTGREY, 'INFO', message);


def printwarn(message):
    """ Function that is used to print warnings in terminal. """
    log(color.BG.ORANGE, 'WARN', message);


def printerr(message):
    """ Function that is used to print errors in terminal. """
    log(color.BG.RED, 'ERRO', message);


def printsucc(message):
    """ Function that is used to print success message in terminal. """
    log(color.BG.GREEN, 'SUCC', message);


def get_hostname():
    try:
        return socket.gethostname();
    except:
        return 'localhost';


def handle_uploaded_file(f, absfilepath):
    """
    Fonction de copy des données d'un fichier uploadé
    dans un fichier créé en mode binaire lecture/ecriture
    dans le systeme de fichier du serveur.
    
    :args:
        + f             [UploadedFile]  Une instance du fichier uploadé.
        + absfilepath   [str]           Le chemin absolue vers le fichier de destination.
    :return:
        [bool]  Retourne False en cas d'erreur
                Retourne True en cas de succès
    """
    try:
        # ouverture du fichier en mode binaire lecture/ecriture
        # avec les fonctionnalites d'une resource
        with open(absfilepath, "wb+") as filedest:
            for chunk in f.chunks():
                filedest.write(chunk);

            """
            En bouclant sur UploadedFile.chunks() au lieu d’appeler read(),
            on peut s’assurer que les gros fichiers ne saturent 
            pas la mémoire du système.
            """
        return True;
    except Exception as e:
        # en cas d'erreur, on affichie l'erreur et on retourne
        # False
        print(f"[ERR]\t {e}");
        return False;


def get_random_name(prefix='', size=16, alpha='0123456789'):
    """
    Fonction de generation aleatoire de chaine de caracteres
    """
    alphalen = len(alpha);  # la  longeur de l'alphabet
    sequence = [];          # la sequence aleatoirement generee
    for i in range(size):
        randidx = random.randint(0, alphalen - 1);
        sequence.append(alpha[randidx]);
    return prefix + (''.join(sequence));



