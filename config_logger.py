import colorlog
import logging
import re

SUCCESS = 5
logging.addLevelName(SUCCESS, 'SUCCESS')

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

class CenteredLevelnameFormatter(colorlog.ColoredFormatter):
    def format(self, record):
        # Appliquer les couleurs sur le levelname, puis centrer
        # Super appelle le formatter parent, mais nous devons d'abord traiter les couleurs
        levelname_colored = super().format(record).split('|')[1].strip()
        
        # Supprimer les séquences ANSI pour obtenir la longueur réelle
        levelname_clean = ansi_escape.sub('', levelname_colored)
        
        # Centrer le texte sans les couleurs
        centered_levelname = levelname_clean.center(8)
        
        # Réappliquer les couleurs autour du texte centré
        # Ici, on garde les codes couleurs avant et après le texte
        centered_colored_levelname = levelname_colored.replace(levelname_clean, centered_levelname)
        
        # Recréer la chaîne formatée
        formatted_log = super().format(record)
        
        # Remplacer le niveau de log par la version centrée et colorée
        return formatted_log.replace(levelname_colored, centered_colored_levelname)

# Exemple de mise en place du handler
handler = colorlog.StreamHandler()

# Création d'un gestionnaire (handler) de flux pour les logs
handler = colorlog.StreamHandler()

# Application du formatteur avec couleurs et centrage du levelname
handler.setFormatter(CenteredLevelnameFormatter(
    "%(asctime_log_color)s%(asctime)s%(reset)s | %(log_color)s%(levelname)s%(reset)s | %(funcName)-15s | %(message_log_color)s%(message)s%(reset)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'SUCCESS':  'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    },
    secondary_log_colors={
        'asctime': {
            'DEBUG': 'black',
            'INFO': 'black',
            'SUCCESS':  'black',
            'WARNING': 'black',
            'ERROR': 'black',
            'CRITICAL': 'red',
        },
        'message': {
            'DEBUG': 'white',
            'INFO': 'white',
            'SUCCESS':  'white',
            'WARNING': 'white',
            'ERROR': 'white',
            'CRITICAL': 'bold_red',
        }
    }
))

# Création du logger et ajout du handler
logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel('SUCCESS')


requests_logger = logging.getLogger('requests')
requests_logger.setLevel(logging.WARNING)
requests_logger.addHandler(handler)

requests_logger = logging.getLogger('seaborn')
requests_logger.setLevel(logging.WARNING)
requests_logger.addHandler(handler)

requests_logger = logging.getLogger('matplotlib')
requests_logger.setLevel(logging.WARNING)
requests_logger.addHandler(handler)

requests_logger = logging.getLogger('discord')
requests_logger.setLevel(logging.WARNING)
requests_logger.addHandler(handler)

pillow_logger = logging.getLogger('PIL')
pillow_logger.setLevel(logging.WARNING) 
pillow_logger.addHandler(handler)

requests_logger = logging.getLogger('discord.client')
requests_logger.setLevel(logging.WARNING)
requests_logger.addHandler(handler)

pillow_logger = logging.getLogger('discord.gateway')
pillow_logger.setLevel(logging.WARNING) 
pillow_logger.addHandler(handler)

pillow_logger = logging.getLogger('discord.http')
pillow_logger.setLevel(logging.WARNING) 
pillow_logger.addHandler(handler)



def test_logger():
    print("")
    print("Test du Loger :")
    logger.info("Yo ")
    logger.log(5,"Yo ")
    logger.error("Yo ")
    logger.critical("Yo ")
    logger.debug('Yo')
    print("")


#test_logger()