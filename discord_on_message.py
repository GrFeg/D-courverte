import os
import json
from config_logger import logger
import discord
from boss import ajout_lien_au_df, traitement_message_log
import fonction
import affichage_info
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

"""
Fichier python qui gère l'evènement on_message de discord. Cet évènement detecte chaque envoit de message sur le serveur discord.

"""


chemin_fichier_config = '_donnee/config.json'

if os.path.isfile(chemin_fichier_config):
    #Récupération des configurations du bot
    with open(chemin_fichier_config) as config_file:
        config = json.load(config_file)

    ID_JOUEUR_PIZZABLEU = config['ID_JOUEUR_PIZZABLEU']
    ID_JOUEUR_CLOUD = config['ID_JOUEUR_CLOUD']
    ID_BOT = config['ID_BOT']
    ID_BOT_MIOUNE = config['ID_BOT_MIOUNE']
    ID_GUILD_SERVEUR_INAE = config['ID_GUILD_SERVEUR_INAE']

    CHANNEL_ID_LOGS = 892509041140588581 
    CHEMIN_HISTO_LOGS = 'csv/histo_logs.csv'
    CHEMIN_RACINE = script_dir = os.path.dirname(__file__)

else:
    logger.info("discord_on_message Fichier config.json introuvable ")



#Fonction pour changer le pseudo d'un utilisateur avec le message envoyé
async def changement_pseudo(message: discord.Message, id_utilisateur: int):
    message_contenu = message.content
    guild = message.guild
    member = guild.get_member( id_utilisateur )
    await member.edit(nick= message_contenu) 
    await message.delete() 
    
    logger.info(f"Pseudo de Mioune changé pour: {message_contenu}")

#Fonction qui traite le message, extrait les lien dps.report et les traite (ajout au df, affichage)
async def traitement_message_envoye_log(bot, message: discord.Message):
    
    #Récupère les liens dps.report
    liste_logs = traitement_message_log(message.content)
    
    #Si la liste n'est pas vide
    if len(liste_logs) > 0:
            
            #Pour chaque lien dans la liste
            for lien_log in liste_logs:
                logger.debug(f"Début du traitement de {lien_log}")
                #Ajoute le lien au df global du boss (traite etc ..)
                erreur = ajout_lien_au_df(lien_log)
                

                #Si tout c'est bien passé, le rajoute a histo_log
                date_du_jour = datetime.now()
                date_log = lien_log.split("-")[1]
                date_log_format = datetime.strptime(date_log, "%Y%m%d")
                
                if (date_du_jour - date_log_format).days > 7:
                    logger.info(f"Log trop ancien ({(date_du_jour - date_log_format).days} jours), boss hebdo non mis à jour")
                else:
                    if not erreur == -1:
                        df_histo_message = await fonction.recuperation_message(bot, CHANNEL_ID_LOGS, 15, True, CHEMIN_HISTO_LOGS)
                        await affichage_info.actualisation_embed(bot, df_histo_message)
    else:
        await message.delete()

#Affichage d'un graphique (tout est fait main dans la fonction, sert pour les log des boss précis)
async def affichage_graphique(message: discord.Message):
    xe = ['N°1','N°2','N°3']
    ye = [78,72,0]
    min = [33,5,0]
    plt.clf()
    sns.barplot(x= ye, y = xe, label = "Moyenne")
    sns.barplot(x= min, y = xe, label = "Min")

    plt.title('Evolution des trys Qadim CM')
    plt.ylabel('Numéro Tentative')
    plt.xlabel('Pourcentage de vie (%)')
    plt.grid(True, axis = 'x')
    plt.xlim(0, 100)

    
    plt.savefig('mon_graphique.png')

    embed = discord.Embed(
        color=discord.Color.blue()  # Vous pouvez choisir la couleur
    )

    # Attachez l'image locale en utilisant un File et ajoutez-la à l'embed
    file = discord.File("mon_graphique.png", filename="mon_graphique.png")
    embed.set_image(url="attachment://mon_graphique.png")
    
    # Envoyez l'embed et l'image dans le canal
    await message.channel.send(file=file, embed=embed)
    

#Detecte un message envoyé
async def message_discord(bot, message : discord.Message):

    #Définition des variables
    channel_nom = message.channel.name
    channel_id = message.channel.id
    joueur = message.author.name
    id_joueur = message.author.id
    message_contenu = message.content

    logger.debug(f"{message.guild.name} - Message de: {joueur}:  {message_contenu} dans: {channel_nom}")

    #Test si le chanel est le canal des logs
    if channel_id == CHANNEL_ID_LOGS:
        await traitement_message_envoye_log(bot, message)

    #Changer le pseudo de mioune
    if "Mioune"  in message_contenu:
        await changement_pseudo(message, ID_BOT_MIOUNE)

    #Nils !
    if message_contenu =="Ah bah c'est bien Nils!":
        await message.channel.send("Ah bah oui c'est super même !")

    #Cloud !
    if id_joueur == ID_JOUEUR_CLOUD and not channel_id == CHANNEL_ID_LOGS:
        await message.add_reaction('💩')

    if "graphq"  in message_contenu:
        await affichage_graphique(message)
