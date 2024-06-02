import discord
from discord.ext import commands
import main
import fonction
from fonction import log
import ast
import json
from pathlib import Path
import os

#Fonction setup qui va définir quel type de bot.event sont utilisé dans ce fichier
async def setup(bot):

    #Detection de suppression d'une réaction sur un message
    async def reaction_remove(payload):
        await on_raw_reaction_remove(payload, bot)
    bot.add_listener(reaction_remove, 'on_raw_reaction_remove')

    #Detection d'ajout de réaction sur un message
    async def reaction_add(payload):
        await on_raw_reaction_add(payload, bot)
    bot.add_listener(reaction_add, 'on_raw_reaction_add')


if os.path.isfile( Path('config.json') ):
    #Récupération des configurations du bot
    with open('config.json') as config_file:
        config = json.load(config_file)

    ID_BOT = config['ID_BOT']
else:
    log("Fichier config.json introuvable", 3)


#Definir l'embed inscription
def inscriptions(type_de_sortie = 0, 
                 descriptions = 0, 
                 date = 0, 
                 liste_joueur = 0, 
                 nombre = 0, 
                 liste_joueur_absent = 0):
    
    '''
    Fonction qui créer un embed inscription en fonction des paramètres d'entrée.
    Si aucun paramètre n'est entrée crée un embed vide

    return l'embed
    '''

    log("Création de l'embed inscription.", 0)
    
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
    embed_inscription = discord.Embed(title = f"**Inscription {type_de_sortie}:ㅤㅤㅤㅤ**", description ="", color=0x80ff80)
    embed_inscription.set_thumbnail(url="https://i.ibb.co/rHyn3Qs/sdfsdf.png")
    embed_inscription.add_field(name = "" , value = descriptions , inline = False)
    embed_inscription.add_field(name = "Date:" , value = date , inline = False)
    embed_inscription.add_field(name = "\u200b" , value = "" , inline = False)
    
    #Création de la ligne de carré en fonction du nombre d'inscris
    total = 0
    test = ""
    if 'fractale' in type_de_sortie.lower():
        total = 5
        if nombre == 0:
            test = "⬜ ⬜ ⬜ ⬜ ⬜"
    else:
        total = 10
        if nombre == 0:
            test = "⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜"

    for i in range(total):
        if i < int(nombre):
            test = test + " " + "🟦"
        else:
            test = test + " " + "⬜"

    if nombre_reserve != 0:
        test = test.replace("🟦",'🟩',nombre_reserve)


    if "fractale" in type_de_sortie.lower():
        embed_inscription.add_field(name = f"Personne inscrite: {nombre} / 5" , value = format_liste_joueur , inline = False)
        embed_inscription.add_field(name = "\u200b" , value = "" , inline = False)
        embed_inscription.add_field(name = "\u200b" , value = test , inline = False)

    else:
        embed_inscription.add_field(name = f"Personne inscrite: {nombre} / 10" , value = format_liste_joueur , inline = False)
        if int(nombre) > 10:
            embed_inscription.add_field(name = f"Réserve: {nombre_reserve}" , value = format_reserve , inline = False)
        if len(liste_joueur_absent) != 0:
            embed_inscription.add_field(name = "\u200b" , value = "" , inline = False)
            embed_inscription.add_field(name = "Non disponible:" , value = format_liste_joueur_absent , inline = False)
        embed_inscription.add_field(name = "\u200b" , value = "" , inline = False)
        embed_inscription.add_field(name = "\u200b" , value = test , inline = False)

    embed_inscription.add_field(name = "\u200b" , value = "" , inline = False)
    

    return embed_inscription

#Detecte l'ajout d'une réaction
async def on_raw_reaction_add(payload, bot):

    #Regarde si ce n'est pas le bot qui réagis (on l'exclus)
    if payload.user_id  != ID_BOT:

        channel = await bot.fetch_channel(payload.channel_id)  
        message = await channel.fetch_message(payload.message_id)  
        emoji = payload.emoji

        guild = bot.get_guild(payload.guild_id)  # Récupère l'objet Guild grâce à l'ID de la guilde
        if guild:
            member = await guild.fetch_member(payload.user_id)

        
        if emoji.name  == "✅" or emoji.name  == "❌":
            csv_embed = fonction.csv_recup('csv/varaible.csv')
            n_embed = main.recherche_embed(csv_embed, message.id)
        else:
            return

        #Regarde si la réaction est sur le bonne embed
        if int(csv_embed[n_embed][0]) == message.id and (emoji.name  == "✅") and n_embed != -1:
            csv_embed[n_embed][4] = ast.literal_eval(csv_embed[n_embed][4])
            csv_embed[n_embed][6] = ast.literal_eval(csv_embed[n_embed][6])

            if payload.member.global_name in csv_embed[n_embed][6]:
                csv_embed[n_embed][6].remove(payload.member.global_name)

            if payload.member.global_name not in csv_embed[n_embed][4]:
                csv_embed[n_embed][4].append(payload.member.global_name)
                csv_embed[n_embed][5] = len(csv_embed[n_embed][4])

            #Met a jour le csv
            fonction.csv_actu('csv/varaible.csv',csv_embed)
            
            await message.edit(embed=inscriptions(csv_embed[n_embed][1],csv_embed[n_embed][2],csv_embed[n_embed][3],csv_embed[n_embed][4],csv_embed[n_embed][5],csv_embed[n_embed][6]))
            await message.remove_reaction(emoji, member)

            log(f"{payload.member.global_name} inscrit dans {csv_embed[n_embed][1]}", 0)

        #Regarde si la réaction est sur le bonne embed
        if int(csv_embed[n_embed][0]) == message.id and (emoji.name  == "❌") and n_embed != -1:
            csv_embed[n_embed][4] = ast.literal_eval(csv_embed[n_embed][4])
            csv_embed[n_embed][6] = ast.literal_eval(csv_embed[n_embed][6])

            if payload.member.global_name not in csv_embed[n_embed][6]:
                csv_embed[n_embed][6].append(payload.member.global_name)

            if payload.member.global_name in csv_embed[n_embed][4]:
                csv_embed[n_embed][4].remove(payload.member.global_name)
                csv_embed[n_embed][5] = len(csv_embed[n_embed][4])
                
            fonction.csv_actu('csv/varaible.csv',csv_embed)

            await message.edit(embed=inscriptions(csv_embed[n_embed][1],csv_embed[n_embed][2],csv_embed[n_embed][3],csv_embed[n_embed][4],csv_embed[n_embed][5],csv_embed[n_embed][6]))
            await message.remove_reaction(emoji, member)

            log(f"{payload.member.global_name} désinscrit de {csv_embed[n_embed][1]}")


        print(f"Réaction: {emoji.name} ajouté sur un message par {payload.member.global_name}.")

#Detecte la suppression d'une réaction
async def on_raw_reaction_remove(payload, bot):
    1

