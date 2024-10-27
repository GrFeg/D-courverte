import discord
import os
import json
import threading
import inscription.inscription as inscription
from discord.ext import commands
from affichage_info import init_semaine_df
from config_logger import logger
from boss import init_instances_boss
from joueur import init_instances_joueur
from commande.recap_raid.init_log import init_log
from discord.ui import Button, View
import bot_instance
from api import run_api

espace = "ㅤㅤㅤㅤㅤ" #Ligne conserver pour avoir le caractère " " ^^


'''
Fichier où le Bot discord est initialisé ainsi que les fonctions init des différents bloc du bot

'''
print("")
os.chdir(os.path.dirname(__file__))

chemin_fichier_config = '_donnee/config.json'

if os.path.isfile(chemin_fichier_config):
    #Récupération des configurations du bot
    with open(chemin_fichier_config) as config_file:
        config = json.load(config_file)

    TOKEN = config['TOKEN']
    ID_JOUEUR_PIZZABLEU = config['ID_JOUEUR_PIZZABLEU']
    ID_JOUEUR_CLOUD = config['ID_JOUEUR_CLOUD']
    ID_BOT = config['ID_BOT']
    ID_BOT_MIOUNE = config['ID_BOT_MIOUNE']
    ID_GUILD_SERVEUR_INAE = config['ID_GUILD_SERVEUR_INAE']

    CHANNEL_ID_LOGS = 892509041140588581 
    CHEMIN_HISTO_LOGS = 'csv/histo_logs.csv'
    CHEMIN_RACINE = os.path.dirname(__file__)

else:
    logger.info("Main ! Fichier config.json introuvable")

chemin_fichier_info = '_donnee/info.json'


if os.path.isfile(chemin_fichier_info):
    #Récupération des configurations du bot
    with open(chemin_fichier_info) as config_file:
        INFO_JOUEUR = json.load(config_file)['joueur']
else:
    logger.critical("Fichier info_raid.json introuvable")


async def test(bot : bot_instance.MonBot, data, channel_id):
    channel = bot.get_channel(channel_id)
    await channel.send(data["Test"])
    
def testo(data, channel_id):
    test(bot, data, channel_id)

def init_api():
    flask_thread = threading.Thread(target=run_api)
    flask_thread.start()

#Initalisation des init() des différents fichiers python
def init(): 
    logger.debug("Démarrage Initialisation")

    result = init_semaine_df()
    if result:
        logger.info("Affichage info Initialisé")
    
    result = init_log()
    if result:
        logger.info("init log Initialisé")

    logger.info("Boss() Initialisé")
    init_instances_boss()
    
    logger.info("Joueur() Initialisé")
    init_instances_joueur(INFO_JOUEUR)
    
    
if __name__ == "__main__":

    init_api()
    init()

    bot = bot_instance.bot
    
    bot.run(TOKEN)
