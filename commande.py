import discord
from discord.ext import commands
from discord import app_commands
from fonction import log
import fonction
import statistiqueraid
import inscription
import csv
import random
from discord.ui import Button, View
from datetime import datetime, timedelta
import locale
import os
import json
from pathlib import Path

'''
Fichier ou va se trouver le nom de toutes les commandes du bot Discord


'''

if os.path.isfile( Path('config.json')):
    #Récupération des configurations du bot
    with open('config.json') as config_file:
        config = json.load(config_file)

    ID_GUILD_SERVEUR_INAE = config['ID_GUILD_SERVEUR_INAE']

else:
    log("Fichier config.json introuvable", 3)


message_ids = {}



#Definition de la   class   commande
class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    #Commande Statistique de raid
    @app_commands.command(name="statistique", description="Renvoit les statistiques du dernier raid.")
    @discord.app_commands.guilds(discord.Object(id= ID_GUILD_SERVEUR_INAE))
    async def statistique(self, interaction: discord.Interaction):
        await interaction.response.send_message("Arriva")
        
        await interaction.edit_original_response(embed = statistiqueraid.embedstatistique())
    

    #Commande Details_Boss de raid
    @app_commands.command(name="details_boss", description="Renvoit les statistiques du boss.")
    @discord.app_commands.guilds(discord.Object(id= ID_GUILD_SERVEUR_INAE))
    async def details_boss(self, interaction: discord.Interaction, lien: str):
        await interaction.response.send_message("Recheche du log . . .")
        embed = statistiqueraid.embed_detail(lien)
        await interaction.edit_original_response(embed = embed)
    
    #Commande rôles de raid
    @app_commands.command(name="role", description="Renvoit les rôles jouée sur un Boss.")
    @discord.app_commands.guilds(discord.Object(id=ID_GUILD_SERVEUR_INAE))
    async def statistique(self, interaction: discord.Interaction, boss: str):
        joueur = interaction.user.id
        file, embed = statistiqueraid.embed_role(joueur, boss)
        if file != -1:
            await interaction.response.send_message(embed=embed, file=file, ephemeral=False)
        else:
            await interaction.response.send_message(embed=embed)


    #Commande soiree
    @app_commands.command(name="soiree", description="Renvoit les statistiques de la soirée, boss par boss")
    @discord.app_commands.guilds(discord.Object(id= ID_GUILD_SERVEUR_INAE))
    async def soiree(self, interaction: discord.Interaction):
        await interaction.response.send_message("J'utilise mon neuronne pour réfléchir niaaaaaaaaa")
        embed = statistiqueraid.embed_soiree(0, False)

        async def bouton_callback(interaction: discord.Interaction):
            if interaction.data['custom_id'] == "mecanique":
                if bouton2.label == "Mécaniques":
                    mec = True
                    bouton2.label = "Rôle"
                else:
                    mec = False
                    bouton2.label = "Mécaniques"
            else:
                if bouton2.label == "Mécaniques":
                    mec = False
                else:
                    mec = True


            if interaction.data['custom_id'] == "suivant":
                await interaction.response.edit_message(embed = statistiqueraid.embed_soiree(1,mec), view =  view)
            elif interaction.data['custom_id'] == "precedent":
                await interaction.response.edit_message(embed = statistiqueraid.embed_soiree(-1,mec), view =  view)

            elif interaction.data['custom_id'] == "mecanique":
                await interaction.response.edit_message(embed = statistiqueraid.embed_soiree(0,mec), view =  view)


        bouton1 = Button(label="Boss Suivant", style=discord.ButtonStyle.primary, custom_id="suivant")
        bouton1.callback = bouton_callback
        bouton2 = Button(label="Mécaniques", style=discord.ButtonStyle.primary, custom_id="mecanique")
        bouton2.callback = bouton_callback
        bouton3 = Button(label="Boss Précedent", style=discord.ButtonStyle.primary, custom_id="precedent")
        bouton3.callback = bouton_callback
        view = View(timeout = None)
        view.add_item(bouton3)
        view.add_item(bouton2)
        view.add_item(bouton1)
        await interaction.edit_original_response(content = "",embed = embed, view =  view)  


    #Commande Inscription
    @app_commands.command(name="inscription", description="Faire une inscription pour un évènement.")
    @discord.app_commands.guilds(discord.Object(id= ID_GUILD_SERVEUR_INAE))
    async def inscription(self, interaction: discord.Interaction, type_de_sortie: str, description: str, date: str):

        await interaction.response.send_message(embed = inscriptions(type_de_sortie, description, date,0,0))
        message_vote = await interaction.original_response()

        fonction.csv_ajout('csv/varaible.csv', [message_vote.id, type_de_sortie, description, date, [],0,[]])

        print("embed:",message_vote.id)

        await message_vote.add_reaction('✅')
        await message_vote.add_reaction('❌')


    #Commande Excuse
    @app_commands.command(name="excuse", description="Si tu n'as pas d'excuse, laisse le bot t'en trouver une.")
    @discord.app_commands.guilds(discord.Object(id= ID_GUILD_SERVEUR_INAE))
    async def excuse(self, interaction: discord.Interaction):
        ID_CHANNEL_EXCUSE = 1216496548616339647
        messages_liste = []
        channel = interaction.client.get_channel(ID_CHANNEL_EXCUSE)

        async for message in channel.history(limit=100):
            print(f"{message.author.name}: {message.content}")
            messages_liste.append(message.content)

        n_aleatoire = random.randint(0,len(messages_liste))

        await interaction.response.send_message(messages_liste[n_aleatoire])

        
    #Commande Vote
    @app_commands.command(name="vote", description="Crée un vote entre deux possibilités, vive la démocratie !")
    async def vote(self, interaction: discord.Interaction, question: str, reponse1: str, reponse2: str):

        await interaction.response.send_message(embed = vote(question, reponse1, reponse2))
        message_vote = await interaction.original_response()

        fonction.csv_ajout('csv/varaible.csv', [message_vote.id, question, reponse1, reponse2,0,0])

        print("embed:",message_vote.id)

        await message_vote.add_reaction('1️⃣')
        await message_vote.add_reaction('2️⃣')
    

#Fonction pour synchroniser les commandes avec le fichier main
async def setup(bot):
    await bot.add_cog(SlashCommands(bot))




def vote(question, reponse1, reponse2):
    print("Création de l'embed vote.")
    embed_vote = discord.Embed(title = "**Vote:**", description = question, color=0x80ff80)
    embed_vote.add_field(name = "\u200b" , value = "" , inline = False)

    embed_vote.add_field(name = "1️⃣ Team verte" , value = f"{reponse1:<10}" , inline = False)
    embed_vote.add_field(name = "\u200b" , value = "" , inline = False)
    embed_vote.add_field(name = "2️⃣ : Team Bleu" , value = f"{reponse2:<10}" , inline = False)
    embed_vote.add_field(name = "\u200b" , value = "⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜" , inline = False)

    return embed_vote


    
def inscriptions(type_de_sortie , descriptions , date , liste_joueur , nombre ):
    log("- Fonction inscription - Création de l'embed . . .")
    
    embed_inscription = discord.Embed(title = f"**Inscription {type_de_sortie}:ㅤㅤㅤㅤ**", description = descriptions, color=0x80ff80)
    embed_inscription.set_thumbnail(url="https://i.ibb.co/rHyn3Qs/sdfsdf.png")
    embed_inscription.add_field(name = "Date:" , value = date , inline = False)
    embed_inscription.add_field(name = "\u200b" , value = "" , inline = False)

    if "fractale" in type_de_sortie.lower():
        embed_inscription.add_field(name = f"Personne inscrite: 0 / 5" , value = "" , inline = False)
        embed_inscription.add_field(name = "\u200b" , value = "" , inline = False)
        embed_inscription.add_field(name = "\u200b" , value = "⬜ ⬜ ⬜ ⬜ ⬜" , inline = False)

    else:
        embed_inscription.add_field(name = f"Personne inscrite: 0 / 10" , value = "" , inline = False)
        embed_inscription.add_field(name = "\u200b" , value = "" , inline = False)
        embed_inscription.add_field(name = "\u200b" , value = "⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜", inline = False)

    embed_inscription.add_field(name = "\u200b" , value = "" , inline = False)
    

    return embed_inscription

