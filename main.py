import discord
import os
import json
import inscription.inscription as inscription
from discord.ext import commands
from affichage_info import actualisation_embed, init_semaine_df
from config_logger import logger
from discord_on_message import message_discord
from commande.vote import ajout_reaction, suppression_reaction
from fonction import recuperation_message
from boss import init_instances_boss
from joueur import init_instances_joueur


'''
Fichier où le Bot discord est initialisé

'''

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
    CHEMIN_RACINE = script_dir = os.path.dirname(__file__)

else:
    logger.info("Main ! Fichier config.json introuvable")

chemin_fichier_info = '_donnee/info.json'


if os.path.isfile(chemin_fichier_info):
    #Récupération des configurations du bot
    with open(chemin_fichier_info) as config_file:
        INFO_JOUEUR = json.load(config_file)['joueur']
else:
    logger.critical("Fichier info_raid.json introuvable")



def init():
    logger.debug("Démarrage Initialisation")

    init_semaine_df()
    logger.info("Affichage info Initialisé")

    logger.info("Boss() Initialisé")
    init_instances_boss()
    
    logger.info("Joueur() Initialisé")
    init_instances_joueur(INFO_JOUEUR)


init()

#Definir la class MonBot
class MonBot(commands.Bot, discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):

        #Pour récuperer la commande dans le fichier "commande"
        try:
            await self.load_extension("discord_commande")
        except:
            logger.critical('Fichier discord_commande.py introuvable !',)
        try:
            await self.load_extension("inscription.inscription")
        except:
            logger.critical('Fichier inscription.py introuvable !')

        #Synchronise les commandes avec touts les serveurs discord
        await self.tree.sync()
        #Synchronise les commandes avec le serveur INAE (plus rapide)
        await self.tree.sync(guild=discord.Object(id= ID_GUILD_SERVEUR_INAE))

    async def on_ready(self):
        logger.info(f'Le {self.user.name} est connecté')

        df_histo_message = await recuperation_message(self, CHANNEL_ID_LOGS, 20, True, CHEMIN_HISTO_LOGS)

        await inscription.purge_event(self)
        await inscription.init_schedule_thread(self)
        await inscription.recuperation_reaction_off(self)

        logger.debug(f'Début récap raid')
        await actualisation_embed(self, df_histo_message)
    
    #Detection de message
    async def on_message(self, message : discord.Message):
        await message_discord(self, message)
    
    async def on_raw_reaction_add(self, payload):
        await ajout_reaction(self, payload)
    
    async def on_raw_reaction_remove(self, payload):
        await suppression_reaction(self, payload)



bot = MonBot()

bot.run(TOKEN)
