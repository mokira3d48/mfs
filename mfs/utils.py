import socket


class utils:

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


    @staticmethod
    def log(cl, type, message):
        """ Function to make log in terminal. """
        print("{col}{fgc} {type} {reset} \t{message}".format(col=cl, fgc=utils.color.FG.BLACK, type=type, reset=utils.color.RESET, message=message));


    @staticmethod
    def printinfo(message):
        """ Function that is used to print infos in terminal. """
        utils.log(utils.color.BG.LIGHTGREY, 'INFO', message);


    @staticmethod
    def printwarn(message):
        """ Function that is used to print warnings in terminal. """
        utils.log(utils.color.BG.ORANGE, 'WARN', message);


    @staticmethod
    def printerr(message):
        """ Function that is used to print errors in terminal. """
        utils.log(utils.color.BG.RED, 'ERRO', message);


    @staticmethod
    def printsucc(message):
        """ Function that is used to print success message in terminal. """
        utils.log(utils.color.BG.GREEN, 'SUCC', message);


    @staticmethod
    def get_hostname():
        try:
            return socket.gethostname();
        except:
            return 'localhost';

