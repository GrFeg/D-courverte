import csv
import discord
import fonction
from fonction import log
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json
from discord.ui import Button, View
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from PIL import Image

pointeur_lien_log = 0
CHEMIN_RACINE = os.path.dirname(__file__)  

class Joueur:

    """
    Class qui définit touts les joueurs de raids des InAe !
    """
    nombre_joueurs = 0
    instances = {}

    def __init__(self, pseudo, nom_de_compte, id_discord = 0):
        
        #Définition des variables du JOUEUR
        self.pseudo = pseudo
        self.nom_de_compte = nom_de_compte
        self.nom_de_compte_log = ":" + nom_de_compte
        self.id_discord = id_discord

        #Partie utile pour la commande statistique
        self.nbr_mort = -1
        self.nbr_terre = -1
        self.nbr_mecanique = -1
        self.calin = -1

        Joueur.nombre_joueurs += 1
        Joueur.instances[self.pseudo] = self

    
    def raid(self, csv_raid):
        '''
        Fonction utilisé dans la commande Statistique
        '''
        #Pour chaque ligne du CSV
        for ligne in csv_raid:
            #Test si la ligne possède le nom d'un joueur de la guilde
            if self.nom_de_compte in ligne:
                #Recupère les informations utile
                if "All" in ligne:
                    self.nbr_mort = ligne[7]
                    self.nbr_terre = ligne[6]
                    self.nbr_mecanique = ligne[5]
                
                if "was snatched" in ligne:
                    self.calin = ligne[5]

        #Test si le joueur a été trouvé. Renvoit True, sinon Renvoit False et met toutes les valeurs à -1.
        if self.nbr_mort != -1:
            return True
        else:
            self.nbr_mort = -1
            self.nbr_terre = -1
            self.nbr_mecanique = -1
            self.calin = -1
            return False
    
    def liste_joueurs(cls):
        return list(Joueur.instances.keys()), list(Joueur.instances.values())

    liste_joueurs = classmethod(liste_joueurs)

class Boss:
    '''
    Class qui définit tout les boss présent dans le jeu, leurs noms (anglais et français).
    Stocke tout les Data Frame du boss

    Fonction recherche_combat_dans_Boss: Test si l'ID est dans le df_global -> Renvoit true ou false
    '''

    instances = {}
    nbr_boss = 0
    
    def __init__(self, nom_francais: str, nom_anglais: str, raccourcis_nom: str):

        self.nom_francais = nom_francais
        self.nom_anglais = nom_anglais
        self.raccourcis_nom = raccourcis_nom
        self.nbr_combat = 0

        dico_df = lire_boss(raccourcis_nom)

        #Test si chaque df existe bien dans le dict et le charge.
        if type(dico_df) == dict:
            if 'Stats_global' in dico_df:
                self.df_global = dico_df['Stats_global']
            else:
                log(f'{raccourcis_nom}: Stats_global non trouvé, erreur ! ', 2)
            
            if 'Stats_DPS' in dico_df:
                self.df_dps = dico_df['Stats_DPS']
            else:
                log(f'{raccourcis_nom}: Stats_DPS non trouvé, erreur ! ', 2)

            if 'Boons_gen_group' in dico_df:
                self.df_gen_group = dico_df['Boons_gen_group']
            else:
                log(f'{raccourcis_nom}: Boons_gen_group non trouvé, erreur ! ', 2)

            if 'Boons_uptime' in dico_df:
                self.df_boon_uptime = dico_df['Boons_uptime']
            else:
                log(f'{raccourcis_nom}: df_boon_uptime non trouvé, erreur ! ', 2)

            if 'mecanique' in dico_df:
                self.df_mecanique = dico_df['mecanique']
            else:
                log(f'{raccourcis_nom}: mecanique non trouvé, erreur ! ', 2)
        else:
            log(f"L'instance de {raccourcis_nom} n'a pas pu charger les df",2)

        Boss.instances[self.raccourcis_nom] = self
        Boss.nbr_boss += 1
    
    #Fonction pour savoir si un combat existe dans l'instance du boss ou non, return True or False
    def recherche_combat_dans_Boss(self, date_essais):
        log(f"Recherche de {date_essais} dans {self.df_global['ID'].values}, {date_essais in self.df_global['ID'].values}",0)

        if  date_essais in self.df_global['ID'].values:
            return True
        else:
            return False

class Combat:
    """
    Class qui définit touts les Combat de raids que les InAe ont fait !
    """
    instances = {}

    def __init__(self, date: datetime, raccourcis_nom, duree: int, succes: bool, cm: bool, pourcentage: float, log, nom_joueur, nom_mecanique, 
                 mecanique, lien: str):
        
        nom_donnee = ['date',"racourcis_nom", 'duree','succes','cm','pourcentage','mecanique_nom','nom_joueurs','mecaniques','lien'] 

        self.boss = Boss.instances[raccourcis_nom].raccourcis_nom
        self.date = date
        self.duree = duree #Durée en secondes
        self.temps = str(int(self.duree) // 60) + "m " + str(int(self.duree) % 60) + "s" #Affichage sympathique pour la durée
        self.succes = succes
        self.cm = cm
        self.pourcentage = pourcentage
        self.nom_joueur = nom_joueur
        self.stats = log
        self.nom_mecanique = nom_mecanique
        self.mecanique = mecanique
        self.lien = lien

        Boss.instances[raccourcis_nom].nbr_combat += 1
        Combat.instances[raccourcis_nom + "_" + str(datetime.strftime(date, '%Y%m%d-%H%M%S'))] = self

#Fonction pour lire tout les csv d'un boss est les stocker
def lire_boss(boss):
    '''
    Fonction pour lire les et enregistrer les csv d'un boss.
    '''
    #Recupère tout les fichiers d'un dossier 
    chemin_dossier = os.path.join(CHEMIN_RACINE, 'log_boss_df', boss)

    if os.path.isdir(chemin_dossier):
        fichiers = os.listdir(chemin_dossier)
    else:
        log(f"Le dossier {chemin_dossier} n'éxiste pas !", 2)
        return -1

    dico_df = {}
    #Lis chaque fichier dans le fichier Boss.
    for fichier in fichiers:
        nom = fichier.split('.')[0]
        dico_df[nom] = pd.read_csv(chemin_dossier + '\\' + fichier)

    if len(dico_df) != 11:
        log(f"Fichier dans {boss} manquant, risque d'erreur probable.",2)
    return dico_df

def ajout_boss(raccourcis_nom, df_global, df_dps, df_gen_group, df_uptime, df_mecanique):

    chemin = '\\log_boss_df\\' + raccourcis_nom
    l_chemin = ['\\Stats_global.csv', '\\Stats_DPS.csv', '\\Boons_gen_group.csv', '\\Boons_uptime.csv', '\\mecanique.csv']
    nom_df = ['df_global', 'df_dps', 'df_gen_group', 'df_boon_uptime' 'df_mecanique']
    l_df = [df_global, df_dps, df_gen_group, df_uptime, df_mecanique]
    compteur = 0
    #Pour chaque df, met a jour le bon fichier
    for df in l_df:
        #Regarde si le fichier existe
        if os.path.isfile(CHEMIN_RACINE + chemin + l_chemin[compteur]):
            df_fichier = pd.read_csv(CHEMIN_RACINE + chemin + l_chemin[compteur], index_col=None)
        else:
            log(f"Le fichier {l_chemin[compteur]} n'existe pas ! !",2)
            return -1
            
        id_boss = df['ID'].iloc[0]
        if str(id_boss) in df_fichier['ID'].values:
            log(f'Fonction ajout_boss: Combat ID: {id_boss} pour le fichier {l_chemin[compteur]} existe déjà',0)
            compteur += 1
            continue
            

        df_fichier = pd.concat([df_fichier, df], ignore_index=True)

        df_fichier.to_csv(chemin + l_chemin[compteur], index= False)
        setattr(Boss.instances[raccourcis_nom], nom_df[compteur], df_fichier)
        compteur += 1

    

    return True

#Scrap d'un site, prend le liens en entrée
def scrap(lien: str):
    requete = requests.get(lien)
    page = requete.content
    soup = BeautifulSoup(page, features="html.parser")
    log("Log de raid mis en soup")
    return soup

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
        log("Scrappage du site",0)
        soup = scrap(lien)
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
        boss = Boss.instances[raccourcis_nom].nom_anglais
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


        boons = {740 :0,
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

        for i in range(len(data["players"])):
            l_id_boss.append(id_boss)

            for e in range(len(data["phases"][0]["boonGenGroupStats"][i]["data"])):
                valeur_du_boon = data["phases"][0]["boonGenGroupStats"][i]["data"][e]
                if valeur_du_boon != []:
                    if valeur_du_boon[0] == 0:
                        liste_buff[boons[ordre_boon[e]]][0][i] = valeur_du_boon[0]
                    else:
                        liste_buff[boons[ordre_boon[e]]][0][i] = str(valeur_du_boon[0]) + "%"
                    
                    if valeur_du_boon[3] == 0:
                        liste_buff[boons[ordre_boon[e]]][1][i] = valeur_du_boon[3]
                    else:
                        liste_buff[boons[ordre_boon[e]]][1][i] = str(valeur_du_boon[3]) + "%"
                else:
                    liste_buff[boons[ordre_boon[e]]][i] = 0
        
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

        for i in range(len(data["players"])):
            avg_boons.append(data["phases"][0]["boonStats"][i]["avg"])

            for e in range(len(data["phases"][0]["boonStats"][i]["data"])):
                valeur_du_boon = data["phases"][0]["boonStats"][i]["data"][e]
                if valeur_du_boon != []:
                    liste_buff[boons[ordre_boon[e]]][i] = valeur_du_boon[0]
                else:
                    liste_buff[boons[ordre_boon[e]]][i] = 0
                    

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
        df_mecanique = {}
        for i in range(len(data["players"])):
            df_mecanique['ID'] = id_boss
            df_mecanique["Name"] = data["players"][i]["name"]
            for mecs in mecanique_desc:
                df_mecanique[mecs] = data["phases"][0]["mechanicStats"][i][0]

        df_mecanique = pd.DataFrame(df_mecanique)
        df_mecanique.fillna(0, inplace=True)   
        
        #Fonction pour ajouter le boss dans les fichiers log_boss_df
        ajout_boss(raccourcis_nom, df_global, df_dps, df_gen_group, df_uptime, df_mecanique)

        return data

#Definition des boss présent dans le jeu
if 1:
    vg = Boss('Gardien de la Valée', 'Vale Guardian', 'vg')
    gors = Boss('Gorseval', 'Gorseval the Multifarious', 'gors')
    sab = Boss('Sabetha', 'Sabetha the Saboteur', 'sab')
    sloth = Boss('Paressor', 'Slothasor','sloth')
    trio = Boss('Trio','Bandit Trio','trio')
    matt = Boss('Mathias','Matthias Gabrel','matt')
    esc = Boss('escort','escort','esc')
    kc = Boss('kc','kc','kc')
    tc = Boss('Chateau corompu','Twistel castle','tc')
    xera = Boss('xera','xera','xera')
    cairn = Boss('Cairn', 'Cairn the Indomitable', 'cairn')
    mo = Boss('Mursaat', 'Mursaat','mo')
    sam = Boss('Samarog','Samarog','sam')
    dei = Boss('Deimos','Deimos','dei')
    sh = Boss('Desmina','Soulless Horror','sh')
    dhuum = Boss('Dhuum','Dhuum','dhuum')
    adina = Boss('Adina','Adina','adina')
    sabir = Boss('Sabir','Sabir','sabir')
    qpeer = Boss('Qadim 2','Qadim the Peerless','qpeer')
    ca = Boss('CA','CA','ca')
    twins = Boss('Jumeaux Largos', 'Twins Largos', 'twins')
    qadim = Boss('Qadim', 'Qadim', 'qadim')

    trin = Boss('Mai trin','Mai trin','trin')
    ankka = Boss('Ankka','Ankka','ankka')

    log(f"Les objets Boss sont bien crées, nombre crée: {Boss.nbr_boss}", 1)

#Joueur de la guilde
if 1:
    cloud = Joueur("Cloud","Cloudlloyd.9240")
    tenro = Joueur("Tenro",'Tenro.8107')
    elnabo = Joueur('Elnabo','Elnabo.2014', 281853299886653441)
    drakh = Joueur('Drakh','Drakh.7321')
    pizza = Joueur('PizzaBleu',"PizzaBleu.7615", 259605122240348160)
    nils = Joueur('Nils','Nils.7289')
    blade = Joueur('BladeLarkin','bladelarkin.5790')
    gon = Joueur('Gon','BigBang.9125')
    yoda = Joueur('Yoda','Mini maitreyoda.7849')
    elias = Joueur('Ellias','Spongex.7864')
    lux = Joueur('Luxx','LuXx.9354')
    damien = Joueur('Damien','Escrimeur.4192')
    nachryma = Joueur('Nachryma','ZancrowFT.7319')
    aniteck = Joueur('Aniteck','Aniteck.6124')
    clement = Joueur('Clement','The Mangoose.7643')
    isma = Joueur('Isma','Ismael.1427')

    log(f"Les objets joueurs sont bien crées, nombre crée: {Joueur.nombre_joueurs}", 1)

#Test
traiterLogs('https://dps.report/eZsa-20240506-213434_sab')


#Fonction qui va s'occuper de tout les raid parse par le logiciel.
def init_log():

    #Recupère tout les fichiers d'un dossier 
    chemin_dossier = os.path.join(CHEMIN_RACINE, 'log_dps')

    if os.path.isdir(chemin_dossier):
        fichiers = os.listdir(chemin_dossier)
    else:
        log(f"Le dossier {chemin_dossier} n'éxiste pas !", 2)
        return -1


    compteur = 0
    #Pour chaque fichier dans fichiers
    for fichier in fichiers:
        #creer le chemin complet avec le nom du fichier
        chemin_complet = os.path.join(chemin_dossier, fichier)

        #Si le fichier existe
        if os.path.isfile(chemin_complet):
            #Si c'est un csv
            if fichier.endswith('.csv'):
                #print(f"Ouverture du fichier {fichier}")
                data = []
                #Stock le fichier dans data
                with open(chemin_complet, mode='r', encoding='ISO-8859-1') as file:
                    reader = csv.reader(file)
                    
                    for row in reader:
                        data.append(row)
                #print(len(data))

                #Split data en différent df pour chaque saut de ligne detecté.
                tableau = []
                df_tableau = []
                
                #Partie Stats_global
                stats_global = data[4:6] + data[10:16]
                stats_global[0][1] = stats_global[0][1][:-8]
                stats_global[1][1] = stats_global[1][1][:-8]
                stats_global[7][1] = stats_global[7][1][:stats_global[7][1].index('s') +1]
                stats_global.insert(0, ['ID', fichier.split('_')[0]])
                #print(stats_global[7][1])

                dico_stats_global = {}
                for i in stats_global:
                    dico_stats_global[i[0]] = i[1]

                df_tableau.append(pd.DataFrame([dico_stats_global]))


                for i, ligne in enumerate(data):
                    if i > 15 and i < 396:
                        #print(str(i), ": ", ligne)
                        if ligne == []:
                            if tableau == []:
                                tableau = []

                            else:
                                normalized_data = [row + [0]*(len(tableau[0])+1 - len(row)) for row in tableau]

                                for index, sous_liste in enumerate(normalized_data):
                                    if index == 0:
                                        normalized_data[0].insert(0, 'ID')
                                    else:
                                        normalized_data[index].insert(0, fichier.split('_')[0])

                                df_tableau.append(pd.DataFrame(normalized_data[1:], columns=normalized_data[0]))
                                df_tableau[-1].replace([None, ""], pd.NA, inplace=True)
                                df_tableau[-1].fillna('-1', inplace=True)  # Utilisez une chaîne au lieu d'un entier
                                df_tableau[-1] = df_tableau[-1].infer_objects()

                                for e in df_tableau[-1].columns:
                                    try:
                                        df_tableau[-1][e] = df_tableau[-1][e].astype(int)
                                    except:
                                        1
                                #Supprime la ligne que je rajoute à la fin suite a la manière dont est écris le csv
                                del df_tableau[-1][0]
                                tableau = []
                                #display(df_tableau[-1])
                                
                        else:
                            tableau.append(ligne)

                
                #Récuperer les données qui m'intérèsse
                del df_tableau[11:21]
                dico_tableau = {"Stats_global"    :   df_tableau[0],
                                "Stats_DPS"       :   df_tableau[1],
                                "Critique_cible"  :   df_tableau[2],
                                "Stats_defensive" :   df_tableau[4],
                                "Stats_support"   :   df_tableau[5],
                                "Boons_uptime"    :   df_tableau[6],
                                "Boons_gen_group" :   df_tableau[8],
                                "mecanique"       :   df_tableau[11],
                                "meccanique_temps":   df_tableau[12],
                                "Boss_condi"      :   df_tableau[13],
                                "Escouade_condi"  :   df_tableau[14]}

                for key, value in dico_tableau.items():
                    date = fichier.split('_')[0]
                    boss = fichier.split('_')[1]

                    if boss == 'twinlargos':
                        boss = 'twins'
                    
                    if boss == 'prlqadim':
                        boss = 'qpeer'


                    chemin = '\\log_boss_df\\' + boss + "\\" +  key + ".csv"

                    try:
                        df = pd.read_csv(chemin, index_col=False)
                        if key == 'Stats_global':
                            if df['Time Start'].isin([value['Time Start'].iloc[0]]).any():
                                break


                        cols = df.columns  # Utilisez les colonnes du premier DataFrame comme référence ou définissez manuellement
                        value = value.reindex(columns=cols)
                        df = pd.concat([df, value], ignore_index=True)
                        print(f'\rProgression: avant {len(df.columns)} après {len(value.columns)}', end='')
                        df.to_csv(chemin, index = False)
                    except:
                        
                        value.to_csv(chemin, index = False)

                compteur += 1 
                
                os.remove(chemin_complet)
    return

#Fonction pour afficher un graphique des rôles
def joli_graphique(df):

    # Colonnes numériques à utiliser pour le graphique
    cols = ['Condi', 'Soigneur', 'Tank', 'Power', 'Quick', 'Alac']

    # Normaliser les données pour chaque colonne (entre 0 et 1)
    #data_norm = (df[cols] - df[cols].min()) / (df[cols].max() - df[cols].min())
    df2 = df[cols]
    # Séparer les données par cluster
    data_by_cluster = [df2[df['Boss'] == c] for c in df['Boss'].unique()]
    nom_cluster = [df['Boss'][df['Boss'] == c].iloc[0] for c in df['Boss'].unique()]

    # Définir les étiquettes pour les axes
    categories = cols
    N = len(categories)

    # Initialiser le graphique
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    # Tracer un graphique en toile d'araignée par cluster
    plt.figure(figsize=(10, 6))
    for i, cluster in enumerate(data_by_cluster):
        values = cluster.values.mean(axis=0)
        values = np.concatenate((values, [values[0]]))
        labels = [f"{nom_cluster[i]}"] * (N + 1)
        plt.polar(angles, values, label=labels[0])

    # Ajuster les éléments du graphique
    plt.xticks(angles[:-1], categories)
    plt.ylim(0, 1)
    plt.legend(bbox_to_anchor=(0.90, 1), loc=2, borderaxespad=0.)
    plt.savefig('mon_graphique.png')
    
    # Ouvrir une image existante
    image = Image.open(CHEMIN_RACINE + '\\mon_graphique.png')

    # Définir la zone de rognage (left, top, right, bottom)
    # Par exemple, pour rogner l'image de sorte à enlever 100 pixels de chaque côté
    left = 200
    top = 0
    right = image.width - 100
    bottom = image.height - 0
    cropped_image = image.crop((left, top, right, bottom))

    # Sauvegarder l'image rognée
    cropped_image.save(CHEMIN_RACINE + '\\mon_graphique.png')

    # Attachez l'image locale en utilisant un File et ajoutez-la à l'embed
    file = discord.File(CHEMIN_RACINE + "\\mon_graphique.png", filename="mon_graphique.png")

    return file    

#Fonction pour récuperer et traiter les donnée des rôles pour un boss et un joueur en particulier
def quel_role_sur_quel_boss(boss, nom_de_compte):
    '''
    Fonction pour savoir quels proportion des rôles le joueur a t-il fait sur un boss en question.
    Affiche le graphique grace a la fonction joli_graphique
    '''

    #Recupère les df du boss
    dico_df = lire_boss(boss)

    #Cherche si le dico est non nul (pas d'erreur dans lire_boss())
    if dico_df == -1:
        log(f"Dico_df inexploitable pour {boss}, fin de la fonction quel_role_sur_quel_boss", 2)
        return -1, -1

    #Cherche si le df Stats_global existe, l'isole, sinon return -1
    if 'Stats_global' in dico_df:
        df_stats_global = dico_df['Stats_global'][['ID','Boss']]
    else:
        log(f"DataFrame 'Stats_global' introuvable", 2)
        return -1, -1

    #Cherche si le df Stats_DPS existe, l'isole, sinon return -1
    if 'Stats_DPS' in dico_df:
        df_stats_dps =  dico_df['Stats_DPS'][['ID','Role','Account','Name']]
    else:
        log(f"DataFrame 'Stats_DPS' introuvable", 2)
        return -1, -1

    #Cherche si le df Boons_gen_group existe, l'isole, sinon return -1
    if 'Boons_gen_group' in dico_df:
        df_boon_gen_gorup =  dico_df['Boons_gen_group'][['ID','Name','Quickness','Alacrity']]
    else:
        log(f"DataFrame 'Boons_gen_group' introuvable", 2)
        return -1, -1

    #Garde uniquement le joueur voulus
    df_stats_dps = df_stats_dps[df_stats_dps['Account'] == nom_de_compte]
    df_boon_gen_gorup = df_boon_gen_gorup[df_boon_gen_gorup['Name'].isin(df_stats_dps['Name'])]

    #Merge les df pour un df_global
    df = pd.merge(df_stats_dps, df_stats_global, on = 'ID', how = 'left')
    df = pd.merge(df, df_boon_gen_gorup, on = 'ID', how = 'left')

    #Pour chaque ligne du df, regarde le rôle que la personne faisait.
    for indexe, ligne in df.iterrows():
        #Tank
        if ligne['Role'] == " Concentration:10 Healing:10 Toughness:10":
            df.loc[indexe, ['Role']] = ['Toughness:10']
        #DPS
        if ligne['Role'] == "Condi:10" or ligne['Role'] == "-1":
            #ALAC
            if ligne['Alacrity'] != '0':
                gen_alac = float(ligne['Alacrity'][:-1])
                print(gen_alac)
                if gen_alac > 20:
                    df.loc[indexe, ['Role']] = ["Quick"]
                    print(df.loc[indexe, ['Role']])
            #QUICK
            if ligne['Quickness'] != '0':
                gen_quick = float(ligne['Quickness'][:-1])
                print(gen_quick)
                if gen_quick > 20:
                    df.loc[indexe, ['Role']] = ["Alac"]
                    print(df.loc[indexe, ['Role']])

    #Split les différents rôle et considère les case vide comme étant Power
    df2 = df['Role'].str.get_dummies(sep=' ')
    df2 = df2.rename(columns = {'-1': "Power"})
    df_final = pd.concat([df, df2], axis=1)

    #Si une colonne n'existe pas, la créee
    liste_nom_colonne = ['Condi:10', 'Healing:10', 'Toughness:10','Power','Quick', 'Alac']
    for nom_colonnes in liste_nom_colonne:
        if nom_colonnes not in df_final.columns:
            df_final[nom_colonnes] = 0
    
    #Renomme les noms des colonnes pour une VF
    df_final.rename(columns={'Condi:10': 'Condi', 'Healing:10': 'Soigneur', 'Toughness:10': 'Tank'}, inplace=True)

    #Afficher le graphique et renvoit le nombre de try
    return joli_graphique(df_final), df_final.shape[0]
    

init_log()

#Recupère la date de modification de log.csv pour s'en référer comme la date. Unitilisé.

url_raid = 'csv/log.csv'
timestamp = os.path.getmtime(CHEMIN_RACINE + '/' + url_raid)
date_modification = datetime.fromtimestamp(timestamp).strftime('%Y%m%d')



#Fonction pour afficher les mécaniques
def affichage_mecs(raccourcis_nom: str, log_boss: dict):
    '''
    Fontion qui définit l'affichage des méccaniques en fonction du boss
    Traite log_boss qui est la version brut avec toutes les information du boss en question pour n'en garder que les méccaniques utiles.
    Traduis les mécaniques en Français.
    En déduit les rôles spécifiques au boss jouait pas les joueurs seulement pour la partie méccaniques.
    '''

    #Affichage mécaniques de W1 B1:
    if raccourcis_nom == 'vg':
        compteur = 0 
        stats = []
        for joueur in list(Joueur.instances.values()):
            nom_f = joueur.nom_de_compte.strip(':')
            if nom_f in log_boss: 
                index = log_boss['nom_joueurs'].index(nom_f)
                joueur = log_boss[nom_f]
                mecanique_nom = log_boss['mecanique_nom'].copy()
                mecanique = log_boss['mecaniques'][index].copy()

                #Suppression des mécaniques inutiles
                meca_a_drop = ['Green Team', 'Blue Attuned', 'Red Attuned', 'Green Attuned']
                for meca in meca_a_drop:
                    if meca in mecanique_nom:
                        place = mecanique_nom.index(meca)
                        del mecanique_nom[place]
                        del mecanique[place]
                
                #Regroupement des mécaniques:
                if 'Green Guard TP' in mecanique_nom: 
                    if 'Boss TP' in mecanique_nom:
                        num1 = mecanique_nom.index('Green Guard TP')
                        num2 = mecanique_nom.index('Boss TP')
                        mecanique_nom[num1] = 'Zone Bleu'
                        mecanique[num1][0] = mecanique[num1][0] + mecanique[num2][0]
                        del mecanique[num2]
                        del mecanique_nom[num2]

                if 'Floor dmg' in mecanique_nom:
                    total = 0
                    indexo = []
                    for indexe, element in enumerate(mecanique_nom):
                        if element == 'Floor dmg':
                            indexo.append(indexe)
                            total += mecanique[indexe][0]

                    for indexe in range(len(indexo)- 1, -1, -1):
                        del mecanique[indexo[indexe]]
                        del mecanique_nom[indexo[indexe]]
                    mecanique_nom.append('Tick sol')        
                    mecanique.append([total,0])

                #renomage Mécanique version fr
                if 'Seeker' in mecanique_nom:
                    mecanique_nom[mecanique_nom.index('Seeker')] = 'Fureteur'        

                #Definis le stats en fonction de la liste mecanique et mecaniques_nom
                stats.append(f"ㅤ**- Rôle:** {joueur[2]} \n")
                for i in range(len(mecanique_nom)):
                    stats[compteur] += f"ㅤ**- {mecanique_nom[i]}:** {mecanique[i][0]} \n"
                compteur += 1
                            
        return stats
    
    #Affichage mécaniques de W1 B2:
    if raccourcis_nom == 'gors':
        compteur = 0 
        stats = []
        for joueur in list(Joueur.instances.values()):
            nom_f = joueur.nom_de_compte.strip(':')
            if nom_f in log_boss: 
                index = log_boss['nom_joueurs'].index(nom_f)
                joueur = log_boss[nom_f]
                mecanique_nom = log_boss['mecanique_nom'].copy()
                mecanique = log_boss['mecaniques'][index].copy()

                #Suppression des mécaniques inutiles
                meca_a_drop = ['Slam','Black Goo']
                for meca in meca_a_drop:
                    if meca in mecanique_nom:
                        place = mecanique_nom.index(meca)
                        del mecanique_nom[place]
                        del mecanique[place]

                #Renomage Mécanique version fr
                if 'Egged' in mecanique_nom:
                    mecanique_nom[mecanique_nom.index('Egged')] = 'Oeuf'
                if 'Orb Debuff' in mecanique_nom:
                    mecanique_nom[mecanique_nom.index('Orb Debuff')] = 'Debuff orbe'          

                #Definis le stats en fonction de la liste mecanique et mecaniques_nom
                stats.append(f"ㅤ**- Rôle:** {joueur[2]} \n")
                for i in range(len(mecanique_nom)):
                    stats[compteur] += f"ㅤ**- {mecanique_nom[i]}:** {mecanique[i][0]} \n"
                compteur += 1
                            
        return stats
    
    #Affichage mécaniques de W1 B3:
    if raccourcis_nom == 'sab':
        compteur = 0 
        stats = []
        for joueur in list(Joueur.instances.values()):
            nom_f = joueur.nom_de_compte.strip(':')
            if nom_f in log_boss: 
                index = log_boss['nom_joueurs'].index(nom_f)
                joueur = log_boss[nom_f]
                mecanique_nom = log_boss['mecanique_nom'].copy()
                mecanique = log_boss['mecaniques'][index].copy()

                #Suppression des mécaniques inutiles
                meca_a_drop = ['Flamethrower (Karde)','Flak Shot','Bandit Kick','Cannon Shot']
                for meca in meca_a_drop:
                    if meca in mecanique_nom:
                        place = mecanique_nom.index(meca)
                        del mecanique_nom[place]
                        del mecanique[place]

                #Renomage Mécanique version fr
                if 'Sapper Bomb' in mecanique_nom:
                    mecanique_nom[mecanique_nom.index('Sapper Bomb')] = 'Bombe verte'
                if 'Timed Bomb' in mecanique_nom:
                    mecanique_nom[mecanique_nom.index('Timed Bomb')] = 'Bombe collante'          

                #Definis le stats en fonction de la liste mecanique et mecaniques_nom
                if mecanique[mecanique_nom.index('Shell-Shocked')][0] == 0:
                    stats.append(f"ㅤ**- Rôle:** {joueur[2]} \n")
                if mecanique[mecanique_nom.index('Shell-Shocked')][0] != 0:
                    stats.append(f"ㅤ**- Rôle:** {joueur[2]} Canon \n")

                yo = mecanique_nom.index('Shell-Shocked')
                del mecanique_nom[yo]
                del mecanique[yo]

                for i in range(len(mecanique_nom)):
                    stats[compteur] += f"ㅤ**- {mecanique_nom[i]}:** {mecanique[i][0]} \n"
                compteur += 1
                            
        return stats
    
    #Affichage mécaniques de W5 B3:
    if raccourcis_nom == 'dhuum':
        compteur = 0 
        stats = []
        for joueur in list(Joueur.instances.values()):
            nom_f = joueur.nom_de_compte.strip(':')
            if nom_f in log_boss: 
                index = log_boss['nom_joueurs'].index(nom_f)
                joueur = log_boss[nom_f]
                mecanique_nom = log_boss['mecanique_nom'].copy()
                mecanique = log_boss['mecaniques'][index].copy()

                #Suppression des mécaniques inutiles
                meca_a_drop = ['Golem Dmg','Bomb dmg','Took Superspeed orb','Knockback dmg','Rending Swipe Hit','Freed from Echo']
                for meca in meca_a_drop:
                    if meca in mecanique_nom:
                        place = mecanique_nom.index(meca)
                        del mecanique_nom[place]
                        del mecanique[place]

                #Renomage Mécanique version fr
                if 'Cracks' in mecanique_nom:
                    mecanique_nom[mecanique_nom.index('Cracks')] = 'Fissure'
                if 'Bomb' in mecanique_nom:
                    mecanique_nom[mecanique_nom.index('Bomb')] = 'Bombe' 
                if 'Bomb Triggered' in mecanique_nom:
                    mecanique_nom[mecanique_nom.index('Bomb Triggered')] = 'Détonation Bombe'
                if "Enderd'As Pick up" in mecanique_nom:
                    mecanique_nom[mecanique_nom.index("Enderd'As Pick up")] = 'Câlin <3'
                if 'Dip AoE' in mecanique_nom:
                    mecanique_nom[mecanique_nom.index('Dip AoE')] = 'Mini soul-split'
                if 'Suck dmg' in mecanique_nom:
                    mecanique_nom[mecanique_nom.index('Suck dmg')] = 'Soul-split'
                          

                #Definis le stats en fonction de la liste mecanique et mecaniques_nom
                if mecanique[mecanique_nom.index('Messenger Fixation')][0] < 3:
                    stats.append(f"ㅤ**- Rôle:** {joueur[2]} ")
                if mecanique[mecanique_nom.index('Messenger Fixation' )][0] > 3:
                    stats.append(f"ㅤ**- Rôle:** {joueur[2]} Kite ")

                yo = mecanique_nom.index('Messenger Fixation')
                del mecanique_nom[yo]
                del mecanique[yo]

                #Definis le stats en fonction de la liste mecanique et mecaniques_nom
                if mecanique[mecanique_nom.index('Green port')][0] != 0:
                    stats[-1] += f"green \n"
                else:
                    stats[-1] += f"\n"

                yo = mecanique_nom.index('Green port')
                del mecanique_nom[yo]
                del mecanique[yo]

                for i in range(len(mecanique_nom)):
                    stats[compteur] += f"ㅤ**- {mecanique_nom[i]}:** {mecanique[i][0]} \n"
                compteur += 1
                            
        return stats 

    #Sinon
    if 1:
        compteur = 0 
        stats = []
        for joueur in list(Joueur.instances.values()):
            nom_f = joueur.nom_de_compte.strip(':')
            if nom_f in log_boss: 
                index = log_boss['nom_joueurs'].index(nom_f)
                joueur = log_boss[nom_f]
                mecanique_nom = log_boss['mecanique_nom']
                mecanique = log_boss['mecaniques']

                stats.append(f"ㅤ**- Rôle:** {joueur[2]} \n")
                for i in range(len(mecanique_nom)):
                    stats[compteur] += f"ㅤ**- {mecanique_nom[i]}:** {mecanique[index][i][0]} \n"
                compteur += 1
                            
        return stats

#Fonction pour afficher les statistiques global d'un combat
def affichage_stats_glo(df_global):
    #Définir les stats globals
    stats_global = (f"Durée du raid: {df_global['Duration'].iloc[0]} \n")

    #Regarde si le Boss est vaincu, définit la couleur et le message en fonction
    if df_global['Success'].iloc[0] == True:
        stats_global += f'Boss vaincu'
        couleur = discord.Colour.green()
    else:
        stats_global += f"Point de vie du Boss: {100 - int(df_global['Boss Health Burned %'].iloc[0])} %"
        couleur = discord.Colour.red()
    return stats_global, couleur

#Fonction pour afficher les statistiques global d'un joueur
def affichage_stats_glo_joueur(joueur, date_essais, raccourcis_nom: str):

    df_dps_glo = Boss.instances[raccourcis_nom].df_dps[Boss.instances[raccourcis_nom].df_dps['ID'] == date_essais]

    df_dps = df_dps_glo.copy()
    df_dps = df_dps[df_dps['Account'] == joueur.nom_de_compte]
    nom_personnage = df_dps['Name'].iloc[0]

    df_gen_group = Boss.instances[raccourcis_nom].df_gen_group[Boss.instances[raccourcis_nom].df_gen_group['ID'] == date_essais]
    df_gen_group = df_gen_group[df_gen_group['Name'] == nom_personnage]
    
    df_boon_uptime = Boss.instances[raccourcis_nom].df_boon_uptime
    df_boon_uptime = df_boon_uptime[df_boon_uptime['ID'] == date_essais]

    #Définition des variables
    nom_de_compte = joueur.nom_de_compte

    degat = str(round(df_dps['Boss DPS'].iloc[0] / 1000,2)) + "K"
    sub = df_dps['Sub Group'].iloc[0]
    gen_alac = df_gen_group['Alacrity'].iloc[0]
    gen_quick = df_gen_group['Quickness'].iloc[0]
    boon = "none"
    boon_stats = ""

    #Regarde si alac est superieur à 0, si oui enlève le % et convertit en float.
    if gen_alac != '0':
        gen_alac = float(gen_alac[:-1])
        if gen_alac > 20:
           boon = 'Alacrity' 
    if gen_quick != '0':
        gen_quick = float(gen_quick[:-1])
        if gen_quick > 20:
            boon = 'Quickness'

    #Définition de persos
    stats = f"ㅤ**- Perso: **{df_dps['Profession'].iloc[0]}ㅤㅤ \n"
    if boon != "none":
        uptime_boon = 0
        compteur = 0
        #Pour chaque ligne, récupère l'uptime du boon du gars pour ensuite faire le pourcentage moyen d'uptime du sous_groupe
        for _, ligne in df_dps_glo.iterrows():
            if sub == ligne['Sub Group']:
                nom_mate = ligne['Name']
                uptime_boon += float(df_boon_uptime[boon][df_boon_uptime['Name'] == nom_mate].iloc[0][:-1])
                compteur += 1
        uptime_boon = uptime_boon / compteur

        if boon == 'Quickness':
            boon_stats += (f" Quick \n"
                      f"ㅤ**- Uptime:** {round(uptime_boon,1)}% ")
        elif boon == 'Alacrity':
            boon_stats += (f" Alac \n"
                      f"ㅤ**- Uptime:** {round(uptime_boon,1)}% ")
            
            
    
    #Test is soigneur
    if 'Healing:' in df_dps['Role'][df_dps['Account'] == nom_de_compte].iloc[0]:      
        stats += (f"ㅤ**- Rôle:** Heal {boon_stats} \n")        
    else:
        stats += (f"ㅤ**- Rôle:** DPS {boon_stats} \n"
                  f"ㅤ**- DPS:** {degat} \n")

    return stats

#####Definition des embed#####

def embedstatistique():

    for nom ,objet in Boss.instances.items():
        Boss.trouverBoss(objet, nom, date_modification)
    print(Boss.debut_soiree)

    if Boss.fin_soiree != 0:
        delta_temps = [int(Boss.fin_soiree[0:2]) - int(Boss.debut_soiree[0:2]),
                       int(Boss.fin_soiree[2:4]) - int(Boss.debut_soiree[2:4]),
                       int(Boss.fin_soiree[4:]) - int(Boss.debut_soiree[4:])]

        if delta_temps[2] < 0:
            delta_temps[1] -= 1
            delta_temps[2] += 60

        if delta_temps[1] < 0:
            delta_temps[0] -= 1
            delta_temps[1] += 60
    else:
        delta_temps = [0,0,0]



    _ , objet_joueurs = Joueur.liste_joueurs()
    stats_global = [[],[],[],[]] #[[Mort],[Terre],[Mecanique],[calin de dhuum]]
    csv_raid = fonction.csv_recup(url_raid)

    for objet in objet_joueurs:
        if objet.raid(csv_raid) == True:
            
            stats_global[0].append(int(objet.nbr_mort))
            stats_global[1].append(int(objet.nbr_terre))
            stats_global[2].append(int(objet.nbr_mecanique))
            stats_global[3].append(int(objet.calin))
            print(int(objet.calin))

    moyenne_terre = round(sum(stats_global[1]) / len(stats_global[1]))
    note_mecs = round(sum(stats_global[2]) / len(stats_global[2]) * 2 / 10)

    stat_g = (
            f"ㅤ- Joueur tombé à terre en moyenne: **{moyenne_terre}** \n"
            f"ㅤ- Total des mécaniques ratées: **{sum(stats_global[2])}** \n"
            f"ㅤ- Durée de la session: **{delta_temps[0]}h{delta_temps[1]}min** \n"
        )

    note = 'ㅤㅤ🟥 🟥 🟥 🟥 🟥 🟥 🟥 🟥 🟥 🟥'
    malus = 10 - round((moyenne_terre + note_mecs) / 2)
    note = note.replace('🟥','🟩', malus)
        

    log("Création de l'embed statistique.", 0)
    embed = discord.Embed(title = "**Statistique:**", description = "Voici les statistiques de la dernière sortie en Guilde, Inae 4 pour le pire comme pour l'encore plus méga pire", color=0x80ff80)
    embed.add_field(name = "\u200b" , value = "" , inline = False)
    embed.set_thumbnail(url="https://i.ibb.co/rHyn3Qs/sdfsdf.png")
    embed.add_field(name="Statistiques globales:", value=stat_g, inline=False)
    embed.add_field(name="\u200b", value='', inline=False)
    compteur = 0 
    for i in range(len(objet_joueurs)):
        if objet_joueurs[i].nbr_mort != -1: 
            compteur += 1

            stats = (f"ㅤ- Mort: **{objet_joueurs[i].nbr_mort}** \n"
                     f"ㅤ- A terre: **{objet_joueurs[i].nbr_terre}** \n"
                     f"ㅤ- Mécanique: **{objet_joueurs[i].nbr_mecanique}**")
            if objet_joueurs[i].calin != -1:
                stats = stats + f" \nㅤ- Câlin: **{int(objet_joueurs[i].calin)}**"
                
            embed.add_field(name = (f"# {objet_joueurs[i].pseudo}:"), value = stats , inline = True)
            if compteur == 2 or compteur ==  5 or compteur == 8:
                embed.add_field(name="\u200b", value='', inline=False)

    embed.add_field(name="\u200b", value='\u200b', inline=False)        
    embed.add_field(name="Note de la sortie:", value=note, inline=False) 

    return embed

def embed_detail(lien: str):

    #Traiter le lien
    raccourcis_nom = lien[lien.index('_') +1 :]
    date_essais = lien[lien.index('-') +1 : lien.index('_')]

    #Test si le log du boss est déjà dans l'instance du boss, sinon le crée
    if  not Boss.instances[raccourcis_nom].recherche_combat_dans_Boss(date_essais):
        log(f'{date_essais} non trouvé dans df_global de {raccourcis_nom}, démarrage traiterlogs', 0)
        traiterLogs(lien)

    df_global = Boss.instances[raccourcis_nom].df_global[Boss.instances[raccourcis_nom].df_global['ID'] == date_essais]
    df_dps = Boss.instances[raccourcis_nom].df_dps[Boss.instances[raccourcis_nom].df_dps['ID'] == date_essais]

    stats_global, couleur = affichage_stats_glo(df_global)

    #Partie statistique classiquo !
    #Définir les propriété de l'embed
    embed = discord.Embed(title = f"**{pointeur_lien_log + 1} / {len(liens_soiree)} - Détail de {df_global['Boss'].iloc[0]} - Global:**",
                              description = "", 
                              color= couleur)

    embed.add_field(name = "\u200b" , value = "" , inline = False)
    embed.set_thumbnail(url="https://i.ibb.co/rHyn3Qs/sdfsdf.png")
    embed.add_field(name="Satistique global:", value= stats_global, inline=False)
    embed.add_field(name="\u200b", value='', inline=False)
    compteur = 0 

    #Parcours tout les jouers de la guilde
    for joueur in list(Joueur.instances.values()):
        if joueur.nom_de_compte in df_dps['Account'].values:
            #récupération des variables.
            nom = joueur.nom_de_compte
            pseudo = joueur.pseudo
            mort = ""
            stats = affichage_stats_glo_joueur(joueur, date_essais, raccourcis_nom)

            if df_dps['Time Died'][df_dps['Account'] == nom].iloc[0] == 1:
                mort = "(mort)"

                    
            #Le texte de l'embed une fois stats remplis    
            embed.add_field(name = (f"# {pseudo}: {mort}"), value = stats , inline = True)
            compteur += 1
            if compteur == 2 or compteur ==  4 or compteur == 6 or compteur == 8:
                embed.add_field(name="\u200b", value='', inline=False)

    #Fin de page, avec le lien du boss en question
    embed.add_field(name="\u200b", value='', inline=False)    
    embed.add_field(name ="Lien du boss:", value = lien , inline = True)

    return embed

def embed_soiree(bouton: int, mecs: bool):

    #Récupération des liens stocké dans histo_log.csv et définiton du pointeur.
    liste_liens_logs = fonction.csv_recup('csv/histo_logs.csv')
    liens_soiree = liste_liens_logs[0]


    #definir le navigateur entre les liens avec limites.
    global pointeur_lien_log
    
    pointeur_lien_log += bouton
        
    if pointeur_lien_log < 0:
        pointeur_lien_log = len(liens_soiree) - 1
    if pointeur_lien_log == len(liens_soiree):
        pointeur_lien_log = 0
    lien = liens_soiree[pointeur_lien_log]

    #Nettoie le lien ("cm" ou autre)
    try:
        lien = lien[:lien.index(" ")]
    except:
        1

    #Traiter le lien
    raccourcis_nom = lien[lien.index('_') +1 :]
    date_essais = lien[lien.index('-') +1 : lien.index('_')]

    #Test si le log du boss est déjà dans l'instance du boss, sinon le crée
    if  not Boss.instances[raccourcis_nom].recherche_combat_dans_Boss(date_essais):
        log(f'{date_essais} non trouvé dans df_global de {raccourcis_nom}, démarrage traiterlogs', 0)
        traiterLogs(lien)

    df_global = Boss.instances[raccourcis_nom].df_global[Boss.instances[raccourcis_nom].df_global['ID'] == date_essais]
    df_dps = Boss.instances[raccourcis_nom].df_dps[Boss.instances[raccourcis_nom].df_dps['ID'] == date_essais]

    stats_global, couleur = affichage_stats_glo(df_global)

    #Partie statistique classiquo !
    if mecs == False:
        #Définir les propriété de l'embed
        embed = discord.Embed(title = f"**{pointeur_lien_log + 1} / {len(liens_soiree)} - Détail de {df_global['Boss'].iloc[0]} - Global:**",
                              description = "", 
                              color= couleur)

        embed.add_field(name = "\u200b" , value = "" , inline = False)
        embed.set_thumbnail(url="https://i.ibb.co/rHyn3Qs/sdfsdf.png")
        embed.add_field(name="Satistique global:", value= stats_global, inline=False)
        embed.add_field(name="\u200b", value='', inline=False)
        compteur = 0 

        #Parcours tout les jouers de la guilde
        for joueur in list(Joueur.instances.values()):
            if joueur.nom_de_compte in df_dps['Account'].values:
                #récupération des variables.
                nom = joueur.nom_de_compte
                pseudo = joueur.pseudo
                mort = ""
                stats = affichage_stats_glo_joueur(joueur, date_essais, raccourcis_nom)

                if df_dps['Time Died'][df_dps['Account'] == nom].iloc[0] == 1:
                    mort = "(mort)"

                    
                #Le texte de l'embed une fois stats remplis    
                embed.add_field(name = (f"# {pseudo}: {mort}"), value = stats , inline = True)
                compteur += 1
                if compteur == 2 or compteur ==  4 or compteur == 6 or compteur == 8:
                    embed.add_field(name="\u200b", value='', inline=False)

        #Fin de page, avec le lien du boss en question
        embed.add_field(name="\u200b", value='', inline=False)    
        embed.add_field(name ="Lien du boss:", value = lien , inline = True)

    #Partie Mécaniques ! :)
    if mecs == True:
        #Definir l'embed
        embed = discord.Embed(title = f"**{pointeur_lien_log + 1} / {len(liens_soiree)} - Détail de {Boss.instances[raccourcis_nom].nom_francais} - Mécaniques:**", description = "", color= couleur)

        embed.add_field(name = "\u200b" , value = "" , inline = False)
        embed.set_thumbnail(url="https://i.ibb.co/rHyn3Qs/sdfsdf.png")
        embed.add_field(name="Satistique global:", value= stats_global, inline=False)
        embed.add_field(name="\u200b", value='', inline=False)
        compteur = 0 

        #Définir la variable stats, qui va afficher seulement les mécaniques importante, trtaduite en français.
        stats = 1 #affichage_mecs(raccourcis_nom, log_boss)

        for joueur in list(Joueur.instances.values()):
            try: 
                pseudo = joueur.pseudo
                
                embed.add_field(name = (f"# {pseudo}:"), value = stats[compteur] , inline = True)
                compteur += 1
                if compteur == 2 or compteur ==  4 or compteur == 6 or compteur == 8:
                    embed.add_field(name="\u200b", value='', inline=False)
            except:
                1
        embed.add_field(name="\u200b", value='', inline=False)    
        embed.add_field(name ="Lien du boss:", value = lien , inline = True)
    return embed

def embed_role(joueur, boss):

    for nom in Joueur.instances.values():
        if nom.id_discord == joueur:
            graphique, taille = quel_role_sur_quel_boss(boss,nom.nom_de_compte)
            break
    
    info = f"Nom :  {nom.nom_de_compte} \n Nombre de try: {taille}"

    #Début Embed
    couleur = discord.Colour.green()
    embed = discord.Embed(title = f"Répartition des rôles pour {Boss.instances[boss].nom_francais}: ", description = "", color= couleur)

    embed.add_field(name = "\u200b" , value = "" , inline = False)
    embed.set_thumbnail(url="https://i.ibb.co/rHyn3Qs/sdfsdf.png")
    embed.add_field(name="Information:", value= info, inline=False)
    embed.add_field(name="\u200b", value='', inline=False)

    embed.set_image(url="attachment://mon_graphique.png")
    
    return graphique, embed

async def stats_message(message):

    #Actualiser liens_soiree si des liens sont postés pendant le bot est allumé. Remet à 0 le pointeur.
    if message.channel.id == 892509041140588581:
        global liens_soiree
        global pointeur_lien_log
        liens_soiree = message.content.split('\n') 
        pointeur_lien_log = 0
