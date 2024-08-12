from fonction import log
import discord
import ast

#Definir l'embed inscription
def embed_inscriptions(
                        nom_de_la_sortie: str = None, 
                        descriptions: str = None, 
                        date: str = None, 
                        liste_joueur: list = None, 
                        nombre_inscrit: int = None, 
                        liste_joueur_absent: list = None
                        ):
    
    '''
    Créer un embed inscription en fonction des paramètres d'entrée.
    Si aucun paramètre n'est entrée crée un embed vide

    ### Arguments:
    - nom_de_la_sortie (str)
    - descriptions (str) 
    - date (str) 
    - liste_joueur (list) 
    - nombre_inscrit (int) 
    - liste_joueur_absent (list) 

    ### Renvoie:
    - embed (embed) : embed discord
    '''

    log("| Fonction embed_inscriptions | Création de l'embed inscription.", 0)

    #Test des types des Arguments
    if not type(nom_de_la_sortie) == str or not type(descriptions) == str or not type(date) == str:
        log(f"| Fonction embed_inscriptions | Problème d'argument, format non valide ({nom_de_la_sortie}, {descriptions}, {date}")
        return "erreur"

    
    #Mise en forme de liste_joueur pour une version affichable dans un embed (saut de ligne, "", etc)
    format_liste_joueur = f""
    format_reserve =f""
    nombre_reserve = 0
    for i in range(len(liste_joueur)):
        if i <10:
            format_liste_joueur += "ㅤ- " + liste_joueur[i].strip("'") + '\n'
        if i >= 10: #Si plus de 10 joueurs, alors stock dans reserve
            format_reserve += "ㅤ- " + liste_joueur[i].strip("'") + '\n'
            nombre_reserve +=1

    #Mise en forme de format_liste_joueur_absent pour une version affichable dans un embed (saut de ligne, "", etc)
    format_liste_joueur_absent = f""
    for i in range(len(liste_joueur_absent)):
        format_liste_joueur_absent += "ㅤ- " + liste_joueur_absent[i].strip("'") + '\n'

            
    #Début de la création de l'embed
    embed_inscription = discord.Embed(title = f"**Inscription {nom_de_la_sortie}:ㅤㅤㅤㅤ**", description ="", color=0x80ff80)
    embed_inscription.set_thumbnail(url="https://i.ibb.co/rHyn3Qs/sdfsdf.png")
    embed_inscription.add_field(name = "" , value = descriptions , inline = False)
    embed_inscription.add_field(name = "Date:" , value = date , inline = False)
    embed_inscription.add_field(name = "\u200b" , value = "" , inline = False)
    
    #Création de la ligne de carré en fonction du nombre d'inscris
    total = 0
    test = ""
    if 'fractale' in nom_de_la_sortie.lower():
        total = 5
        if nombre_inscrit == 0:
            test = "⬜ ⬜ ⬜ ⬜ ⬜"
    else:
        total = 10
        if nombre_inscrit == 0:
            test = "⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜"

    for i in range(total):
        if i < int(nombre_inscrit):
            test = test + " " + "🟦"
        else:
            test = test + " " + "⬜"

    if nombre_reserve != 0:
        test = test.replace("🟦",'🟩',nombre_reserve)


    if "fractale" in nom_de_la_sortie.lower():
        embed_inscription.add_field(name = f"Personne inscrite: {nombre_inscrit} / 5" , value = format_liste_joueur , inline = False)
        embed_inscription.add_field(name = "\u200b" , value = "" , inline = False)
        embed_inscription.add_field(name = "\u200b" , value = test , inline = False)

    else:
        embed_inscription.add_field(name = f"Personne inscrite: {nombre_inscrit} / 10" , value = format_liste_joueur , inline = False)
        if int(nombre_inscrit) > 10:
            embed_inscription.add_field(name = f"Réserve: {nombre_reserve}" , value = format_reserve , inline = False)
        if len(liste_joueur_absent) != 0:
            embed_inscription.add_field(name = "\u200b" , value = "" , inline = False)
            embed_inscription.add_field(name = "Non disponible:" , value = format_liste_joueur_absent , inline = False)
        embed_inscription.add_field(name = "\u200b" , value = "" , inline = False)
        embed_inscription.add_field(name = "\u200b" , value = test , inline = False)

    embed_inscription.add_field(name = "\u200b" , value = "" , inline = False)
    

    return embed_inscription

#Embed incscription hebdo
def embed_inscription_semaine(
                              date = 0, 
                              liste_joueur = 0):

    #Début de la création de l'embed
    embed = discord.Embed(title = f"**Inscription Hebdomadaire:ㅤㅤㅤㅤ**", description ="", color=0x80ff80)
    embed.set_thumbnail(url="https://i.ibb.co/rHyn3Qs/sdfsdf.png")
    embed.add_field(name = "" , value = "Le but est de savoir qui est là quelle jour et en fonction on avise quand on sort !" , inline = False)
    embed.add_field(name = "Date:" , value = date , inline = False)
    embed.add_field(name = "\u200b" , value = "" , inline = False)

    liste_joueur = ast.literal_eval(liste_joueur)
    jour_semaine = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']
    for num, jour in enumerate(jour_semaine):
        embed.add_field(name = f"{jour}: " , value =  f"ㅤㅤNombre présent: {liste_joueur[num]}", inline = False)



    return embed
