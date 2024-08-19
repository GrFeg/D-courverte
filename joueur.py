import os
import json
from fonction import log

chemin_fichier_info = '_donnee/info.json'


if os.path.isfile(chemin_fichier_info):
    #Récupération des configurations du bot
    with open(chemin_fichier_info) as config_file:
        INFO_JOUEUR = json.load(config_file)['joueur']
else:
    log("Fichier info_raid.json introuvable", 3)


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
        Joueur.instances[self.id_discord] = self

    
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


#Definition des boss présent dans le jeu
def init_instances_joueur(INFO_JOUEUR):
    for joueur in INFO_JOUEUR.values():
        Joueur(joueur['nom_discord'], joueur['nom_de_compte'], joueur['ID_DISCORD'])
    

    log(f"Les objets Joueur sont bien crées, nombre crée: {Joueur.nombre_joueurs}", 1)

init_instances_joueur(INFO_JOUEUR)