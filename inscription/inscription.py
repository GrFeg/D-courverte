import fonction
from fonction import log, est_emoji_valide
import ast
import json
import os
from datetime import datetime
import locale
import threading
import schedule 
import time
import pandas as pd
import asyncio
from inscription.embed import embed_inscription_semaine, embed_inscriptions
from config_logger import logger

"""
Fichier python qui gère la commande discord /inscription
Detecte l'ajout d'une réaction au embed inscription déjà crée (par le fichier commande) et met à jour l'embed en fonction.

Gère les evenements terminés et les supprime du canal. Récupère les réactgions lorsque le bot est hors ligne pour mettre à jour les inscriptions.
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


chemin_fichier_config = '_donnee/config.json'

if os.path.isfile(chemin_fichier_config):
    #Récupération des configurations du bot
    with open(chemin_fichier_config) as config_file:
        config = json.load(config_file)

    ID_BOT = config['ID_BOT']
    ID_CHANNEL_EVENT = config['ID_CHANNEL_EVENT']
    CHEMIN_EVENEMENT = 'csv/varaible.csv'
    CHEMIN_RACINE = script_dir = os.path.dirname(__file__).rstrip(r'\\inscription')
    HEURE_PURGE = "00:01"

    locale.setlocale(locale.LC_TIME, 'fr_FR')

    date_du_jour = datetime.now()
    nom_du_jour = date_du_jour.strftime("%A")
else:
    log("Fichier config.json introuvable", 3)

#Fonction pour trouver le jour dans une chaine de caractère
def trouver_jour(date: str):
    '''
    Renvoit la différence entre le jour actuel et le jour de la semaine qui sera extrait de date

    ### Argument :
    - date (str) : Chaine de caractère contenant un jour de la semaine

    ### Renvoie:
    - delta (int) : La différence entre le jour en argument et le jour actuel.
    '''

    global nom_du_jour
    liste_jours = ['lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche']
    date = date.lower().strip() #Met le str en minuscule et retire les espaces inutiles

    #Test si la date contient un jour de la semaine
    liste_mots = date.split()
    jour_trouve = None
    for mot in liste_mots:
        if mot in liste_jours:
            jour_trouve = mot
            break

    #Si un jour de la semaine est trouvé
    if jour_trouve:
        #Recupère les numéros des jours de la semaine (lundi: 0 etc)
        num_jour_actuel = liste_jours.index(nom_du_jour)
        num_jour_trouve = liste_jours.index(jour_trouve)

        #Si le jour actuel est plus petit ou égale que le jour trouvé
        if num_jour_actuel <= num_jour_trouve:
            delta = num_jour_trouve - num_jour_actuel
            return delta
        else:
            log(f"| Fonction trouver_jour | Jour de la semaine déjà passé: {jour_trouve}")
            return -5
    
    else:
        log(f"| Fonction trouver_jour | Jour de la semaine non reconnu ({date})", 2)
    
    return "erreur"

#Fonction pour supprimer les evenement terminés
async def purge_event(bot):
    log('| Fonction purge_event | Démarrage . . . ', 0)

    #Récupère le fichier sous forme de df
    df_evenement = pd.read_csv(CHEMIN_RACINE + "/" + CHEMIN_EVENEMENT)
    print("Réussis :)")

    #Pour chaque ligne du df
    for indexe, event in df_evenement.iterrows():

        if not event['type'] == 0:
            break
        
        #Si l'évènement n'est pas terminé
        if event['event_terminer'] == 0:

            #Test si le jour est passé ou non (renvoit -5 si le jour est passé, "erreur" en cas de jour non trouvé)
            jour_restant = trouver_jour(event['date'])

            #Gestion des erreurs pour la fonciton trouver_jour
            if jour_restant == "erreur":
                log(f"| Fonction purge_event | Ligne {indexe} ingoré, format date non reconnu ({event['date']})")
                continue

            if jour_restant == -5:
                log(f"| Fonction purge_event | Event {indexe} terminé !", 0)
                channel = bot.get_channel( ID_CHANNEL_EVENT )
                try:
                    #Supprime le message
                    message = await channel.fetch_message(event['id'])
                    await message.delete()
                except:
                    log('Evenement non trouvé dans le canal, suppression impossible', 2)

                #Met à 1 la ligne event_terminer
                df_evenement.at[indexe, "event_terminer"] = 1

    #Actualise le csv
    df_evenement.to_csv(CHEMIN_RACINE + "/" + CHEMIN_EVENEMENT, index= False)

    return True

#Fonction qui va être lancé dans le thread
def executer_schedule():
    while True:
        schedule.run_pending()
        time.sleep(5)

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
def actu_csv_varaible(emoji: str, nom: str, id_message: int):
    """
    Actualise le csv varaible contenant tout les embed crée par inscription ou inscription_hebdo.

    ### Arguments:
    - emoji (str) : L'émoji que l'utilisateur a entré.
    - nom (str) : Pseudos de l'utilisateur.
    - id_message : ID de l'embed ou l'émoji a été mis.

    ### Renvoie:
    True / False si la fonction à reussis ou non a actualiser le csv.
    """

    #Test les arguments sont du bon type
    if not est_emoji_valide(emoji):
        log(f"| Fonction actu_csv_varaible | Emoji en argument non valide ({emoji})",2)
        return False
    if not type(nom) == str or not type(id_message) == int:
        log(f"| Fonction actu_csv_varaible | Format argument non valide ({nom}, {id_message})",2)
        return False
    
    if nom == "Régent": #A mettre dans une variable
        log(f"| Fonction actu_csv_varaible | Non repéré comme étant celui de bot ({nom})",2)
        return False
    
    log(f"| Fonction actu_csv_varaible | Recherche pour: {emoji} mis par {nom}", 0)

    emoji_semaine = ['🇱', '🇲', 'Ⓜ️','🇯', '🇻', '🇸', '🇩']

    df_event = pd.read_csv(CHEMIN_RACINE + "/" + CHEMIN_EVENEMENT)

    #Chercher si c'est une emote utilisé pour inscription_hebdo
    if emoji in emoji_semaine:
        #Recherche du nom dans 'present' de la ligne id_message

        #Rechercher quel emoji est utilisé dans emoji_semaine
        for num, emote in enumerate(emoji_semaine):
            
            #Emoji trouvé
            if emote == emoji:

                joueur_inscris = ast.literal_eval(df_event.loc[df_event['id'] == id_message, 'present'].iloc[0])[num]

                #Test si l'argument nom n'est pas dans la liste des inscrits.
                if not nom in joueur_inscris:
                    
                    #Recupère les données du DF pour les mettre à jour
                    joueur_inscris_series  =  df_event.loc[df_event['id'] == id_message, 'present'].iloc[0]
                    indexe         =  df_event.loc[df_event['id'] == id_message, 'present'].index[0]
                    nbr_present    =  df_event.loc[df_event['id'] == id_message, 'nbr_present'].iloc[0]

                    #Ajout du nom dans la liste des présents
                    liste_joueur_inscris = ast.literal_eval(joueur_inscris_series)
                    liste_joueur_inscris[num].append(nom)

                    #Incrémente le nombre de personne inscrite à l'évènnement
                    liste_nbr_present = ast.literal_eval(nbr_present)
                    nbr_present = liste_nbr_present[num] + 1

                    #Réinjecte la liste des personnes présente dans le DF
                    df_event.at[indexe, "present"] = liste_joueur_inscris
                    df_event.at[indexe, "nbr_present"] = liste_nbr_present

                    log(f'| Fonction actu_csv_varaible | {nom} ajouté au DF à la colonne présent')

                    df_event.to_csv(CHEMIN_RACINE + "/" + CHEMIN_EVENEMENT, index= False)

                else:
                    log(f'| Fonction actu_csv_varaible | {nom} à déjà voté !', 0)

            break #Une fois l'émoji trouvé, sort de la boucle for
        
        return True

    #Test si l'émoji est un emoji utilisé pour la l'inscription classiquo
    if emoji == "✅" or emoji == "❌":
        if emoji == "✅":
            
            #Test pour debug en attendant que l'erreur se reproduise :)
            try:
                liste_joueur_inscris = ast.literal_eval(df_event.loc[df_event['id'] == id_message, 'present'].iloc[0])
            except:
                logger.error("Erreur lors de la tentative de récuperation de la liste des joueurs présent !")
                logger.debug(f"ID du message: {id_message}")
                logger.debug(f"df_event:")
                logger.debug(f"{df_event}")
                logger.debug(f"Ligne recherché:")
                logger.debug(f"{df_event.loc[df_event['id'] == id_message]}")
                
                return False

            #Test si l'argument nom n'est pas dans la liste des joueurs inscrit
            if not nom in liste_joueur_inscris:

                #Recupère les données du DF pour les mettre à jour
                indexe         =  df_event.loc[df_event['id'] == id_message, 'present'].index[0]
                nbr_present    =  df_event.loc[df_event['id'] == id_message, 'nbr_present'].iloc[0]

                #Ajout du nom dans la liste des présents
                liste_joueur_inscris.append(nom)

                #Réinjecte la liste des personnes présente dans le DF
                df_event.at[indexe, "present"] = liste_joueur_inscris
                df_event.at[indexe, "nbr_present"] = int(nbr_present) + 1
                
                log(f'| Fonction actu_csv_varaible | {nom} ajouté au df à la colonne présent')

                df_event.to_csv(CHEMIN_RACINE + "/" + CHEMIN_EVENEMENT, index= False)
            else:
                log(f'| Fonction actu_csv_varaible | {nom} à déjà voté !', 0)

            liste_joueur_absent = ast.literal_eval(df_event.loc[df_event['id'] == id_message, 'absent'].iloc[0])

            #Recherche du nom dans 'absent' de la ligne id_message
            if nom in liste_joueur_absent:
                
                #Recupère les données du DF pour les mettre à jour
                indexe          =   df_event.loc[df_event['id'] == id_message, 'absent'].index[0]
                nbr_absent      =   df_event.loc[df_event['id'] == id_message, 'nbr_absent'].iloc[0]

                #Retirer le nom dans la liste des absent
                liste_joueur_absent.remove(nom)
                
                #Réinjecte la liste des personnes absente dans le DF
                df_event.at[indexe, "absent"] = liste_joueur_absent
                df_event.at[indexe, "nbr_absent"] = int(nbr_absent) - 1
                
                log(f'| Fonction actu_csv_varaible | {nom} enlevé au df à la colonne absent')

                df_event.to_csv(CHEMIN_RACINE + "/" + CHEMIN_EVENEMENT, index = False)

        if emoji == "❌":

            liste_joueur_absent = ast.literal_eval(df_event.loc[df_event['id'] == id_message, 'absent'].iloc[0])
            
            #Test si l'argument nom n'est pas dans la liste des joueurs absent
            if not nom in liste_joueur_absent:

                #Recupère les données du DF pour les mettre à jour
                indexe      =  df_event.loc[df_event['id'] == id_message, 'absent'].index[0]
                nbr_absent  =  df_event.loc[df_event['id'] == id_message, 'nbr_absent'].iloc[0]

                #Ajoute le nom dans la liste des absent
                liste_joueur_absent.append(nom)

                #Réinjecte la liste des personnes absente dans le DF
                df_event.at[indexe, "absent"] = liste_joueur_absent
                df_event.at[indexe, "nbr_absent"] = int(nbr_absent) + 1
                
                log(f'| Fonction actu_csv_varaible | {nom} ajouté au df à la colonne absent')

                df_event.to_csv(CHEMIN_RACINE + "/" + CHEMIN_EVENEMENT, index= False)
            else:
                log(f'| Fonction actu_csv_varaible | {nom} à déjà voté !', 0)
            
            liste_joueur_inscris = ast.literal_eval(df_event.loc[df_event['id'] == id_message, 'present'].iloc[0])

            #Recherche du nom dans 'absent' de la ligne id_message
            if nom in liste_joueur_inscris:

                #Recupère les données du DF pour les mettre à jour
                indexe       =  df_event.loc[df_event['id'] == id_message, 'present'].index[0]
                nbr_present  =  df_event.loc[df_event['id'] == id_message, 'nbr_present'].iloc[0]
                
                #Retire le nom dans la liste des present
                liste_joueur_inscris.remove(nom)

                #Réinjecte la liste des personnes présente dans le DF
                df_event.at[indexe, "present"]    =  liste_joueur_inscris
                df_event.at[indexe, "nbr_present"] =  int(nbr_present) - 1
                
                log(f'| Fonction actu_csv_varaible | {nom} enlevé au df à la colonne present')

                df_event.to_csv(CHEMIN_RACINE + "/" + CHEMIN_EVENEMENT, index = False)

    else:
        log(f'| Fonction actu_csv_varaible | nom non pris en compte ({nom}) !', 2)
        return False



    return True

#Fonction pour récupérer les réaction sur les embed lorsque le bot était éteind
async def recuperation_reaction_off(bot):

    #Recupère les id des messages présent dans le canal evenement
    df_message = await fonction.recuperation_id_message(bot, ID_CHANNEL_EVENT, 10)
    channel = bot.get_channel( ID_CHANNEL_EVENT )

    #Pour chaque message présent dans le canal evenement
    for _, ligne in df_message.iterrows():

        #Récupère le message à partir de son ID
        message = await channel.fetch_message( ligne['id_message'] )

        #Pour chaque reaction dans le message
        for reaction in message.reactions:
            
            #Pour chaque utilisateur qui a mit une émote
            async for user in reaction.users():

                #Test que ce ne soit pas le BOT
                if not user.id == ID_BOT:

                    print('')
                    print(f"Emoji: {reaction.emoji}, Réactions: {reaction.count} pour message {message.id}")

                    resultat = actu_csv_varaible(reaction.emoji, user.global_name, message.id)
                    
                    if not resultat:
                        logger.error("Risque d'erreur sur la récupération reaction ! ! !")

                    df_message = pd.read_csv( CHEMIN_RACINE + '/' + CHEMIN_EVENEMENT)
                    ligne = df_message[df_message['id'] == message.id]
                    
                    await message.remove_reaction(reaction, user)      

                    emoji_inscription = ['✅','❌']
                    if reaction.emoji in emoji_inscription:
                        await message.edit(embed= embed_inscriptions(ligne['titre'].iloc[0],
                                                              ligne['description'].iloc[0],
                                                              ligne['date'].iloc[0],
                                                              ast.literal_eval(ligne['present'].iloc[0]),
                                                              ligne['nbr_present'].iloc[0],
                                                              ast.literal_eval(ligne['absent'].iloc[0])))
                    
                    emoji_inscription_hebdo = ['🇱', '🇲', 'Ⓜ️','🇯', '🇻', '🇸', '🇩']
                    if reaction.emoji in emoji_inscription_hebdo:
                        await message.edit(embed= embed_inscription_semaine(
                                                              ligne['date'].iloc[0],
                                                              ligne['nbr_present'].iloc[0]))



    return True

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

        emoji_hebdo = "🇱 🇲 Ⓜ️ 🇯 🇻 🇸 🇩"
        #Check si l'emote est la coche ou la croix
        if emoji.name  == "✅" or emoji.name  == "❌" or emoji.name in emoji_hebdo:
            print("Emoji trouvé !")
            csv_embed = fonction.csv_recup('csv/varaible.csv')
            n_embed = fonction.recherche_embed(csv_embed, message.id)
        else:
            return

        #Regarde si la réaction est sur le bonne embed
        if int(csv_embed[n_embed][0]) == message.id and n_embed != -1:

            #Actualise le csv_varaible
            resultat = actu_csv_varaible(emoji.name, payload.member.global_name, message.id)
            
            if not resultat:
                        logger.error("Risque d'erreur sur la récupération reaction ! ! !")

            if emoji.name  == "✅" or emoji.name  == "❌":
                #Récupère le csv pour l'embed inscriptions
                df_message = pd.read_csv( CHEMIN_RACINE + '/' + CHEMIN_EVENEMENT)
                ligne = df_message[df_message['id'] == message.id]
                
                #Supprime la réaction et met à jour l'embed
                await message.remove_reaction(emoji, member)     
                await message.edit(embed= embed_inscriptions(ligne['titre'].iloc[0],
                                                    ligne['description'].iloc[0],
                                                    ligne['date'].iloc[0],
                                                    ast.literal_eval(ligne['present'].iloc[0]),
                                                    ligne['nbr_present'].iloc[0],
                                                    ast.literal_eval(ligne['absent'].iloc[0])))

                log(f"{payload.member.global_name} inscrit/désinscrit dans {csv_embed[n_embed][1]}", 0)
            else:
                #Récupère le csv pour l'embed inscriptions
                df_message = pd.read_csv( CHEMIN_RACINE + '/' + CHEMIN_EVENEMENT)
                ligne = df_message[df_message['id'] == message.id]
                
                #Supprime la réaction et met à jour l'embed
                await message.remove_reaction(emoji, member)     
                await message.edit(embed= embed_inscription_semaine(
                                                    ligne['date'].iloc[0],
                                                    ligne['nbr_present'].iloc[0]))

                log(f"{payload.member.global_name} inscrit/désinscrit dans {csv_embed[n_embed][1]}", 0)


        print(f"Réaction: {emoji.name} ajouté sur un message par {payload.member.global_name}.")

#Detecte la suppression d'une réaction
async def on_raw_reaction_remove(payload, bot):
    1

