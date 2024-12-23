import pandas as pd
import os
import json
from datetime import datetime
from config_logger import logger
import requests
from bs4 import BeautifulSoup
import fonction
from typing import Type
import re

'''
Fichier qui contient la Class Boss et toutes les fonctions touchant au combat de boss.


'''
chemin_fichier_info = '_donnee/info.json'
chemin_fichier_config = '_donnee/config.json'

if os.path.isfile(chemin_fichier_info):
    #Récupération des configurations du bot
    with open(chemin_fichier_info, encoding= 'utf-8') as config_file:
        INFO_RAID = json.load(config_file)['raid']
else:
    logger.critical("boss, Fichier info_raid.json introuvable")

if os.path.isfile(chemin_fichier_config):
    #Récupération des configurations du bot
    with open(chemin_fichier_config) as config_file:
        config = json.load(config_file)

    ID_JOUEUR_PIZZABLEU = config['ID_JOUEUR_PIZZABLEU']
    ID_JOUEUR_CLOUD = config['ID_JOUEUR_CLOUD']
    ID_JOUEUR_ELNABO = config['ID_JOUEUR_ELNABO']
    ID_BOT = config['ID_BOT']

    CHEMIN_HISTO_LOGS = '/csv/histo_logs.csv'
    CHEMIN_BOSS_HEBDO = 'csv/boss_done_hebdo.csv'
    CHEMIN_RACINE = os.path.dirname(__file__) 

    date_du_jour = datetime.now()
    numero_semaine = int( date_du_jour.strftime('%W') )
else:
    logger.critical("Fichier config.json introuvable")


class Boss:
    '''
    Class qui définit tout les boss présent dans le jeu, leurs noms (anglais et français) et le raccourcis utilisé dans les liens dps.report.
    Stocke tout les Data Frame du boss

    Fonction recherche_combat_existe_dans_Boss: Test si l'ID est dans le df_global -> Renvoit True ou False
    Fonction boss_mort_ou_vivant: Test si le boss est mort ou non -> Renvoit True ou False
    Fonction boss_en_cm: Test si le boss est en cm ou non -> Renvoit True ou False
    '''

    instances = {}
    nbr_boss = 0
    
    def __init__(self, nom_francais: str, nom_anglais: str, raccourcis_nom: str, aile: str):

        #Stockage des variables renseigné dans init
        nom_francais = nom_francais.replace('Ã©','é')
        
        self.nom_francais = nom_francais
        self.nom_anglais = nom_anglais
        self.raccourcis_nom = raccourcis_nom
        self.aile = aile

        #Ouverture du fichier boss_done_hebdo
        df_boss_hebdo = pd.read_csv(CHEMIN_RACINE + "/" + CHEMIN_BOSS_HEBDO, index_col = 'num_sem')

        #Recherche et ajout de la variable mort_hebdo
        try:
            self.mort_hebdo =  df_boss_hebdo.loc[numero_semaine][raccourcis_nom]
        except KeyError:
            logger.error(f"mort_hebdo non pris en charge pour {raccourcis_nom}")
            self.mort_hebdo = None


        #Recupérer tout les df du boss et le stocker dans dico_df
        self.chemin_dossier = os.path.join(CHEMIN_RACINE, 'log_boss_df', raccourcis_nom)

        #Test si le chemin existe
        if os.path.isdir(self.chemin_dossier):
            fichiers = os.listdir(self.chemin_dossier)
            
            dico_df = {}
            #Lis chaque fichier dans le fichier Boss.
            for fichier in fichiers:
                nom = fichier.split('.')[0]
                dico_df[nom] = pd.read_csv(self.chemin_dossier + '\\' + fichier)

            #Si on a pas 11 df
            if not len(dico_df) == 11:
                logger.error(f"Fichier dans {raccourcis_nom} manquant, risque d'erreur probable.")

        else:
            logger.error(f"Le dossier {self.chemin_dossier} n'éxiste pas !")
            dico_df = -1

        
        #Test si chaque df existe bien dans le dict et le charge.
        if type(dico_df) == dict:
            if 'Stats_global' in dico_df:
                self.df_global = dico_df['Stats_global']
            else:
                logger.error(f'{raccourcis_nom}: Stats_global non trouvé, erreur ! ')
            
            if 'Stats_DPS' in dico_df:
                self.df_dps = dico_df['Stats_DPS']
            else:
                logger.error(f'{raccourcis_nom}: Stats_DPS non trouvé, erreur ! ')

            if 'Boons_gen_group' in dico_df:
                self.df_gen_group = dico_df['Boons_gen_group']
            else:
                logger.error(f'{raccourcis_nom}: Boons_gen_group non trouvé, erreur ! ')

            if 'Boons_uptime' in dico_df:
                self.df_boon_uptime = dico_df['Boons_uptime']
            else:
                logger.error(f'{raccourcis_nom}: df_boon_uptime non trouvé, erreur ! ')

            if 'mecanique' in dico_df:
                self.df_mecanique = dico_df['mecanique']
            else:
                logger.error(f'{raccourcis_nom}: mecanique non trouvé, erreur ! ')
        else:
            logger.error(f"L'instance de {raccourcis_nom} n'a pas pu charger les df")

        self.__class__.instances[self.raccourcis_nom] = self
        Boss.nbr_boss += len(self.__class__.instances.keys())
        
        logger.info(f"Instance {self.raccourcis_nom} créee ! ")

        
    #Fonction pour savoir si un combat existe dans l'instance du boss ou non, return True or False
    def recherche_combat_existe_dans_Boss(self, date_essais : str) -> bool:
        """
        Recherche si un log existe dans la Base de donnée, si oui renvoit True, si non renvoit False
        """
        #Test si la variable existe
        if not hasattr(self, 'df_global'):
            logger.error(f'Fonction recherche_combat_dans_Boss : Erreur, le df n\'est pas chargé ! ! !')
            return -1

        #Test si date est dans le df_global
        if  date_essais in self.df_global['ID'].values:
            return True
        else:
            return False
        
    def boss_mort_ou_vivant(self, date_essais : str) -> bool:
        """
        Recherche si le boss correspondant a la date a été tué ou non.
        
        Prend en entrée la date du boss, sous forme "20240514-221721" \n
        Fonction qui a pour but de rechercher dans le df_global du boss si le boss est combat est réussis ou non.
        Renvoit -1 si le boss n'existe pas dans le df
        Renvoit True / False si le boss est mort ou non.
        """

        #Test si la du boss existe dans le df
        if self.recherche_combat_existe_dans_Boss(date_essais) == True:

            #Recupère le pourcentage de point de vie du boss
            success = self.df_global['Success'][self.df_global['ID'] == date_essais].iloc[0]

            #Si le % est égale à 0 alors le boss est mort, renvoit True
            if success:
                return True
            else: #Sinon False
                return False
             
        elif self.recherche_combat_existe_dans_Boss(date_essais) == False: #Si le boss n'existe pas
            logger.error(f"Le boss à la date {date_essais} n'existe pas!")
            return -1
        
        else: #Erreur
            logger.error("Erreur!")
            return -1

    def boss_en_cm(self, date_essais : str):
        """
        Prend en entrée la date du boss, sous forme "20240514-221721"
        Fonction qui retourne True si le boss est en CM, sinon False
        """

        #Test si la date du boss existe dans le df
        if self.recherche_combat_existe_dans_Boss(date_essais) == True:
            nom_boss = self.df_global['Boss'][self.df_global['ID'] == date_essais].iloc[0]

            #Si il y CM dans le nom du boss alors renvoit True
            if "CM" in nom_boss:
                return True
            else: #Sinon False
                return False
        
        elif self.recherche_combat_existe_dans_Boss(date_essais) == False: #Si le boss n'existe pas
            logger.error(f"Le boss à la date {date_essais} n'existe pas!")
            return -1
        
        else: #Erreur
            logger.error("Erreur dans le recherche de cm")
            return -1

    def nom_boss_existe(raccourcis):
        try:
            Boss.instances[raccourcis]
            return True
        except:
            return False

#Prend un string en entrée et renvoit une liste de lien de logs.
def traitement_message_log(message : str) -> list[str]:
    """
    Fonction qui isole les liens dps.report et les renvoit sous forme de liste
    """
    liste_log =  re.findall(r"https://dps.report/[\w]+-20[0-9]+-[0-9]+_[a-z]{2,5}", message)

    return liste_log

#Fonction qui prend les df d'un boss pour actualisé les fichiers des boss
def ajout_boss(raccourcis_nom, df_global, df_dps, df_gen_group, df_uptime, df_mecanique):

    chemin = '/log_boss_df/' + raccourcis_nom
    l_chemin = ['\\Stats_global.csv', '\\Stats_DPS.csv', '\\Boons_gen_group.csv', '\\Boons_uptime.csv', '\\mecanique.csv']
    nom_df = ['df_global', 'df_dps', 'df_gen_group', 'df_boon_uptime', 'df_mecanique']
    l_df = [df_global, df_dps, df_gen_group, df_uptime, df_mecanique]
    compteur = 0

    #Pour chaque df, met a jour le bon fichier
    for df in l_df:
        print(l_chemin[compteur])
        #Regarde si le fichier existe
        if os.path.isfile(CHEMIN_RACINE + chemin + l_chemin[compteur]):
            df_fichier = pd.read_csv(CHEMIN_RACINE + chemin + l_chemin[compteur], index_col=None)
            
        else:
            logger.error(f"Le fichier {l_chemin[compteur]} n'existe pas ! !")
            return -1
            
        id_boss = df['ID'].iloc[0]
        if str(id_boss) in df_fichier['ID'].values:
            logger.debug(f'Combat ID: {id_boss} pour le fichier {l_chemin[compteur]} existe déjà')
            compteur += 1
            continue
            

        df_fichier = pd.concat([df_fichier, df], ignore_index=True)
        print(df_fichier)

        df_fichier.to_csv(CHEMIN_RACINE + chemin + l_chemin[compteur], index= False, encoding= "utf-8")
        print(l_chemin[compteur] + " : OK " + str(compteur))
        setattr(Boss.instances[raccourcis_nom], nom_df[compteur], df_fichier)
        compteur += 1

    

    return True

#Scrap d'un site, prend le liens en entrée
def scrap(lien: str):
    requete = requests.get(lien)
    page = requete.content
    soup = BeautifulSoup(page, features="html.parser")
    logger.info("Log de raid mis en soup")

    print(type(soup.text))

    if "error" in soup.text:
        logger.error(f"| Fonction ajout_boss() | Le lien n'existe pas ! ! ! {lien}")
        return -1
    return soup

#Fonction qui prend un lien de dps.report et le convertis pour mettre à jour les df
def traiterLogs(lien: str):
        '''
        lien: Lien du raid.
        Fonction qui va prendre en entrée un lien de raid propre.
        Si l'instance dans Combat de ce lien n'existe pas, va scrapper le site, traiter les données et l'enregistrer dans le csv correspondant.
        Sinon ne fait rien
        Return True si l'instance existe. Sinon renvoit les data bruts du site.
        '''
        #Définir les variables clés
        raccourcis_nom = lien[lien.index('_') +1 :]
        date_essais = lien[lien.index('-') +1 : lien.index('_')]
        date_essais = datetime.strptime(date_essais, '%Y%m%d-%H%M%S')

        #Récupèrer le soup
        logger.debug("Scrappage du site")
        soup = scrap(lien)
        if soup == -1:
            logger.error(f"Le lien n'a pas pu être soup, traiterLogs avorté ! ! !")
            return -1
    
        fonction.csv_actu('csv/debbug_log.csv', soup) #Ligne pour debbug, voir le scrap.

        #Traite le soup, en récuperant que la partis dictionnaire
        soup = str(soup)
        soup = soup[soup.index("var _logData = ") + 15:]
        soup = soup[:soup.index(";")]

        #Convertis le soup (str) en dico
        data = json.loads(soup)

        #récuperer la durée du boss et la convertir en secondes
        duree_boss = data["encounterDuration"]
        duree_boss = duree_boss.rstrip("ms").replace(" ","")
        duree_boss = int(duree_boss[0:duree_boss.index('m')]) * 60 + int(duree_boss[duree_boss.index('m')+1:duree_boss.index('s')])
        
        log_boss = {}
        #Test si c'est une cm ou non
        if "CM" in data['fightName']:
            log_boss['cm'] = True
        else:
            log_boss['cm'] = False

        #Récupère les mecaniques prises sur le Boss
        mecanique_desc = []
        mechanicMap = data["mechanicMap"] #[{},{},{}] chaque dict est une mécanique
        #Pour chaque mécanique
        for mecs in mechanicMap:
            #Test si la mécaniques a été prise
            if mecs["playerMech"] == True:
                #Tranforme temporairement les ' dans les noms des mécaniques pour éviter les conflits
                mecs["description"] = mecs["description"].replace("'","$")
                mecanique_desc.append(mecs["description"])


        #Partie pour le parse
        id_boss = lien[lien.index('-') +1 : lien.index('_')]
        boss = Boss.instances[raccourcis_nom].nom_francais
        
        logger.debug(f"Création du DF GLOBAL pour {boss}")
        
        if log_boss["cm"]:
            boss += " CM"
        print(data['targets'][0]['hpLeft'])
        #Définition du df_stats_global
        df_global = {'ID':[id_boss],
                  'Time Start':[-1],
                  'Time End':[-1],
                  'Boss':[boss],
                  'Success': [data["success"]],
                  'Total Boss Health':[-1],
                  'Final Boss Health':[-1],
                  'Boss Health Burned %':[data['targets'][0]['hpLeft']],
                  'Duration': [data["encounterDuration"].split('s')[0]]}
        df_global = pd.DataFrame(df_global)

        #Définition du df_Stats_DPS
        wepSet2_2,wepSet2_1,wepSet1_2,wepSet1_1,dps_target_condi,dps_target_power,dmg_target_condi,dmg_target_power,dps_total_condi,dps_total_power,role,dps_total,dps_target,dmg_target,sous_groupe,profession,account,name,dmg_total,dmg_total_power,dmg_total_condi,times_downed,time_die,percent_alive,l_id_boss = [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]

        for i in range(len(data["players"])):
            l_id_boss.append(id_boss)
            sous_groupe.append(data["players"][i]['group'])
            profession.append(data["players"][i]["profession"])
            account.append(data["players"][i]["acc"])
            name.append(data["players"][i]["name"])


            dmg_total.append(data["phases"][0]["dpsStats"][i][0])
            dmg_total_power.append(data["phases"][0]["dpsStats"][i][1])
            dmg_total_condi.append(data["phases"][0]["dpsStats"][i][2])

            dps_total.append(data["phases"][0]["dpsStats"][i][0] / data["phases"][0]["end"])
            dps_total_power.append(data["phases"][0]["dpsStats"][i][1] / data["phases"][0]["end"])
            dps_total_condi.append(data["phases"][0]["dpsStats"][i][2] / data["phases"][0]["end"])


            dmg_target.append(data["phases"][0]["dpsStatsTargets"][i][0][0])
            dmg_target_power.append(data["phases"][0]["dpsStatsTargets"][i][0][1])
            dmg_target_condi.append(data["phases"][0]["dpsStatsTargets"][i][0][2])

            dps_target.append(data["phases"][0]["dpsStatsTargets"][i][0][0] / data["phases"][0]["end"])
            dps_target_power.append(data["phases"][0]["dpsStatsTargets"][i][0][1] / data["phases"][0]["end"])
            dps_target_condi.append(data["phases"][0]["dpsStatsTargets"][i][0][2] / data["phases"][0]["end"])


            times_downed.append(data["phases"][0]["defStats"][i][-5])
            time_die.append(data["phases"][0]["defStats"][i][-3])
            percent_alive.append(data["phases"][0]["defStats"][i][-2])
            
            role_j = ""
            if data["players"][i]["tough"] == 10:
                role_j += ("Toughness:10")
            if data["players"][i]["heal"] == 10:
                role_j += ("Healing:10")
            if data["players"][i]["condi"] == 10:
                role_j += ("Condi:10")
            if data["players"][i]["conc"] == 10:
                role_j += ("Concentration:10")
            if role_j == "":
                role_j += "-1"
            role.append(role_j)
            wepSet1_1.append(1)
            wepSet1_2.append(1)
            wepSet2_1.append(1)
            wepSet2_2.append(1)

        df_dps = {'ID':l_id_boss,
                  'Sub Group':sous_groupe,
                  'Profession':profession,
                  'Role':role,
                  'Name': name,
                  'Account':account,
                  'WepSet1_1':wepSet1_1,
                  'WepSet1_2':wepSet1_2,
                  'WepSet2_1':wepSet2_1,
                  'WepSet2_2':wepSet2_2,
                  'Boss DPS':dps_target,
                  'Boss DMG':dmg_target,
                  'Boss Power DPS':dmg_target_power,
                  'Boss Power DMG':dmg_target_power,
                  'Boss Condi DPS':dps_target_condi,
                  'Boss Condi DMG':dmg_target_condi,
                  'All DPS':dps_total,
                  'All DMG':dmg_total,
                  'All Power DPS':dps_total_power,
                  'All Power DMG':dmg_total_power,
                  'All Condi DPS':dps_total_condi,
                  'All Condi DMG':dmg_total_condi,
                  'Times Downed':times_downed,
                  'Time Died':time_die,
                  'Percent Alive':percent_alive}
        df_dps = pd.DataFrame(df_dps)

        #Les ID correpondant aux boons
        dico_id_boons = {740 :0,
                725: 1,
                1187: 2,
                30328: 3,
                717: 4,
                718: 5,
                726: 6,
                743: 7,
                1122: 8,
                719: 9,
                26980: 10,
                873: 11}
        ordre_boon = data["boons"]

        #Définition du df_gen_group
        l_id_boss= []
        liste_buff = [[[0] * len(data["players"]), [0] * len(data["players"])] for _ in range(12)]

        liste_boon_squad = data["phases"][0]["buffsStatContainer"]["boonGenGroupStats"]

        #Boucle pour chaque joueur présent dans la squad
        for i in range(len(data["players"])):

            l_id_boss.append(id_boss)
            
            #Pour chaque boon présent dans la liste "data" (12)
            for e in range(len(liste_boon_squad[i]["data"])):

                #Récupère le boon en fonction de e
                valeur_du_boon = liste_boon_squad[i]["data"][e] #=> [Nombre généré, ???, Wasted, ???, ???, Extended]

                #Si il n'est pas vide
                if not valeur_du_boon == []:

                    boon_gen = valeur_du_boon[0]
                    boon_wasted = valeur_du_boon[3]
                    id_boon = dico_id_boons[ordre_boon[e]]
                    
                    #Ajoute le nombre de boon_gen
                    if boon_gen == 0:
                        liste_buff[id_boon][0][i] = boon_gen
                    else:
                        liste_buff[id_boon][0][i] = str(boon_gen) + "%"
                    
                    #Ajoute le nombre de boon_wasted
                    if boon_wasted == 0:
                        liste_buff[id_boon][1][i] = boon_wasted
                    else:
                        liste_buff[id_boon][1][i] = str(boon_wasted) + "%"
                else:
                    liste_buff[id_boon][i] = 0
        
        df_gen_group = {'ID': l_id_boss,
                        'Name': name,
                        'Might':liste_buff[0][0],
                        'Might Overstack': liste_buff[0][1],
                        'Fury': liste_buff[1][0],
                        'Fury Overstack': liste_buff[1][1],
                        'Quickness': liste_buff[2][0],
                        'Quickness Overstack': liste_buff[2][1],
                        'Alacrity': liste_buff[3][0],
                        'Alacrity Overstack': liste_buff[3][1],
                        'Protection': liste_buff[4][0],
                        'Protection Overstack': liste_buff[4][1],
                        'Regeneration': liste_buff[5][0],
                        'Regeneration Overstack': liste_buff[5][1],
                        'Vigor': liste_buff[6][0],
                        'Vigor Overstack': liste_buff[6][1],
                        'Aegis': liste_buff[7][0],
                        'Aegis Overstack': liste_buff[7][1],
                        'Stability': liste_buff[8][0],
                        'Stability Overstack': liste_buff[8][1],
                        'Swiftness': liste_buff[9][0],
                        'Swiftness Overstack': liste_buff[9][1],
                        'Resistance': liste_buff[10][0],
                        'Resistance Overstack': liste_buff[10][1],
                        'Resolution': liste_buff[11][0],
                        'Resolution Overstack': liste_buff[11][1],}
        df_gen_group = pd.DataFrame(df_gen_group)
        
        
        #Définition du df_boon_uptime
        avg_boons= []
        liste_buff = [[0] * len(data["players"]) for _ in range(12)]
        l_id_boss = [id_boss for _ in range(len(data["players"]))]

        liste_boon_uptime = data["phases"][0]["buffsStatContainer"]["boonStats"]

        for i in range(len(data["players"])):
            avg_boons.append(liste_boon_uptime[i]["avg"])

            for e in range(len(liste_boon_uptime[i]["data"])):
                valeur_du_boon = liste_boon_uptime[i]["data"][e]
                if valeur_du_boon != []:
                    liste_buff[dico_id_boons[ordre_boon[e]]][i] = valeur_du_boon[0]
                else:
                    liste_buff[dico_id_boons[ordre_boon[e]]][i] = 0
                    

        df_uptime = {'ID': l_id_boss,
                        'Name': name,
                        'Avg Boons': avg_boons,
                        'Might':liste_buff[0],
                        'Fury': liste_buff[1],
                        'Quickness': liste_buff[2],
                        'Alacrity': liste_buff[3],
                        'Protection': liste_buff[4],
                        'Regeneration': liste_buff[5],
                        'Vigor': liste_buff[6],
                        'Aegis': liste_buff[7],
                        'Stability': liste_buff[8],
                        'Swiftness': liste_buff[9],
                        'Resistance': liste_buff[10],
                        'Resolution': liste_buff[11]}
        df_uptime = pd.DataFrame(df_uptime)

        #Définition du df_mecanique
        df_mecanique = {
                        'ID': [],
                        'Name': []
                        }
        
        print("df_mecanique")
        print("nbr joueurs: ",len(data["players"]))
        
        for i in range(len(data["players"])):
            df_mecanique['ID'].append(id_boss)
            df_mecanique["Name"].append(data["players"][i]["name"])
            
            print(data["players"][i]["name"])
            
            for num_mec, mecs in enumerate(mecanique_desc):
                if mecs not in df_mecanique:
                    df_mecanique[mecs] = []
                df_mecanique[mecs].append(int(data["phases"][0]["mechanicStats"][i][num_mec][0]))
                print(data["phases"][0]["mechanicStats"][i][num_mec][0])

        df_mecanique = pd.DataFrame(df_mecanique)
        df_mecanique.fillna("0", inplace=True)   
        
        
        #Fonction pour ajouter le boss dans les fichiers log_boss_df
        ajout_boss(raccourcis_nom, df_global, df_dps, df_gen_group, df_uptime, df_mecanique)

        return data

#Ajoute un lien au df du boss en question.
def ajout_lien_au_df(lien : str):
    """
    Traite le lien est l'ajouté à la base de donnée du boss.
    
    ### Paramètre:
     - Lien (str): Lien dps.report du boss
    """
    logger.debug(f"Début de ajout_lien")
    #Extrait la date du lien
    date_essais = (lien.split('-')[1] + '-' + lien.split('-')[2]).split('_')[0]

    #Extrait le raccourcis_boss du lien
    raccourcis_boss = lien.split('_')[1]
    #Test si le raccourcis_boss est bien une instance de l'objet Boss()
    if raccourcis_boss in Boss.instances:
        instance = Boss.instances[raccourcis_boss]
        instance: Type[Boss]
    else:
        logger.error(f"Instance du boss : {raccourcis_boss} non trouvé ! ! !")
        return -1
    
    nom_fr = instance.nom_francais
    nom_en = instance.nom_anglais

    #Test si le boss n'est pas déjà présent dans l'instance
    logger.debug(f"Vérification si le boss : {raccourcis_boss} de la date : {date_essais} existe . . .")
    combat_present = instance.recherche_combat_existe_dans_Boss(date_essais)

    if combat_present == False:
        logger.info("Boss non trouvé, début de traiterlogs()")
        traiterLogs( lien )
        logger.info(f"Actualisation de l'instance {raccourcis_boss}")
        aile = Boss.instances[raccourcis_boss].aile
        Boss(nom_fr, nom_en, raccourcis_boss, aile) #Recrée l'instance du boss

    elif combat_present == True:
        logger.info(f"Boss trouvé dans l'instance : {raccourcis_boss}")
    else:
        logger.error("Erreur, fonction ajout_lien_au_df() non executé ! ! !")

#Definition des boss présent dans le jeu
def init_instances_boss():
    for aile in INFO_RAID.values():
        for boss in aile.values():
            Boss(boss['nom_francais'], boss['nom_anglais'], boss['raccourcis'], boss['aile'])
    

    Boss('Mai trin','Mai trin','trin','strike')
    Boss('Ankka','Ankka','ankka','strike')

    logger.info(f"Nombre d'instance de Boss crée: {Boss.nbr_boss}")


