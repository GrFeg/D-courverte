from datetime import datetime
import csv
import os
from pathlib import Path
import json
import pandas as pd
import re

"""
Fichier python contenant des fonction utilitaires

"""
def est_emoji_valide(texte_a_tester) -> bool:
    """
    Renvoit True si le texte contient un Emoji, sinon renvoit False.
    
    Fonctionne pour detecter si un caractère dans un texte est un emoji ou bien pour tester un caractère bien précis.

    ### Argument:
    - texte_a_tester (str) : chaine de caractère a tester.
    """
    emoji_pattern = re.compile(
    "[\U0001F600-\U0001F64F" #Emoticônes
    "\U0001F300-\U0001F5FF"  #Symboles et pictogrammes divers
    "\U0001F680-\U0001F6FF"  #Transports et symboles de carte
    "\U0001F1E0-\U0001F1FF"  #Drapeaux
    "\U00002700-\U000027BF"  #Divers symboles
    "\U000024C2-\U0001F251" 
    "]+", flags=re.UNICODE)

    return bool(emoji_pattern.search(texte_a_tester))


def fichier_existe(chemin):
    script_dir = os.path.dirname(__file__)  # Répertoire du script Python
    chemin_dossier = os.path.join(script_dir, chemin)

    if os.path.exists(chemin_dossier):
        return True
    else:
        return False


def log(message, num = 1):
    '''
    Permet d'afficher les messages dans la console avec un affichage plus esthétique:

    Variable num:
    Debug- 0
    Succés- 1
    Echec- 2
    Message- 3
    '''
    heure = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if num == 0:
        print(f"{heure} \033[34mINFO\033[0m ㅤㅤ{message}")
    if num == 1:
        print(f"{heure} \033[32mSUCCEE\033[0m ㅤ{message}")
    elif num == 2:
        print(f"{heure} \033[31mECHEC\033[0m ㅤㅤ{message}")
    elif num == 3:
        print(message)

if os.path.isfile( Path('config.json')):
    #Récupération des configurations du bot
    with open('config.json') as config_file:
        config = json.load(config_file)

    TOKEN = config['TOKEN']
    ID_JOUEUR_PIZZABLEU = config['ID_JOUEUR_PIZZABLEU']
    ID_JOUEUR_CLOUD = config['ID_JOUEUR_CLOUD']
    ID_BOT = config['ID_BOT']
    ID_BOT_MIOUNE = config['ID_BOT_MIOUNE']
    ID_GUILD_SERVEUR_INAE = config['ID_GUILD_SERVEUR_INAE']
    ID_CHANNEL_EVENT = config['ID_CHANNEL_EVENT']
    ID_CHANNEL_TEST = config['ID_CHANNEL_TEST']

    CHANNEL_ID_LOGS = 892509041140588581 
    CHEMIN_HISTO_LOGS = 'csv/histo_logs.csv'
    CHEMIN_RACINE = script_dir = os.path.dirname(__file__)

else:
    log("Fichier config.json introuvable", 3)


def csv_recup(chemin: str):
    '''
    Ouvrir un fichier CSV et recuperer l'intégralité du fichier dans une liste
    csv_liste = [[Ligne 1],[Ligne 2], ... ]

    '''
    if fichier_existe(chemin):
        with open(chemin, mode='r', encoding = 'utf-8') as fichier:
            lecteur_csv = csv.reader(fichier)
            csv_embed = []
            for ligne in lecteur_csv:
                csv_embed += [ligne]
        
        nom_du_csv = chemin.split('/')
        nomducsv = nom_du_csv[-1]
        log(f"CSV {nomducsv} recupéré",0)
        return csv_embed
    
    else:

        log(f"Le fichier {chemin} n'existe pas ! !", 2)


def csv_ajout(chemin: str, contenu):
    '''
    Ajoute une ligne a un fichier csv
    '''
    if fichier_existe(chemin):
        with open(chemin, 'a', newline='', encoding='utf-8') as csv_variable:
            ecrire = csv.writer(csv_variable)
            ecrire.writerow(contenu)

        nom_du_csv = chemin.split('/')
        nom_du_csv = nom_du_csv[-1]
        log(f"CSV {nom_du_csv} rajouté",0)

    else:

        log(f"Le fichier {chemin} n'existe pas ! !", 2)


def csv_actu(chemin: str, contenu: list):
    '''
    Réecrire l'entièreté du csv avec le contenu. Ecrase toute les données !

    '''
    if fichier_existe(chemin):

        with open(chemin, 'w', newline='', encoding='utf-8') as csv_variable:
            ecrire = csv.writer(csv_variable)
            ecrire.writerows(contenu)

        nom_du_csv = chemin.split('/')
        nom_du_csv = nom_du_csv[-1]
        log(f"CSV {nom_du_csv} remplacé",0)
    
    else:

        log(f"Le fichier {chemin} n'existe pas ! !", 2)

#Recherche si l'id d'un embed existe
def recherche_embed(csv_embed, embed_id):
    '''
    Recherche si l'id d'un embed est dans la variable d'un csv sous forme de liste.
    Si oui renvoit la ligne, si non renvoit -1
    '''
    
    for i, e in enumerate(csv_embed):
        if str(embed_id) in e:
            return i
    return -1 #Pour erreur

#Récupere les messages dans un canal
async def recuperation_message(bot, channel_id, nbr_messages, 
                               save_csv = False, chemin_csv = ""):
    '''
    Fonction qui permet de récuperer n nombres de messages dans un canal donné.
    '''

    channel = bot.get_channel(channel_id)

    #Si le canal existe
    if channel_id == CHANNEL_ID_LOGS:
        liste_logs = []
        liste_date = []
        liste_boss = []

        async for message in channel.history( limit= nbr_messages ):
            
            #Nettoyage
            message_sep = message.content.split('\n')
            #Si le message comporte plusieurs liens
            for message_sep_pars in message_sep:
                if not message_sep_pars == "":
                    if message_sep_pars[0] == "h":
                        liste_logs.append( message_sep_pars.split(' ')[0] )
                        liste_date.append( message_sep_pars.split('-')[1] )
                        liste_boss.append( message_sep_pars.split('_')[1] )

        #Création du DataFrame
        dico = {'date' : liste_date,
                'boss' : liste_boss,
                'logs' : liste_logs}
        
        df_historique_logs = pd.DataFrame(dico)

        if save_csv == True:
            df_historique_logs.to_csv(CHEMIN_RACINE + '/' + chemin_csv, index= False)


        log("Messages logs recupérés")  
        return df_historique_logs
    
    elif channel_id == ID_CHANNEL_EVENT or channel_id == ID_CHANNEL_TEST:
        async for message in channel.history( limit= nbr_messages ):

            liste_message = []
            
            #Nettoyage
            message_sep = message.content.lower().split('\n')
            #Si le message comporte plusieurs liens
            for message_sep_pars in message_sep:
                liste_message.append(message_sep_pars)

            dico = {'message' : liste_message} 

            log("Messages evenement recupérés")
            return pd.DataFrame(dico)

async def recuperation_id_message(bot, channel_id, nbr_messages):

    channel = bot.get_channel(channel_id)
    liste_id_message = []
    async for message in channel.history( limit= nbr_messages ):
        liste_id_message.append( message.id )

    dico = {'id_message' : liste_id_message}
    df = pd.DataFrame(dico)
    return df   

