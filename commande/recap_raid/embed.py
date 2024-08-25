import discord

#Embed chargé lorsqu'il y a une erreur
def embed_erreur():
    
    #Définir les propriété de l'embed
    embed = discord.Embed( title = f"** Upsi . . . **",
                           description = "", 
                           color= discord.Colour.red()
                         )
    embed.set_thumbnail(url="https://i.ibb.co/rHyn3Qs/sdfsdf.png") #Image en haut à droite

    #Partie Global de l'embed
    embed.add_field(name = ". . ." , value = "Il y a eu un problème :(" , inline = False)

    return embed
