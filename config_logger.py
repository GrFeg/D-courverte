import logging
import colorlog


# Configuration du handler de couleur
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)-8s - %(funcName)-15s - %(reset)s%(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    },
    secondary_log_colors={
        'message': {
            'DEBUG': 'white',
            'INFO': 'white',
            'WARNING': 'white',
            'ERROR': 'white',
            'CRITICAL': 'white',
        }
    }
))

# Configuration du logger avec le handler coloré
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)