import os
import json
from config_logger import logger
from datetime import datetime
import locale
import discord
import pandas as pd
from boss import Boss
from typing import Type


DICO_NOM_BOSS_RAID = {
        "W1" : ["Gardien de la valée","Groseval","Sabetha"],
        "W2" : ["Slothasor","Trio","Mathias"],
        "W3" : ["Escorte","Titan du fort","Chateau Corrompu","Xera"],
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
        "matt" : "Mathias",
        "esc" : "Escorte",
        "kc" : "Groseval",
        "tc" : "Chateau Corrompu",
        "xera" : "Xera",
        "cairn" : "Cairn",
        "mo" : "Mursaat",
        "sam" : "Samarog",
        "dei" : "Deimos",
        "sh" : "Groseval",
        "rr" : "Groseval",
        "dhuum" : "Dhuum",
        "ca" : "Amalgame conjuré",
        "twins" : "Jumeaux Largos",
        "qadim" : "Qadim",
        "adina" : "Adina",
        "sabir" : "Sabir",
        "qpeer" : "Qadim l'inégalé"
}


chemin_fichier_config = '_donnee/config.json'

if os.path.isfile(chemin_fichier_config):
    #Récupération des configurations du bot
    with open(chemin_fichier_config) as config_file:
        config = json.load(config_file)

    CHANNEL_ID_LOGS = 892509041140588581 
    ID_CHANNEL_TEST = config['ID_CHANNEL_TEST']
    CHEMIN_BOSS_HEBDO = 'csv/boss_done_hebdo.csv'

    locale.setlocale(locale.LC_TIME, 'fr_FR')
    date_du_jour = datetime.now()

else:
    logger.critical("affichage_info Fichier config.json introuvable")

#Renvoit True or False si le boss est mort ou non
def test_si_boss_mort(lien: str):

    #Extrait la date du lien
    date_essais = (lien.split('-')[1] + '-' + lien.split('-')[2]).split('_')[0]

    #Extrait le raccourcis_boss du lien
    raccourcis_boss = lien.split('_')[1]

    boss = Boss.instances[raccourcis_boss]
    boss: Type[Boss]

    return boss.boss_mort_ou_vivant(date_essais)

#Fonction qui initialise la ligne de la semaine en cours à False si la ligne n'existe pas, sinon rien.
def init_semaine_df():
    
    df_boss_hebdo = pd.read_csv(CHEMIN_BOSS_HEBDO, index_col = 'num_sem')
    numero_semaine = int( date_du_jour.strftime('%W') )
    
    if not numero_semaine in df_boss_hebdo.index:
        logger.debug(f"Semaine: {numero_semaine} non trouvée dans le df, initialisation de la ligne à False")
        df_boss_hebdo.loc[numero_semaine] = [False] * len(df_boss_hebdo.columns)
    
    df_boss_hebdo.to_csv(CHEMIN_BOSS_HEBDO)

#Fonction qui va actualiser le fichier Boss_done_hebdo en fonction des boss tombé dans hsito_log
def ajout_boss_hebdo_via_histo(df_histo_message: pd.DataFrame):

    #Recupère le fichier boss_done_hebdo
    df_boss_hebdo = pd.read_csv(CHEMIN_BOSS_HEBDO, index_col = 'num_sem')

    #Pour chaque ligne de df_histo_mesage
    for _, ligne in df_histo_message.iterrows():

        #Convertis la date et récupère le n° de semaine
        date = datetime.strptime( str(ligne['date']),"%Y%m%d" )
        numero_semaine = int( date.strftime('%W') )

        #Si le num de semainez correspond à la semaine en cours
        if numero_semaine == int( date_du_jour.strftime('%W') ):
             
             #Si le boss existe dans la liste des abréviations
             if ligne['boss'] in DICO_EQUIVALENT_ABREGEE_NOM:
                
                 print(ligne['logs'])

                 if test_si_boss_mort(ligne['logs']):
                    #Met ce boss à True (car tombé) 
                    df_boss_hebdo.at[numero_semaine, ligne['boss']] = True
    
             else:
                  logger.debug( f"Boss non trouvé {ligne['boss']}", 2 )
    
    #Remplace toutess les valeurs nulle par False
    df_boss_hebdo = df_boss_hebdo.fillna("False")
    
    #Enregistre le df
    df_boss_hebdo.to_csv(CHEMIN_BOSS_HEBDO)

    return df_boss_hebdo

#Fonction qui définit l'embed de recap_hebdo
def embed_quel_raids(dico_info_raid_done: dict):

    #Récupère le numero de la semaine en cours
    numero_semaine = int(date_du_jour.strftime("%W"))

    #Définition de l'embed
    embed_info_raid = discord.Embed(title="Récap de la Guilde :", description= "\u200b", color=discord.Color.blue())
    embed_info_raid.add_field(name = "" , value = "Liste les ailes tombées par la guilde et les ailes bonus" , inline = False)
    embed_info_raid.add_field(name = "\u200b" , value = "" , inline = False)

    #Définitions de l'aile en hardiesse et double gold en focntion du numero de semaine en cours
    hardiesse = (numero_semaine + 1) % 7 + 1
    gold = (numero_semaine + 2) % 7 + 1


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
async def actualisation_embed(bot, df_histo_message: pd.DataFrame):
    print("prout")
    df_boss_hebdo = ajout_boss_hebdo_via_histo(df_histo_message)
    numero_semaine = int( date_du_jour.strftime('%W') )

    #Si on est lundi RESET des infos
    if date_du_jour.strftime("%A") == "lundi" and  int(date_du_jour.strftime("%H")) < 21 or not numero_semaine in df_boss_hebdo.index: 

        dico_info_raid_done = {
                "W1" : [False, False, False],
                "W2" : [False, False, False],
                "W3" : [False, False, False, False],
                "W4" : [False, False, False, False],
                "W5" : [False, False, False],
                "W6" : [False, False, False],
                "W7" : [False, False, False],
            }
    else:
         series_semaine = df_boss_hebdo.loc[numero_semaine]
         dico_info_raid_done = {
            "W1" : [series_semaine['vg'], series_semaine['gors'], series_semaine['sab']],
            "W2" : [series_semaine['sloth'], series_semaine['trio'], series_semaine['matt']],
            "W3" : [series_semaine['esc'], series_semaine['kc'],series_semaine['tc'], series_semaine['xera']],
            "W4" : [series_semaine['cairn'], series_semaine['mo'], series_semaine['sam'], series_semaine['dei']],
            "W5" : [series_semaine['sh'], series_semaine['rr'], series_semaine['dhuum']],
            "W6" : [series_semaine['ca'], series_semaine['twins'], series_semaine['qadim']],
            "W7" : [series_semaine['sabir'], series_semaine['adina'], series_semaine['qpeer']],
        }

    embed = embed_quel_raids(dico_info_raid_done)

    try:
        channel = bot.get_channel(ID_CHANNEL_TEST)
        message = await channel.fetch_message( 1252744415370285056 ) #Message embed déjà envoyé A automatiser ! ! ! ! !
        message_trouve = True
    except:
        logger.error("Fonction actualisation_embed : EMBED ou CHANNEL non trouvé ! ! !")
        message_trouve = False

    if not message_trouve:
            await channel.send( embed = embed )   
    else:
            await message.edit( embed  = embed )
              
        






    
