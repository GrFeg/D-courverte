import pandas as pd
import os
import json
from datetime import datetime
from fonction import log
from pathlib import Path

if os.path.isfile( Path('config.json')):
    #Récupération des configurations du bot
    with open('config.json') as config_file:
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
    log("Fichier config.json introuvable", 3)


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

        df_boss_hebdo = pd.read_csv(CHEMIN_RACINE + "/" + CHEMIN_BOSS_HEBDO, index_col = 'num_sem')

        try:
            self.mort_hebdo =  df_boss_hebdo.loc[numero_semaine][raccourcis_nom]
        except KeyError:
            log(f"mort_hebdo non pris en charge pour {raccourcis_nom}", 2)
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
                log(f"Fichier dans {raccourcis_nom} manquant, risque d'erreur probable.", 2)

        else:
            log(f"Le dossier {self.chemin_dossier} n'éxiste pas !", 2)
            dico_df = -1



        
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
        #Test si la variable existe
        if  hasattr(self, 'df_global'):
            log(f"Recherche de {date_essais} dans {self.df_global['ID'].values}, {date_essais in self.df_global['ID'].values}",0)
        else:
            log(f'Fonction recherche_combat_dans_Boss : Erreur, le df n\'est pas chargé ! ! !',2)
            return -1

        if  date_essais in self.df_global['ID'].values:
            return True
        else:
            return False

