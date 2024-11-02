import requests

url = "https://dps.report/uploadContent"

# Définir les paramètres de la requête
params = {
    'json': 1,  # Pour obtenir une réponse JSON
    'generator': 'ei',  # Outil de génération de log
    'anonymous': 'false',  # Option d'anonymisation
    'userToken' : ""
}

# Envoyer le fichier en tant que form-data
with open(r'C:\Users\Greg\Documents\Guild Wars 2\addons\arcdps\arcdps.cbtlogs\16199\20210117-170632.evtc', 'rb') as file:
    files = {
        'file': file
    }
    response = requests.post(url, params=params, files=files)

# Vérifier la réponse
if response.status_code == 200:
    print("Upload réussi :", response.json())
else:
    print("Erreur lors de l'upload :", response.status_code, response.text)
