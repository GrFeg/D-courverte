from datetime import datetime


date_du_jour = datetime.now()

print(date_du_jour.day)


def trouver_jour(date):
    liste_jours = ['lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche']
    date = date.lower().split()

    if date[0] in liste_jours:
        print('oui !')

trouver_jour('lundi 12 juin')