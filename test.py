from datetime import datetime
import locale
import threading
import schedule # type: ignore
import time
import json

#Mettre les jours en français
locale.setlocale(locale.LC_TIME, 'fr_FR')

date_du_jour = datetime.now()
nom_du_jour = date_du_jour.strftime("%A")

print(date_du_jour.day)


def trouver_jour(date: str):
    '''
    Fonction qui a pour but de trouver dans un string le jour de la semaine entrée par un utilisateur et en ressort le delta entre
    le jour entrée et le jour actuelle.

    return delta: int
    '''
    liste_jours = ['lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche']
    date = date.lower().split()

    if date[0] in liste_jours:
        print(date[0])

        if liste_jours.index(nom_du_jour) < liste_jours.index(date[0]):
            delta = liste_jours.index(date[0]) - liste_jours.index(nom_du_jour)
            print( liste_jours.index(date[0]) - liste_jours.index(nom_du_jour) )
            return delta
        else:
            print('Jour de la semaine choisit est déjà passé !')
    
    else:
        print('Jour de la semaine non reconnu')
    
    return -1



#Définitions de schedule pour qu'il démarre a tel heure et execute tel fonction.
schedule.every().day.at("16:21").do(lambda: trouver_jour('Dimanche 12 juin'))

#Fonction qui va être lancé dans le thread
def executer_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

#Création et lancement du thread pour ne pas bloquer le reste du programme.
#Le code va s'éxécuter en """""""parallele""""""" du reste du code
schedule_thread = threading.Thread(target=executer_schedule)
schedule_thread.start()


print('suite du programme ...')