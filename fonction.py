from datetime import datetime
import csv
import os

"""
Fichier python contenant des fonction utilitaires

"""
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

