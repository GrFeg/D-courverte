import discord
#import tombola
import statistiqueraid 
import inscription
import commande
from fonction import log
import fonction
from discord.ext import commands
from discord import app_commands
import json
import os
from pathlib import Path

'''
Fichier où le Bot discord est initialisé

'''


if os.path.isfile( Path('config.json')):
    #Récupération des configurations du bot
    with open('config.json') as config_file:
        config = json.load(config_file)

    TOKEN = config['TOKEN']
    ID_JOUEUR_PIZZABLEU = config['ID_JOUEUR_PIZZABLEU']
    ID_JOUEUR_CLOUD = config['ID_JOUEUR_CLOUD']
    ID_BOT = config['ID_BOT']
    ID_BOT_MIOUNE = config['ID_BOT_MIOUNE']
    ID_GUILD_SERVEUR_INAE = config['ID_GUILD_SERVEUR_INAE']

    CHANNEL_ID_LOGS = 892509041140588581 
    CHEMIN_HISTO_LOGS = 'csv/histo_logs.csv'

else:
    log("Fichier config.json introuvable", 3)

messages_liste = []


#Definir la class MonBot
class MonBot(commands.Bot, discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):

        #Pour récuperer la commande dans le fichier "commande"
        try:
            await self.load_extension("commande")
        except:
            log('Fichier commande.py introuvable !', 2)
        try:
            await self.load_extension("inscription")
        except:
            log('Fichier inscription.py introuvable !', 2)

        #Synchronise les commandes avec touts les serveurs discord
        await self.tree.sync()
        #Synchronise les commandes avec le serveur INAE (plus rapide)
        await self.tree.sync(guild=discord.Object(id= ID_GUILD_SERVEUR_INAE))

bot = MonBot()

#Calcule le % entre deux nombres de votes
def calcul_pourcentage(csv_embed: list):
    """
    Fonction utilisé pour la gestion des votes de la commande /vote
    Récupère le nombre de vote pour chaque réponse et retourne le pourcentage de personnes ayant voté pour chaque réponse
    """

    vote_1 = int(csv_embed[4])
    vote_2 = int(csv_embed[5])

    if vote_1 == 0 or vote_2 == 0:

        if vote_1 == 0 and vote_2 == 0:
            vote_1p = 0
            vote_2p = 0

        elif vote_1 == 0:
            vote_1p = 0
            vote_2p = 100

        else:
            vote_1p = 100
            vote_2p = 0

    else:
        vote_1p = round(vote_1 / (vote_1 + vote_2) * 100)
        vote_2p = round(vote_2 / (vote_1 + vote_2) * 100)
    
    return vote_1p, vote_2p

#Recherche si l'id d'un embed existe
def recherche_embed(csv_embed, embed_id):
    '''
    Recherche si l'id d'un embed est dans la variable d'un csv sous forme de liste.
    Si oui renvoit la ligne, si non renvoit -1
    '''
    
    for i, e in enumerate(csv_embed):
        if str(embed_id) in e:
            return i
    return -1

#Récupere les messages dans un canal
async def recuperation_message(CHANNEL_ID_LOGS, nbr_messages):
    '''
    Fonction qui permet de récuperer n nombres de messages dans un canal donné.
    '''

    channel = bot.get_channel(CHANNEL_ID_LOGS)
    global messages_liste
    messages_liste = []

    if channel:
        async for message in channel.history( limit= nbr_messages ):

            messages_liste.append( message.content.split('\n') )

        fonction.csv_actu( CHEMIN_HISTO_LOGS, messages_liste )
        log("Messages logs recupéré")  
    else:
        log('Canal non trouvé, vérifier "CHANNEL_ID_LOGS" ', 3)

#Detecte quand le bot a démarré
@bot.event
async def on_ready():

    await recuperation_message(CHANNEL_ID_LOGS, 10)
    log(f'Le {bot.user.name} est connecté')


#Detecte un message envoyé
@bot.event
async def on_message(message : discord.Message):

    #Les différents fichiers où les messages sont regardé 
    await statistiqueraid.stats_message(message)
    #await shoptitans.shop_message(message)
    #await tombola.tombola_message(message)
    
    #Définition des variables
    channel_nom = message.channel.name
    joueur = message.author.name
    id_joueur = message.author.id
    message_contenu = message.content

    log(f"{message.guild.name} - Message de: {joueur}:  {message_contenu} dans: {channel_nom}",3)

    #Changer le pseudo de mioune
    if "Mioune"  in message_contenu:
        guild = message.guild
        member = guild.get_member( ID_BOT_MIOUNE ) #Id de mioune
        await member.edit(nick= message_contenu) #Change le surnom
        await message.delete() #Efface le message

        log(f"Pseudo de Mioune changé pour: {message_contenu}")

    #Nils !
    if message_contenu =="Ah bah c'est bien Nils!":
        await message.channel.send("Ah bah oui c'est super même !")

    #Cloud !
    if id_joueur == ID_JOUEUR_CLOUD:
        await message.add_reaction('💩')



#Définission de l'embed vote
def embed_vote(ligne_csv: list):

    #Calculer les % des votes
    pourcentage = [0,0]
    pourcentage = calcul_pourcentage(ligne_csv)
    espace = "ㅤㅤㅤㅤㅤ" #Ligne conserver pour avoir le caractère " " ^^
    field1 = f"({pourcentage[0]}%)"
    field2 = f"({pourcentage[1]}%)"

    #Faire la ligne de carré en fonction du %
    note = ""
    for i in range(10):
        if pourcentage[0] == 0 and pourcentage[1] == 0:
            note = "⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜ ⬜"
            break
        if i >= pourcentage[0]/10:
            note = note + " " + "🟦"
        else:
            note = note + " " + "🟩"


    #Définition de l'embed
    embed_vote = discord.Embed(title="Vote:", description= "\u200b", color=discord.Color.blue())
    embed_vote.add_field(name = "Question :" , value = ligne_csv[1] , inline = False)
    embed_vote.add_field(name = "\u200b" , value = "" , inline = False)

    embed_vote.add_field(name = "Résultat :" , value = "" , inline = False)
    embed_vote.add_field(name = f"🟩 | {ligne_csv[2]} : " , value = f"ㅤ {ligne_csv[4]} votes. {field1}" , inline = False)
    embed_vote.add_field(name = "\u200b" , value = "" , inline = False)
    embed_vote.add_field(name = f"🟦 | {ligne_csv[3]} : " , value = f"ㅤ {ligne_csv[5]} votes. {field2}" , inline = False)
    embed_vote.add_field(name = "\u200b" , value = "" , inline = False)
    embed_vote.add_field(name = "------------------------------------" , value = "" , inline = False)
    embed_vote.add_field(name = "" , value = note , inline = False)
        
    return embed_vote

#Detecte lorsqu'une reaction est ajouté
@bot.event
async def on_raw_reaction_add(payload):

    channel = await bot.fetch_channel(payload.channel_id)  # Récupère l'objet Channel
    message = await channel.fetch_message(payload.message_id)  # Récupère l'objet Message
    emoji = payload.emoji
   
    if payload.user_id == ID_BOT:
        return
    if emoji.name  == "🟩" or emoji.name  == "🟦":
        csv_embed = fonction.csv_recup('csv/varaible.csv')
        n_embed = recherche_embed(csv_embed,message.id)
    else:
        return


#Commande vote, actualisation de l'embed à chaque réaction
    log('Réaction détecté, test si elle est sur un embed du bot . . .')

    if int(csv_embed[n_embed][0]) == message.id and (emoji.name  == "🟦" or emoji.name  == "🟩") and n_embed != -1:
        log("prout")
        if emoji.name == "🟩":
            csv_embed[n_embed][4] = 1 + int(csv_embed[n_embed][4])
            log(f"Embed: {csv_embed[n_embed][0]}, incrémentation de 1 sur vote n°2 ({csv_embed[n_embed][4]})")
        else:
            csv_embed[n_embed][5] = 1 + int(csv_embed[n_embed][5])
            log(f"Embed: {csv_embed[n_embed][0]}, incrémentation de 1 sur vote n°2 ({csv_embed[n_embed][5]})")

        embed = embed_vote(csv_embed[n_embed])

        await message.edit(embed=embed)

        fonction.csv_actu('csv/varaible.csv',csv_embed)
    

#Detecte lorsqu'une reaction est enlevé
@bot.event
async def on_raw_reaction_remove(payload):
    channel = await bot.fetch_channel(payload.channel_id)  # Récupère l'objet Channel
    message = await channel.fetch_message(payload.message_id)  # Récupère l'objet Message
    emoji = payload.emoji

#Vote avec les embed
    #Récupère le fichier csv et chercher si la réaction mise et sur un embed de vote.
    if emoji.name  == "🟦" or emoji.name  == "🟩":
        csv_embed = fonction.csv_recup('csv/varaible.csv')
        n_embed = recherche_embed(csv_embed,message.id)
    else:
        return

    #Test si la réaction est sur un embed de vote
    if int(csv_embed[n_embed][0]) == message.id and (emoji.name  == "🟦" or emoji.name  == "🟩") and n_embed != -1:
        #Mettre à jour les votes en fonction de la réaction mise
        if emoji.name == "🟩":
            csv_embed[n_embed][4] =  int(csv_embed[n_embed][4]) - 1
            log(f"Embed: {csv_embed[n_embed][0]}, incrémentation de -1 sur vote n°1 ({csv_embed[n_embed][4]})")
        else:
            csv_embed[n_embed][5] =  int(csv_embed[n_embed][5]) - 1
            log(f"Embed: {csv_embed[n_embed][0]}, incrémentation de -1 sur vote n°2 ({csv_embed[n_embed][5]})")
        
        embed = embed_vote(csv_embed[n_embed])
        await message.edit(embed=embed)

        #Actualiser le csv avec les nouveaux votes
        fonction.csv_actu('csv/varaible.csv',csv_embed)


bot.run(TOKEN)
