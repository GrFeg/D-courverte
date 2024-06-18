import discord
from discord.ext import commands
import fonction
from fonction import log
import ast
import json
from pathlib import Path
import os
from datetime import datetime
import locale
import threading
import schedule # type: ignore
import time
import pandas as pd
import asyncio

"""
Fichier python qui gère la commande discord /inscription
Detecte l'ajout d'une réaction au embed inscription déjà crée (par le fichier commande) et met à jour l'embed en fonction.

Gère les evenements terminé et les supprime du canal. Récupère les réactgion lorsque le bot est hoprs ligne pour mettre à jour les inscriptions.
"""

#Fonction setup qui va définir quel type de bot.event sont utilisé dans ce fichier
async def setup(bot):

    #Detection de suppression d'une réaction sur un message
    async def reaction_remove(payload):
        await on_raw_reaction_remove(payload, bot)
    bot.add_listener(reaction_remove, 'on_raw_reaction_remove')

    #Detection d'ajout de réaction sur un message
    async def reaction_add(payload):
        await on_raw_reaction_add(payload, bot)
    bot.add_listener(reaction_add, 'on_raw_reaction_add')

#Initialisation des variables
if os.path.isfile( Path('config.json') ):
    #Récupération des configurations du bot
    with open('config.json') as config_file:
        config = json.load(config_file)

    ID_BOT = config['ID_BOT']
    ID_CHANNEL_EVENT = config['ID_CHANNEL_EVENT']
    CHEMIN_EVENEMENT = 'csv/varaible.csv'
    CHEMIN_RACINE = script_dir = os.path.dirname(__file__)
    HEURE_PURGE = "00:01"

    locale.setlocale(locale.LC_TIME, 'fr_FR')

    date_du_jour = datetime.now()
    nom_du_jour = date_du_jour.strftime("%A")
else:
    log("Fichier config.json introuvable", 3)

#Fonction pour trouver le jour dans une phrase
def trouver_jour(date: str):
    '''
    Fonction qui a pour but de trouver dans un string le jour de la semaine entrée par un utilisateur et en ressort le delta entre
    le jour entrée et le jour actuelle.

    return delta: int
    '''

    liste_jours = ['lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche']
    date = date.lower().split()

    if date[0] in liste_jours:

        if liste_jours.index(nom_du_jour) <= liste_jours.index(date[0]):
            delta = liste_jours.index(date[0]) - liste_jours.index(nom_du_jour)
            return delta
        else:
            print('Jour de la semaine choisit est déjà passé !')
            return -5
    
    else:
        print('Jour de la semaine non reconnu')
    
    return -1

#Fonction pour supprimer les evenement terminés
async def purge_event(bot):
    log('Fonction purge_event')
    #Récupère le fichier sous forme de df
    df_evenement = pd.read_csv(CHEMIN_RACINE + "/" + CHEMIN_EVENEMENT)

    #Pour chaque ligne du df
    for indexe, event in df_evenement.iterrows():

        #Si l'évenement est pas terminé
        if event['event_terminer'] == 0:

            #Test si le jour est passé ou non (renvoit -5 si terminé, -1 en cas de jour non trouvé)
            jour_restant = trouver_jour(event['date'])

            if jour_restant == -1:
                continue
            if jour_restant == -5:

                channel = bot.get_channel( ID_CHANNEL_EVENT )
                try:
                    #Supprime le message
                    message = await channel.fetch_message(event['id'])
                    await message.delete()
                except:
                    log('Evenement non trouvé dans le canal, suppression impossible', 2)
                #Met a 1 la ligne event_terminer
                df_evenement.at[indexe, "event_terminer"] = 1

    #Actualise le csv
    df_evenement.to_csv(CHEMIN_RACINE + "/" + CHEMIN_EVENEMENT, index= False)

    return True

#Fonction qui va être lancé dans le thread
def executer_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

#Fonction pour initalisé le thread schedule
async def init_schedule_thread(bot):
    #Définitions de schedule pour qu'il démarre a tel heure et execute tel fonction.
    schedule.every().day.at(HEURE_PURGE).do(lambda: asyncio.run(purge_event(bot)))
    #Création et lancement du thread pour ne pas bloquer le reste du programme.
    #Le code va s'éxécuter en """""""parallele""""""" du reste du code
    schedule_thread = threading.Thread(target=executer_schedule)
    schedule_thread.start()
    log(f"Thread mis en place pour la purge_event à {HEURE_PURGE}")

#Mettre à jour le csv varaible
def actu_csv_varaible(emoji, nom, id_message):
    print(f'Recherche pour: {emoji} mis par {nom}')

    df_event = pd.read_csv(CHEMIN_RACINE + "/" + CHEMIN_EVENEMENT)
    if not nom == "Régent":
        if emoji == "✅":
            print(f'{nom} recherché dans {df_event.loc[df_event['id'] == id_message, 'present'].iloc[0]}')

            #Recherche du nom dans 'present' de la ligne id_message
            if not df_event.loc[df_event['id'] == id_message, 'present'].str.contains(nom).any():

                present_liste   =   df_event.loc[df_event['id'] == id_message, 'present'].iloc[0]
                indexe          =   df_event.loc[df_event['id'] == id_message, 'present'].index[0]
                conver_en_liste =   ast.literal_eval(present_liste)
                conver_en_liste.append(nom)

                df_event.at[indexe, "present"] = conver_en_liste
                df_event.at[indexe, "nbr_present"] = df_event.loc[df_event['id'] == id_message, 'nbr_present'].iloc[0] + 1
                
                log(f'{nom} ajouté au df à la colonne présent')

                df_event.to_csv(CHEMIN_RACINE + "/" + CHEMIN_EVENEMENT, index= False)
            else:
                log(f'{nom} à déjà voté !', 0)

            #Recherche du nom dans 'absent' de la ligne id_message
            if df_event.loc[df_event['id'] == id_message, 'absent'].str.contains(nom).any():

                present_liste   =   df_event.loc[df_event['id'] == id_message, 'absent'].iloc[0]
                indexe          =   df_event.loc[df_event['id'] == id_message, 'absent'].index[0]
                conver_en_liste =   ast.literal_eval(present_liste)

                conver_en_liste.remove(nom)
                df_event.at[indexe, "absent"] = conver_en_liste
                df_event.at[indexe, "nbr_absent"] = df_event.loc[df_event['id'] == id_message, 'nbr_absent'].iloc[0] - 1
                
                log(f'{nom} enlevé au df à la colonne absent')

                df_event.to_csv(CHEMIN_RACINE + "/" + CHEMIN_EVENEMENT, index = False)

        if emoji == "❌":
            #Recherche du nom dans 'present' de la ligne id_message
            if not df_event.loc[df_event['id'] == id_message, 'absent'].str.contains(nom).any():

                present_liste   =   df_event.loc[df_event['id'] == id_message, 'absent'].iloc[0]
                indexe          =   df_event.loc[df_event['id'] == id_message, 'absent'].index[0]
                conver_en_liste =   ast.literal_eval(present_liste)
                conver_en_liste.append(nom)

                df_event.at[indexe, "absent"] = conver_en_liste
                df_event.at[indexe, "nbr_absent"] = df_event.loc[df_event['id'] == id_message, 'nbr_absent'].iloc[0] + 1
                
                log(f'{nom} ajouté au df à la colonne absent')

                df_event.to_csv(CHEMIN_RACINE + "/" + CHEMIN_EVENEMENT, index= False)
            else:
                log(f'{nom} à déjà voté !', 0)

            #Recherche du nom dans 'absent' de la ligne id_message
            if df_event.loc[df_event['id'] == id_message, 'present'].str.contains(nom).any():

                present_liste   =   df_event.loc[df_event['id'] == id_message, 'present'].iloc[0]
                indexe          =   df_event.loc[df_event['id'] == id_message, 'present'].index[0]
                conver_en_liste =   ast.literal_eval(present_liste)

                conver_en_liste.remove(nom)
                df_event.at[indexe, "present"]    =  conver_en_liste
                df_event.at[indexe, "nbr_present"] =  df_event.loc[df_event['id'] == id_message, 'nbr_present'].iloc[0] - 1
                
                log(f'{nom} enlevé au df à la colonne present')

                df_event.to_csv(CHEMIN_RACINE + "/" + CHEMIN_EVENEMENT, index = False)

    else:
        log(f'{nom} non pris en compte !')
        return False



    return True

#Fonction pour récupérer les réaction sur les embed lorsque le bot était éteind
async def recuperation_reaction_off(bot):
    #Recupère les id des messages présent dans le canal evenement
    df_message = await fonction.recuperation_id_message(bot, ID_CHANNEL_EVENT, 10)


    #Pour chaque message présent dans le canal evenement
    channel = bot.get_channel( ID_CHANNEL_EVENT )
    for _, ligne in df_message.iterrows():
        message = await channel.fetch_message( ligne['id_message'] )

        #Pour chaque reaction dans le message
        for reaction in message.reactions:

            async for user in reaction.users():
                if not user.id == ID_BOT:
                    print('')
                    print(f"Emoji: {reaction.emoji}, Réactions: {reaction.count} pour message {message.id}")

                    actu_csv_varaible(reaction.emoji, user.global_name, message.id)

                    df_message = pd.read_csv( CHEMIN_RACINE + '/' + CHEMIN_EVENEMENT)
                    ligne = df_message[df_message['id'] == message.id]
                    
                    await message.remove_reaction(reaction, user)      
                    await message.edit(embed=inscriptions(ligne['titre'].iloc[0],
                                                          ligne['description'].iloc[0],
                                                          ligne['date'].iloc[0],
                                                          ast.literal_eval(ligne['present'].iloc[0]),
                                                          ligne['nbr_present'].iloc[0],
                                                          ast.literal_eval(ligne['absent'].iloc[0])))



    return True

#Definir l'embed inscription
def inscriptions(type_de_sortie = 0, 
                 descriptions = 0, 
                 date = 0, 
                 liste_joueur = 0, 
                 nombre = 0, 
                 liste_joueur_absent = 0):
    
    '''
    Fonction qui créer un embed inscription en fonction des paramètres d'entrée.
    Si aucun paramètre n'est entrée crée un embed vide

    return l'embed
    '''

    log("Création de l'embed inscription.", 0)
    
    #Mise en forme de liste_joueur pour une version affichable dans un embed (saut de ligne, "", etc)
    format_liste_joueur = f""
    format_reserve =f""
    nombre_reserve = 0
    for i in range(len(liste_joueur)):
        if i <10:
            format_liste_joueur += "ㅤ- " + liste_joueur[i].strip("'") + '\n'
        if i >= 10: #Si plus de 10 joueurs, alors stock dans reserve
            format_reserve += "ㅤ- " + liste_joueur[i].strip("'") + '\n'
            nombre_reserve +=1

    #Mise en forme de format_liste_joueur_absent pour une version affichable dans un embed (saut de ligne, "", etc)
    format_liste_joueur_absent = f""
    for i in range(len(liste_joueur_absent)):
        format_liste_joueur_absent += "ㅤ- " + liste_joueur_absent[i].strip("'") + '\n'

            
    #Début de la création de l'embed
    embed_inscription = discord.Embed(title = f"**Inscription {type_de_sortie}:ㅤㅤㅤㅤ**", description ="", color=0x80ff80)
    embed_inscription.set_thumbnail(url="https://i.ibb.co/rHyn3Qs/sdfsdf.png")
    embed_inscription.add_field(name = "" , value = descriptions , inline = False)
    embed_inscription.add_field(name = "Date:" , value = date , inline = False)
    embed_inscription.add_field(name = "\u200b" , value = "" , inline = False)
    
    #Création de la ligne de carré en fonction du nombre d'inscris
    total = 0
    test = ""
    if 'fractale' in type_de_sortie.lower():
        total = 5
        if nombre == 0:
            test = "⬜ ⬜ ⬜ ⬜ ⬜"
    else:
        total = 10
        if nombre == 0:
            test = "⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜"

    for i in range(total):
        if i < int(nombre):
            test = test + " " + "🟦"
        else:
            test = test + " " + "⬜"

    if nombre_reserve != 0:
        test = test.replace("🟦",'🟩',nombre_reserve)


    if "fractale" in type_de_sortie.lower():
        embed_inscription.add_field(name = f"Personne inscrite: {nombre} / 5" , value = format_liste_joueur , inline = False)
        embed_inscription.add_field(name = "\u200b" , value = "" , inline = False)
        embed_inscription.add_field(name = "\u200b" , value = test , inline = False)

    else:
        embed_inscription.add_field(name = f"Personne inscrite: {nombre} / 10" , value = format_liste_joueur , inline = False)
        if int(nombre) > 10:
            embed_inscription.add_field(name = f"Réserve: {nombre_reserve}" , value = format_reserve , inline = False)
        if len(liste_joueur_absent) != 0:
            embed_inscription.add_field(name = "\u200b" , value = "" , inline = False)
            embed_inscription.add_field(name = "Non disponible:" , value = format_liste_joueur_absent , inline = False)
        embed_inscription.add_field(name = "\u200b" , value = "" , inline = False)
        embed_inscription.add_field(name = "\u200b" , value = test , inline = False)

    embed_inscription.add_field(name = "\u200b" , value = "" , inline = False)
    

    return embed_inscription

#Detecte l'ajout d'une réaction
async def on_raw_reaction_add(payload, bot):
    #Regarde si ce n'est pas le bot qui réagis (on l'exclus)
    if payload.user_id  != ID_BOT:

        #Récupère l'objet canal, message, emoji
        channel = await bot.fetch_channel(payload.channel_id)  
        message = await channel.fetch_message(payload.message_id)  
        emoji = payload.emoji
        guild = bot.get_guild(payload.guild_id)  # Récupère l'objet Guild grâce à l'ID de la guilde

        #Si il réussit à trouver la guild
        if guild:
            member = await guild.fetch_member(payload.user_id)

        #Check si l'emote est la coche ou la croix
        if emoji.name  == "✅" or emoji.name  == "❌":
            csv_embed = fonction.csv_recup('csv/varaible.csv')
            n_embed = fonction.recherche_embed(csv_embed, message.id)
        else:
            return

        #Regarde si la réaction est sur le bonne embed
        if int(csv_embed[n_embed][0]) == message.id and n_embed != -1:

            #Actualise le csv_varaible
            actu_csv_varaible(emoji.name, payload.member.global_name, message.id)

            #Récupère le csv pour l'embed inscriptions
            df_message = pd.read_csv( CHEMIN_RACINE + '/' + CHEMIN_EVENEMENT)
            ligne = df_message[df_message['id'] == message.id]
            
            #Supprime la réaction et met à jour l'embed
            await message.remove_reaction(emoji, member)     
            await message.edit(embed=inscriptions(ligne['titre'].iloc[0],
                                                  ligne['description'].iloc[0],
                                                  ligne['date'].iloc[0],
                                                  ast.literal_eval(ligne['present'].iloc[0]),
                                                  ligne['nbr_present'].iloc[0],
                                                  ast.literal_eval(ligne['absent'].iloc[0])))

            log(f"{payload.member.global_name} inscrit/désinscrit dans {csv_embed[n_embed][1]}", 0)

        print(f"Réaction: {emoji.name} ajouté sur un message par {payload.member.global_name}.")

#Detecte la suppression d'une réaction
async def on_raw_reaction_remove(payload, bot):
    1

