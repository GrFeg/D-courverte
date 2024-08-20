import discord
import os
import json
#import tombola
import statistiqueraid 
import inscription.inscription as inscription
import commande
from fonction import log
import fonction
from discord.ext import commands
from discord import app_commands
from pathlib import Path
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import affichage_info
import re
from boss import ajout_lien_au_df, traitement_message_log
from config_logger import logger



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
    logger.info("Fichier config.json introuvable")

messages_liste = []


#Definir la class MonBot
class MonBot(commands.Bot, discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):

        #Pour récuperer la commande dans le fichier "commande"
        try:
            await self.load_extension("commande")
        except:
            logger.critical('Fichier commande.py introuvable !',)
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

        df_histo_message = await fonction.recuperation_message(self, CHANNEL_ID_LOGS, 20, True, CHEMIN_HISTO_LOGS)

        await inscription.purge_event(self)
        await inscription.init_schedule_thread(self)
        await inscription.recuperation_reaction_off(self)

        logger.debug(f'Début récap raid')
        await affichage_info.actualisation_embed(self, df_histo_message)

bot = MonBot()


#Calcule le % entre deux nombres de votes
def calcul_pourcentage(votes: list[int]) -> tuple:
    """
    Fonction utilisé pour la gestion des votes de la commande /vote
    Récupère le nombre de vote pour chaque réponse et retourne le pourcentage de personnes ayant voté pour chaque réponse
    """
    total = sum(votes)
    if total == 0:
        return 0, 0
    return [round(vote / total * 100) for vote in votes]



#Définission de l'embed vote
def embed_vote(ligne_csv: list):

    #Calculer les % des votes
    pourcentage = [0,0]
    pourcentage = calcul_pourcentage(ligne_csv)
    espace = "ㅤㅤㅤㅤㅤ" #Ligne conserver pour avoir le caractère " " ^^
    field1 = f"({pourcentage[0]}%)"
    field2 = f"({pourcentage[1]}%)"

    #Faire la ligne de carré en fonction du %
    note = ""
    for i in range(10):
        if pourcentage[0] == 0 and pourcentage[1] == 0:
            note = "⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜"
            break
        if i >= pourcentage[0]/10:
            note = note + " " + "🟦"
        else:
            note = note + " " + "🟩"


    #Définition de l'embed
    embed_vote = discord.Embed(title="Vote:", description= "\u200b", color=discord.Color.blue())
    embed_vote.add_field(name = "Question :" , value = ligne_csv[1] , inline = False)
    embed_vote.add_field(name = "\u200b" , value = "" , inline = False)

    embed_vote.add_field(name = "Résultat :" , value = "" , inline = False)
    embed_vote.add_field(name = f"🟩 | {ligne_csv[2]} : " , value = f"ㅤ {ligne_csv[4]} votes. {field1}" , inline = False)
    embed_vote.add_field(name = "\u200b" , value = "" , inline = False)
    embed_vote.add_field(name = f"🟦 | {ligne_csv[3]} : " , value = f"ㅤ {ligne_csv[5]} votes. {field2}" , inline = False)
    embed_vote.add_field(name = "\u200b" , value = "" , inline = False)
    embed_vote.add_field(name = "------------------------------------" , value = "" , inline = False)
    embed_vote.add_field(name = "" , value = note , inline = False)
        
    return embed_vote

#Detecte lorsqu'une reaction est ajouté
@bot.event
async def on_raw_reaction_add(payload):

    channel = await bot.fetch_channel(payload.channel_id)  # Récupère l'objet Channel
    message = await channel.fetch_message(payload.message_id)  # Récupère l'objet Message
    emoji = payload.emoji
   
    if payload.user_id == ID_BOT:
        return
    if emoji.name  == "🟩" or emoji.name  == "🟦":
        csv_embed = fonction.csv_recup('csv/varaible.csv')
        n_embed = fonction.recherche_embed(csv_embed,message.id)
    else:
        return


#Commande vote, actualisation de l'embed à chaque réaction
    log('Réaction détecté, test si elle est sur un embed du bot . . .')

    if int(csv_embed[n_embed][0]) == message.id and (emoji.name  == "🟦" or emoji.name  == "🟩") and n_embed != -1:
        log("prout")
        if emoji.name == "🟩":
            csv_embed[n_embed][4] = 1 + int(csv_embed[n_embed][4])
            log(f"Embed: {csv_embed[n_embed][0]}, incrémentation de 1 sur vote n°2 ({csv_embed[n_embed][4]})")
        else:
            csv_embed[n_embed][5] = 1 + int(csv_embed[n_embed][5])
            log(f"Embed: {csv_embed[n_embed][0]}, incrémentation de 1 sur vote n°2 ({csv_embed[n_embed][5]})")

        embed = embed_vote(csv_embed[n_embed])

        await message.edit(embed=embed)

        fonction.csv_actu('csv/varaible.csv',csv_embed)
    

#Detecte lorsqu'une reaction est enlevé
@bot.event
async def on_raw_reaction_remove(payload):
    channel = await bot.fetch_channel(payload.channel_id)  # Récupère l'objet Channel
    message = await channel.fetch_message(payload.message_id)  # Récupère l'objet Message
    emoji = payload.emoji

#Vote avec les embed
    #Récupère le fichier csv et chercher si la réaction mise et sur un embed de vote.
    if emoji.name  == "🟦" or emoji.name  == "🟩":
        csv_embed = fonction.csv_recup('csv/varaible.csv')
        n_embed = fonction.recherche_embed(csv_embed,message.id)
    else:
        return

    #Test si la réaction est sur un embed de vote
    if int(csv_embed[n_embed][0]) == message.id and (emoji.name  == "🟦" or emoji.name  == "🟩") and n_embed != -1:
        #Mettre à jour les votes en fonction de la réaction mise
        if emoji.name == "🟩":
            csv_embed[n_embed][4] =  int(csv_embed[n_embed][4]) - 1
            log(f"Embed: {csv_embed[n_embed][0]}, incrémentation de -1 sur vote n°1 ({csv_embed[n_embed][4]})")
        else:
            csv_embed[n_embed][5] =  int(csv_embed[n_embed][5]) - 1
            log(f"Embed: {csv_embed[n_embed][0]}, incrémentation de -1 sur vote n°2 ({csv_embed[n_embed][5]})")
        
        embed = embed_vote(csv_embed[n_embed])
        await message.edit(embed=embed)

        #Actualiser le csv avec les nouveaux votes
        fonction.csv_actu('csv/varaible.csv',csv_embed)


bot.run(TOKEN)
