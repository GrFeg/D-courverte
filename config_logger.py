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

#Configuration du logger de mon code
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


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
