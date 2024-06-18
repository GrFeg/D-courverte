import os
from pathlib import Path
import json
from fonction import log
from datetime import datetime
import locale
import discord
import fonction
import pandas as pd

DICO_NOM_BOSS_RAID = {
        "W1" : ["Gardien de la valée","Groseval","Sabetha"],
        "W2" : ["Slothasor","Trio","Mathias"],
        "W3" : ["Escorte","Titan du fort ","Xera"],
        "W4" : ["Cairn","Mursaat","Samarog","Deimos"],
        "W5" : ["Horreur sans âme","Rivière","Dhuum"],
        "W6" : ["Amalgame conjuré","Jumeaux Largos","Qadim"],
        "W7" : ["Sabir","Adina","Qadim l'inégalé"]
            }

DICO_EQUIVALENT_ABREGEE_NOM = {
        "vg" : "Gardien de la valée",
        "gors" : "Groseval",
        "sab" : "Sabetha",
        "sloth" : "Slothasor",
        "trio" : "Trio",
        "mat" : "Mathias",
        "esc" : "Escorte",
        "kc" : "Groseval",
        "xera" : "Xera",
        "cairn" : "Cairn",
        "mo" : "Mursaat",
        "sam" : "Samarog",
        "dei" : "Deimos",
        "sh" : "Groseval",
        "river" : "Groseval",
        "dhuum" : "Dhuum",
        "ca" : "Amalgame conjuré",
        "twins" : "Jumeaux Largos",
        "qadim" : "Qadim",
        "adina" : "Adina",
        "sabir" : "Sabir",
        "qpeer" : "Qadim l'inégalé"
}


if os.path.isfile( Path('config.json') ):
    #Récupération des configurations du bot
    with open('config.json') as config_file:
        config = json.load(config_file)

    TOKEN = config['TOKEN']
    ID_JOUEUR_PIZZABLEU = config['ID_JOUEUR_PIZZABLEU']
    ID_JOUEUR_CLOUD = config['ID_JOUEUR_CLOUD']
    ID_BOT = config['ID_BOT']
    ID_BOT_MIOUNE = config['ID_BOT_MIOUNE']
    ID_GUILD_SERVEUR_INAE = config['ID_GUILD_SERVEUR_INAE']

    CHANNEL_ID_LOGS = 892509041140588581 
    ID_CHANNEL_TEST = config['ID_CHANNEL_TEST']
    CHEMIN_BOSS_HEBDO = 'csv/boss_done_hebdo.csv'
    CHEMIN_RACINE = script_dir = os.path.dirname(__file__)

    locale.setlocale(locale.LC_TIME, 'fr_FR')
    date_du_jour = datetime.now()

else:
    log("Fichier config.json introuvable", 3)

#Fonction qui va actualiser le fichier Boss_done_hebdo en fonction des boss tombé dans hsito_log
def ajout_boss_hebdo_via_histo(df_histo_message: pd.DataFrame):

    #Recupère le fichier boss_done_hebdo
    df_boss_hebdo = pd.read_csv(CHEMIN_RACINE + "/" + CHEMIN_BOSS_HEBDO, index_col = 'num_sem')

    #Pour chaque ligne de df_histo_mesage
    for indexe, ligne in df_histo_message.iterrows():

        #Convertis la date et récupère le n° de semaine
        date = datetime.strptime( str(ligne['date']),"%Y%m%d" )
        numero_semaine = int( date.strftime('%W') )

        #Si le num de semainez correspond à la semaine en cours
        if numero_semaine == int( date_du_jour.strftime('%W') ):
             
             #Si le boss existe dans la liste des abréviations
             if ligne['boss'] in DICO_EQUIVALENT_ABREGEE_NOM:
                 print('Jackpot pour ', ligne['boss'])

                 #MANQUE A VERIFIER SI LE BOSS EST BIEN TOMBE ! ! ! ! ! ! ! 

                 #Met ce boss à True (car tombé) 
                 df_boss_hebdo.at[numero_semaine, ligne['boss']] = True
   
             else:
                  log( f"Boss non trouvé {ligne['boss']}", 2 )
    
    #Remplace toutess les valeurs nulle par False
    df_boss_hebdo = df_boss_hebdo.fillna("False")
    print(df_boss_hebdo)
    
    #Enregistre le df
    df_boss_hebdo.to_csv(CHEMIN_RACINE + "/" + CHEMIN_BOSS_HEBDO)

    return df_boss_hebdo

#Fonction qui définit l'embed de recap_hebdo
def embed_quel_raids(dico_info_raid_done: dict):

    #Récupère le numero de la semaine en cours
    numero_semaine = int(date_du_jour.strftime("%W"))

    #Définition de l'embed
    embed_info_raid = discord.Embed(title="Récap de la Guilde :", description= "\u200b", color=discord.Color.blue())
    embed_info_raid.add_field(name = "" , value = "Liste les ailes tombé par la guilde et les ailes bonus" , inline = False)
    embed_info_raid.add_field(name = "\u200b" , value = "" , inline = False)

    #Définitions de l'aile en hardiesse et double gold en focntion du numero de semaine en cours
    hardiesse = numero_semaine % 7 + 2
    gold = numero_semaine % 7 + 3

    #Pour chaque Aile de raid (7)
    compteur = 0
    for i in range(7):
        compteur += 1
        affichage = ""

        for e in range(len(DICO_NOM_BOSS_RAID['W' + str(compteur)])):
            if dico_info_raid_done['W' + str(compteur)][e] == True:
                affichage += f"ㅤ- {DICO_NOM_BOSS_RAID['W' + str(compteur)][e]} : ✅  ㅤㅤ\n"
            else:
                affichage += f"ㅤ- {DICO_NOM_BOSS_RAID['W' + str(compteur)][e]} : ❌ ㅤㅤ\n" 

        if compteur == hardiesse:
            embed_info_raid.add_field(name = f"# Aile {str(compteur)} : (Hardiesse)" , value = affichage , inline = True)
        elif compteur == gold:
            embed_info_raid.add_field(name = f"# Aile {str(compteur)} : (Double Gold)" , value = affichage , inline = True)
        else:
            embed_info_raid.add_field(name = f"# Aile {str(compteur)} :" , value = affichage , inline = True)

        if compteur == 2 or compteur ==  4 or compteur == 6 or compteur == 8:
                        embed_info_raid.add_field(name="\u200b", value='', inline=False)



    return embed_info_raid

#Fonction pour acutaliser l'embed recap_hebdo
async def actualisation_embed(bot, df_histo_message):

    df_boss_hebdo = ajout_boss_hebdo_via_histo(df_histo_message)
    numero_semaine = int( date_du_jour.strftime('%W') )


    #Si on est lundi RESET des infos
    if date_du_jour.strftime("%A") == "lundi" : #RESTE A VOIR LA DATE POUR EVITER CONFLIT LE LUNDI SI APRES 21H ! ! ! ! ! ! ! ! !

        dico_info_raid_done = {
            "W1" : [False, False, False],
            "W2" : [False, False, False],
            "W3" : [False, False, False],
            "W4" : [False, False, False, False],
            "W5" : [False, False, False],
            "W6" : [False, False, False],
            "W7" : [False, False, False],
        }

    else:
         print(df_boss_hebdo)
         dico_info_raid_done = {
            "W1" : [df_boss_hebdo.iloc[numero_semaine]['vg'], False, False],
            "W2" : [False, False, False],
            "W3" : [False, False, False],
            "W4" : [False, False, False, False],
            "W5" : [False, False, False],
            "W6" : [False, False, False],
            "W7" : [False, False, False],
        }
         print(dico_info_raid_done)


    embed = embed_quel_raids(dico_info_raid_done)

    try:
        channel = bot.get_channel(ID_CHANNEL_TEST)
        message = await channel.fetch_message( 1252744415370285056 )
        message_trouve = True
    except:
        log("Fonction actualisation_embed : EMBED ou CHANNEL non trouvé ! ! !", 2)
        message_trouve = False

    if not message_trouve:
            print("Envoit de l'embed sur discord ! ")
            await channel.send( embed = embed )   
    else:
            print('Envoit de l embed')
            await message.edit( embed  = embed )
              
        






    
