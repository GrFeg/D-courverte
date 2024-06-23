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
from pathlib import Path
from boss import Boss, traiterLogs, traitement_message_log
from typing import Type


pointeur_lien_log = 0

if os.path.isfile( Path('config.json')):
    #Récupération des configurations du bot
    with open('config.json') as config_file:
        config = json.load(config_file)

    ID_JOUEUR_PIZZABLEU = config['ID_JOUEUR_PIZZABLEU']
    ID_JOUEUR_CLOUD = config['ID_JOUEUR_CLOUD']
    ID_JOUEUR_ELNABO = config['ID_JOUEUR_ELNABO']
    ID_JOUEUR_ARKHANGE = config['ID_JOUEUR_ARKHANGE']
    ID_BOT = config['ID_BOT']

    CHEMIN_HISTO_LOGS = '/csv/histo_logs.csv'
    CHEMIN_BOSS_HEBDO = 'csv/boss_done_hebdo.csv'
    CHEMIN_RACINE = os.path.dirname(__file__) 

    date_du_jour = datetime.now()
    numero_semaine = int( date_du_jour.strftime('%W') )

else:
    log("Fichier config.json introuvable", 3)


class Joueur:

    """
    Class qui définit touts les joueurs de raids des InAe !
    """
    nombre_joueurs = 0
    instances = {}

    def __init__(self, pseudo, nom_de_compte, id_discord = -1):
        
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

#Fonction pour lire tout les csv d'un boss est les stocker, doublon ?????! ! ! 
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

#Joueur de la guilde
if 1:
    cloud = Joueur("Cloud","Cloudlloyd.9240", ID_JOUEUR_CLOUD)
    tenro = Joueur("Tenro",'Tenro.8107')
    elnabo = Joueur('Elnabo','Elnabo.2014', ID_JOUEUR_ELNABO)
    drakh = Joueur('Drakh','Drakh.7321')
    pizza = Joueur('PizzaBleu',"PizzaBleu.7615", ID_JOUEUR_PIZZABLEU)
    nils = Joueur('Nils','Nils.7289')
    blade = Joueur('BladeLarkin','bladelarkin.5790')
    gon = Joueur('Gon','BigBang.9125')
    yoda = Joueur('Yoda','Mini maitreyoda.7849')
    elias = Joueur('Ellias','Spongex.7864')
    damien = Joueur('Damien','Escrimeur.4192')
    nachryma = Joueur('Nachryma','ZancrowFT.7319')
    clement = Joueur('Clement','The Mangoose.7643')
    arkhange = Joueur('Arkhange', 'arkange.4759', ID_JOUEUR_ARKHANGE)

    log(f"Les objets joueurs sont bien crées, nombre crée: {Joueur.nombre_joueurs}", 1)


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
                        df = pd.read_csv(CHEMIN_RACINE + chemin, index_col=False)
                        if key == 'Stats_global':
                            if df['Time Start'].isin([value['Time Start'].iloc[0]]).any():
                                break


                        cols = df.columns  
                        value = value.reindex(columns=cols)
                        df = pd.concat([df, value], ignore_index=True)
                        print(f'\rProgression: avant {len(df.columns)} après {len(value.columns)}', end='')
                        df.to_csv(CHEMIN_RACINE + chemin, index = False)
                    except:
                        
                        value.to_csv(CHEMIN_RACINE + chemin, index = False)

                compteur += 1 
                
                os.remove(chemin_complet)
    return

#Fonction pour afficher un graphique des rôles
def joli_graphique(df : pd.DataFrame):

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
    plt.gca().set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])  # Définir les positions des ticks
    plt.gca().set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
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
def affichage_stats_glo_joueur(joueur: Type[Joueur], date_essais : str, raccourcis_nom: str):

    #Récupération de l'instance Boss pour le boss en question (raccourcis_nom)
    instance_boss = Boss.instances[raccourcis_nom]
    instance_boss: Type[Boss]

    #Récupération des différents df utilisé dans cette fonction
    df_dps_glo = instance_boss.df_dps[instance_boss.df_dps['ID'] == date_essais]
    df_dps_glo : pd.DataFrame

    #Copie de df_dps_glo pour modifier le df sans impacter la boucle for plus bas
    df_dps = df_dps_glo.copy()
    df_dps = df_dps[df_dps['Account'] == joueur.nom_de_compte]
    df_dps : pd.DataFrame

    nom_personnage = df_dps['Name'].iloc[0]

    df_gen_group = instance_boss.df_gen_group[instance_boss.df_gen_group['ID'] == date_essais]
    df_gen_group = df_gen_group[df_gen_group['Name'] == nom_personnage]
    df_gen_group : pd.DataFrame
    
    df_boon_uptime = instance_boss.df_boon_uptime
    df_boon_uptime = df_boon_uptime[df_boon_uptime['ID'] == date_essais]
    df_boon_uptime : pd.DataFrame

    #Définition des variables
    nom_de_compte = joueur.nom_de_compte

    degat = str(round(df_dps['Boss DPS'].iloc[0] / 1000,2)) + "K"
    sub = df_dps['Sub Group'].iloc[0]
    gen_alac = df_gen_group['Alacrity'].iloc[0]
    gen_quick = df_gen_group['Quickness'].iloc[0]
    boon = "none"
    boon_stats = ""

    #Regarde si alac est superieur à 0, si oui enlève le % et convertit en float.
    if str(gen_alac) != '0' :
        gen_alac = float(gen_alac[:-1])
        if gen_alac > 20:
           boon = 'Alacrity' 
    if str(gen_quick) != '0':
        gen_quick = float(gen_quick[:-1])
        if gen_quick > 20:
            boon = 'Quickness'

    #Définition de persos
    stats = f"ㅤ**- Perso: **{df_dps['Profession'].iloc[0]}ㅤㅤ \n"

    #Regarde si les boons existe bien
    if boon != "none":
        uptime_boon_cumulee = 0
        compteur = 0
        #Pour chaque ligne, récupère l'uptime du boon du gars pour ensuite faire le pourcentage moyen d'uptime du sous_groupe
        for _, ligne in df_dps_glo.iterrows():

            #Si la personne est dans le bon sous groupe
            if sub == ligne['Sub Group']:

                #Récupère le nom de l'allié
                nom_mate = ligne['Name']

                #print(df_boon_uptime[boon][df_boon_uptime['Name'] == nom_mate].iloc[0]) #DEBBUG pour les boons

                #Test si les boons ne valent pas 0
                if not df_boon_uptime[boon][df_boon_uptime['Name'] == nom_mate].iloc[0] == '0':

                    #Récupère l'uptime et le voncertis en float (en enlevant le % à la fin)
                    uptime_boon_cumulee += float(str(df_boon_uptime[boon][df_boon_uptime['Name'] == nom_mate].iloc[0])[:-1])
                else:
                    
                    #Sinon met à 0
                    uptime_boon_cumulee += 0
                
                compteur += 1

        #Fait la moyenne
        uptime_boon = uptime_boon_cumulee / compteur

        #Regarde si le boon est quickness ou alac pour afficher le bon nom du bonus
        if boon == 'Quickness':
            boon_stats += (f" Quick \n"
                      f"ㅤ**- Uptime:** {round(uptime_boon,1)}% ")
        elif boon == 'Alacrity':
            boon_stats += (f" Alac \n"
                      f"ㅤ**- Uptime:** {round(uptime_boon,1)}% ")
             
    
    #Test is soigneur et ne met pas la ligne du DPS si oui, sinon la rajoute
    if 'Healing:' in df_dps['Role'][df_dps['Account'] == nom_de_compte].iloc[0]:      
        stats += (f"ㅤ**- Rôle:** Heal {boon_stats} \n")        
    else:
        stats += (f"ㅤ**- Rôle:** DPS {boon_stats} \n"
                  f"ㅤ**- DPS:** {degat} \n")

    return stats

########## Definition des embed ##########

#Embed chargé lorsqu'il y a une erreur
def embed_erreur():
    #Définir les propriété de l'embed
    embed = discord.Embed( title = f"** Upsi . . . **",
                           description = "", 
                           color= discord.Colour.red()
                         )
    embed.set_thumbnail(url="https://i.ibb.co/rHyn3Qs/sdfsdf.png") #Image en haut à droite

    #Partie Global de l'embed
    embed.add_field(name = ". . ." , value = "Il y a eu un problème :(" , inline = False)

    return embed

#Embed pour les statistique avec le log.csv cassé ?
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

#Embed pour la commande detail_soiree
def embed_detail(lien: str):

    if len(traitement_message_log(lien)) == 0:
        return embed_erreur()
    
    #Traiter le lien
    raccourcis_nom = lien[lien.index('_') +1 :]
    date_essais = lien[lien.index('-') +1 : lien.index('_')]

    #Récupération de l'instance Boss pour le boss en question (raccourcis_nom)
    instance_boss = Boss.instances[raccourcis_nom]
    instance_boss: Type[Boss]

    #Test si le log du boss est déjà dans l'instance du boss, sinon le crée
    if  not instance_boss.recherche_combat_existe_dans_Boss(date_essais):
        log(f'{date_essais} non trouvé dans df_global de {raccourcis_nom}, démarrage traiterlogs', 0)
        resultat = traiterLogs(lien)

        if resultat == -1:
            return embed_erreur()


    #Récupération du df_global pour la date du lien
    df_global = instance_boss.df_global[instance_boss.df_global['ID'] == date_essais]
    df_global : pd.DataFrame

    #Récupération du df_dps pour la date du lien
    df_dps = instance_boss.df_dps[instance_boss.df_dps['ID'] == date_essais]
    df_dps : pd.DataFrame

    #Crée l'affichage utilisé dans l'embed pour la partie global
    stats_global, couleur = affichage_stats_glo( df_global )

    #Définir les propriété de l'embed
    embed = discord.Embed( title = f"** Détail de {df_global['Boss'].iloc[0]} - Global:**",
                           description = "", 
                           color= couleur
                         )
    embed.set_thumbnail(url="https://i.ibb.co/rHyn3Qs/sdfsdf.png") #Image en haut à droite

    #Partie Global de l'embed
    embed.add_field(name = "\u200b" , value = "" , inline = False)
    embed.add_field(name="Satistique global:", value= stats_global, inline=False)
    embed.add_field(name="\u200b", value='', inline=False)

    #Partie propre à chaque joueur de l'embed
    compteur = 0 

    #Parcours tout les joueurs de la guilde
    for joueur in list(Joueur.instances.values()):
        joueur : Type[Joueur]

        #Regarde si le joueur récupéré à bien participé a ce raid
        if joueur.nom_de_compte in df_dps['Account'].values:

            #Récupération des information du joueurs
            nom = joueur.nom_de_compte
            pseudo = joueur.pseudo
            compteur += 1

            #Crée l'affichage utilisé dans l'embed pour la partie joueur
            stats = affichage_stats_glo_joueur(joueur, date_essais, raccourcis_nom)

            #Regarde si le joueur est mort
            if df_dps['Time Died'][df_dps['Account'] == nom].iloc[0] == 1:
                mort = "(mort)"
            else:
                mort = ""

            #Ajoute le titre et l'affichage de stats du joueur à l'embed   
            embed.add_field(name = (f"# {pseudo}: {mort}"), value = stats , inline = True)

            #Permet le saut de ligne tout les deux joueurs entré dans l'embed
            if compteur == 2 or compteur ==  4 or compteur == 6 or compteur == 8:
                embed.add_field(name="\u200b", value='', inline=False)

    #Fin de page, avec le lien du boss en question
    embed.add_field(name="\u200b", value='', inline=False)    
    embed.add_field(name ="Lien du boss:", value = lien , inline = True)

    return embed

#Embed pour la commande soirée
def embed_soiree(bouton: int, mecs: bool):

    #Récupération des liens stocké dans histo_log.csv et définiton du pointeur.
    df_logs = pd.read_csv(CHEMIN_RACINE + CHEMIN_HISTO_LOGS)

    dernier_jour = df_logs['date'].max()
    liens_soiree = df_logs['logs'][df_logs['date'] == dernier_jour].to_list()


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

    if len(traitement_message_log(lien)) == 0:
        return embed_erreur()

    #Définition des variables
    raccourcis_nom = lien[lien.index('_') +1 :]

    #Récupération de l'instance Boss pour le boss en question (raccourcis_nom)
    if raccourcis_nom in Boss.instances:
        instance_boss = Boss.instances[raccourcis_nom]
        instance_boss: Type[Boss]
    else:
        log(f"| Fonction embed_soiree() | Instance du boss : {raccourcis_nom} non trouvé ! ! !", 2)
        return embed_erreur()

    date_essais = lien[lien.index('-') +1 : lien.index('_')]

    #Test si le log du boss est déjà dans l'instance du boss, sinon le crée
    if  not instance_boss.recherche_combat_existe_dans_Boss(date_essais):
        log(f'{date_essais} non trouvé dans df_global de {raccourcis_nom}, démarrage traiterlogs', 0)
        resultat = traiterLogs(lien)

        if resultat == -1:
            return embed_erreur()


    df_global = instance_boss.df_global[instance_boss.df_global['ID'] == date_essais]
    df_dps = instance_boss.df_dps[instance_boss.df_dps['ID'] == date_essais]

    stats_global, couleur = affichage_stats_glo(df_global)

    #Partie statistique classiquo !
    if mecs == False:
        #Définir les propriété de l'embed
        embed = discord.Embed(title       =   f"**{pointeur_lien_log + 1} / {len(liens_soiree)} - Détail de {df_global['Boss'].iloc[0]} - Global:**",
                              description =   "", 
                              color       =   couleur)

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
                compteur += 1
                mort = ""

                if df_dps['Time Died'][df_dps['Account'] == nom].iloc[0] == 1:
                    mort = "(mort)"

                stats = affichage_stats_glo_joueur(joueur, date_essais, raccourcis_nom)

                #Le texte de l'embed une fois stats remplis    
                embed.add_field(name = (f"# {pseudo}: {mort}"), value = stats , inline = True)

                
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

#Embed pour la commande rôle
def embed_role(joueur: int, boss: str):

    graphique, taille = 0,0
    for nom in Joueur.instances.values():
        if nom.id_discord == joueur:
            graphique, taille = quel_role_sur_quel_boss(boss,nom.nom_de_compte)
            break
    
    #Test si l'id discord à été trouvé dans les intances joueurs.
    if graphique == 0:
        embed = discord.Embed(title = f"Upsi ", 
                              description = "Tu n'existes pas, demande à la personne qui a ecrit cette ligne de te rajouter . . .", 
                              color= discord.Colour.red())
        return -1, embed
    
    #Si le nom du boss n'est pas reconnu
    if graphique == -1:
        embed = discord.Embed(title = f"Upsi ", 
                              description = "Le Boss que tu as entré n'est pas reconnu, essaye d'entrer les mêmes abréviations que sur les liens des logs . . .", 
                              color= discord.Colour.red())
        return -1, embed

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
