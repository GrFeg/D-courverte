import os
from config_logger import logger
from boss import Boss
import csv
import pandas as pd

CHEMIN_RACINE = os.path.dirname(__file__).split(r'\commande\recap_raid')[0]
STOCKAGE_FICHIER_LOG = "log_dps"

#Fonction pour les fichiers parse.csv, change le nom du boss pour correspondre au raccourcis_nom
def parse_nom_boss(boss : str):
    if boss == 'twinlargos':
        boss = 'twins'
        
    if boss == 'twstcstl':
        boss = 'esc'
                    
    if boss == 'prlqadim':
        boss = 'qpeer'
                    
    if boss == 'aetherhide':
        boss = 'trin'
                    
    if boss == 'river':
        boss = 'rr'
                    
    if boss == 'xunjadejunk':
        boss = 'ankka'
                    
    if boss == 'escort':
        boss = 'esc'
    
    return boss

def init_log():

    #Recupère tout les fichiers d'un dossier 
    chemin_dossier = os.path.join(CHEMIN_RACINE, STOCKAGE_FICHIER_LOG)

    #Test si le fichier existe
    if not os.path.isdir(chemin_dossier):
        logger.error(f"Le dossier {chemin_dossier} n'éxiste pas !")
        return "erreur"
    
    #Récupère tout les fichiers present dans le dossier
    fichiers = os.listdir(chemin_dossier)

    compteur = 0
    #Pour chaque fichier dans fichiers
    for fichier in fichiers:
        
        #creer le chemin complet avec le nom du fichier
        chemin_complet = os.path.join(chemin_dossier, fichier)

        date = fichier.split('_')[0]
        nom_boss = fichier.split('_')[1]

        #Adapte le nom du boss pour correspondre au bon raccourcis
        nom_boss = parse_nom_boss(nom_boss)

        if Boss.nom_boss_existe(nom_boss):
            instance_boss = Boss.instances[nom_boss]
            instance_boss: Boss
        else:
            logger.error(f"Nom de fichier non reconnu: {nom_boss}, fichier suivant ! ! ! ")
            continue

        if instance_boss.recherche_combat_existe_dans_Boss(date):
            logger.error(f"Combat ({date}_{nom_boss}) existe déjà, fonction avorté ! !")
            os.remove(chemin_complet)
            continue
        else:
            logger.debug(f"Combat ({date}_{nom_boss}) non trouvée, récupération logs")

        #Si le fichier existe
        if os.path.isfile(chemin_complet):
            
            #Si c'est un csv
            if fichier.endswith('.csv'):
                
                data = []
                #Stock le fichier dans data
                with open(chemin_complet, mode='r', encoding='utf-8', errors='replace') as file:
                    reader = csv.reader(file)
                    
                    for row in reader:
                        new_row = [cell.replace('�', 'é') for cell in row]
                        data.append(new_row)
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
                if not len(df_tableau) == 25:
                    #os.remove(chemin_complet)
                    logger.error(f'Nombre de DF insuffisant, log non chargé !')
                    continue

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

                    boss = parse_nom_boss(boss)

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
    return True