import discord
from discord.ext import commands
from discord import app_commands
from fonction import log
import fonction
import commande.recap_raid.statistiqueraid as statistiqueraid
from commande.benchmark import embed_benchmark
import random
from discord.ui import Button, View
import os
import json


'''
Fichier ou va se trouver le nom de toutes les commandes du bot Discord


'''


chemin_fichier_config = '_donnee/config.json'
chemin_fichier_shonen = '_donnee/shonen.json'

if os.path.isfile(chemin_fichier_config):
    #Récupération des configurations du bot
    with open(chemin_fichier_config) as config_file:
        config = json.load(config_file)

    with open(chemin_fichier_shonen, encoding='utf-8') as config_file:
        shonen = json.load(config_file)
    
    shonen = shonen["phrase"]
    
    ID_GUILD_SERVEUR_INAE = config['ID_GUILD_SERVEUR_INAE']

else:
    log("Fichier config.json introuvable", 3)


message_ids = {}

#Bouton
class Bouton(View):
    
    def __init__(self, label, custom_id):
        super().__init__(timeout=None)
        button = Button(label=label, style=discord.ButtonStyle.primary, custom_id=custom_id)
        button.callback = self.button_callback
        self.add_item(button)
    
    async def button_callback(self, interaction: discord.Interaction):
        print("Bip")

class BoutonSoiree(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.mec = False 

        self.bouton_suivant = Button(label="Boss suivant", style=discord.ButtonStyle.primary, custom_id="suivant")
        self.bouton_mecanique = Button(label="Mécaniques", style=discord.ButtonStyle.primary, custom_id="mecanique")
        self.bouton_precedent = Button(label="Boss précédent", style=discord.ButtonStyle.primary, custom_id="precedent")

        self.add_item(self.bouton_precedent)
        self.add_item(self.bouton_mecanique)
        self.add_item(self.bouton_suivant)

        self.bouton_suivant.callback = self.button_callback
        self.bouton_mecanique.callback = self.button_callback
        self.bouton_precedent.callback = self.button_callback

    async def button_callback(self, interaction: discord.Interaction):
        if interaction.data['custom_id'] == "mecanique":
            self.mec = not self.mec
            new_label = "Rôle" if self.mec else "Mécaniques"
            self.bouton_mecanique.label = new_label

        if interaction.data['custom_id'] == "suivant":
            await interaction.response.edit_message(embed=statistiqueraid.embed_soiree(1, self.mec), view=self)
        elif interaction.data['custom_id'] == "precedent":
            await interaction.response.edit_message(embed=statistiqueraid.embed_soiree(-1, self.mec), view=self)
        elif interaction.data['custom_id'] == "mecanique":
            await interaction.response.edit_message(embed=statistiqueraid.embed_soiree(0, self.mec), view=self)
      
        

#Definition de la   class   commande
class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bouton", description="Prouuuut")
    @discord.app_commands.guilds(discord.Object(id= ID_GUILD_SERVEUR_INAE))
    async def bouton(self, interaction: discord.Interaction):
        view1 = Bouton("Bouton 1", "button_1")
        view2 = Bouton("Bouton 2", "button_2")
        
        combined_view = View(timeout=None)
        combined_view.add_item(view1.children[0])
        combined_view.add_item(view2.children[0])
        
        await interaction.response.send_message("Arriva", view = combined_view ) 

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
            await interaction.response.send_message(embed = embed, file=file, ephemeral=False)
        else:
           await interaction.response.send_message(embed= embed)
    


    #Commande soiree
    @app_commands.command(name="soiree", description="Renvoit les statistiques de la soirée, boss par boss")
    @discord.app_commands.guilds(discord.Object(id= ID_GUILD_SERVEUR_INAE))
    async def soiree(self, interaction: discord.Interaction):
        await interaction.response.send_message("J'utilise mon neuronne pour réfléchir niaaaaaaaaa")
        embed = statistiqueraid.embed_soiree(0, False)
   
        view = BoutonSoiree()

        await interaction.edit_original_response(content = "",embed = embed, view =  view)  

    #Commande benchamrk
    @app_commands.command(name="benchmark", description="Affiche le Top 10 des DPS")
    @discord.app_commands.guilds(discord.Object(id= ID_GUILD_SERVEUR_INAE))
    async def benchmark(self, interaction: discord.Interaction):
        await interaction.response.send_message("J'utilise mon neuronne pour réfléchir niaaaaaaaaa")
        embed = embed_benchmark()
        await interaction.edit_original_response(content = "",embed = embed)
        
        
    #Commande Inscription
    @app_commands.command(name="inscription", description="Faire une inscription pour un évènement.")
    @discord.app_commands.guilds(discord.Object(id= ID_GUILD_SERVEUR_INAE))
    async def inscription(self, interaction: discord.Interaction, type_de_sortie: str, description: str, date: str):

        await interaction.response.send_message(embed = inscriptions(type_de_sortie, description, date,0,0))
        message_vote = await interaction.original_response()


        fonction.csv_ajout('csv/varaible.csv', [message_vote.id,0, type_de_sortie, description, date, [],0,[],0,0])

        print("embed:",message_vote.id)

        await message_vote.add_reaction('✅')
        await message_vote.add_reaction('❌')
    
    #Commande Inscription hebdo
    @app_commands.command(name="inscription_hebdo", description="Faire une inscription pour la semaine.")
    @discord.app_commands.guilds(discord.Object(id= ID_GUILD_SERVEUR_INAE))
    async def inscription_hebdo(self, interaction: discord.Interaction, date: str):

        await interaction.response.send_message(embed = inscriptions_hebdo(date))
        message_vote = await interaction.original_response()


        fonction.csv_ajout('csv/varaible.csv', [message_vote.id,1, 0, 0, date, [[],[],[],[],[],[],[]], [0,0,0,0,0,0,0],[],0,0])

        print("embed:",message_vote.id)

        await message_vote.add_reaction('🇱')
        await message_vote.add_reaction('🇲')
        await message_vote.add_reaction('Ⓜ️')
        await message_vote.add_reaction('🇯')
        await message_vote.add_reaction('🇻')
        await message_vote.add_reaction('🇸')
        await message_vote.add_reaction('🇩')


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

        fonction.csv_ajout('csv/varaible.csv', [message_vote.id, question, reponse1, reponse2,0,0,0])

        print("embed:",message_vote.id)

        await message_vote.add_reaction('🟩')
        await message_vote.add_reaction('🟦')
    
    #Commande DPS
    @app_commands.command(name="dps", description="Voir son DPS sur un Boss précis !")
    @discord.app_commands.guilds(discord.Object(id= ID_GUILD_SERVEUR_INAE))
    async def dps(self, interaction: discord.Interaction, boss: str):

        user_id = interaction.user.id
        graphique, embed = statistiqueraid.embed_dps(user_id, boss)
        if graphique != -1:
            await interaction.response.send_message(embed = embed, file= graphique, ephemeral=False)
        else:
           await interaction.response.send_message(embed=embed)
    
    #Commande Espoir
    @app_commands.command(name="espoir", description="Si tu es triste, tape cette commande, elle te donnera le courage nécessaire")
    @discord.app_commands.guilds(discord.Object(id= ID_GUILD_SERVEUR_INAE))
    async def espoir(self, interaction: discord.Interaction):
        await interaction.response.send_message(random.choice(shonen))
    





#Fonction pour synchroniser les commandes avec le fichier main
async def setup(bot):
    await bot.add_cog(SlashCommands(bot))




def vote(question, reponse1, reponse2):
    print("Création de l'embed vote.")
    embed_vote = discord.Embed(title = "**Vote:**", description = question, color=0x80ff80)
    embed_vote.add_field(name = "\u200b" , value = "" , inline = False)

    embed_vote.add_field(name = "🟩 | Team verte" , value = f"{reponse1:<10}" , inline = False)
    embed_vote.add_field(name = "\u200b" , value = "" , inline = False)
    embed_vote.add_field(name = "🟦 | Team Bleu" , value = f"{reponse2:<10}" , inline = False)
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

def inscriptions_hebdo(date):
    log("- Fonction inscriptions_hebdo - Création de l'embed . . .")
    
    embed = discord.Embed(title = f"**Inscription Hebdomadaire:ㅤㅤㅤㅤ**", description ="", color=0x80ff80)
    embed.set_thumbnail(url="https://i.ibb.co/rHyn3Qs/sdfsdf.png")
    embed.add_field(name = "" , value = "Le but est de savoir qui est là quelle jour et en fonction on avise quand on sort !" , inline = False)
    embed.add_field(name = "Date:" , value = date , inline = False)
    embed.add_field(name = "\u200b" , value = "" , inline = False)


    jour_semaine = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']
    for jour in jour_semaine:
        embed.add_field(name = f"{jour}:" , value =  "ㅤㅤNombre inscris: 0", inline = False)

    embed.add_field(name = "\u200b" , value = "" , inline = False)

    return embed
