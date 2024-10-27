from flask import Flask, request, jsonify
import bot_instance
import asyncio
import discord

app = Flask(__name__)

    
    


@app.route('/post', methods=['POST'])
def handle_post():

    if request.is_json:

        data = request.get_json()
        print(data)
        if data["type"] == "message":
            bot = bot_instance.bot
            
            channel = bot.get_channel(int(data['channel']))  # ID du channel Discord
            if channel:
                # Envoyer le message au channel Discord de manière asynchrone
                future = asyncio.run_coroutine_threadsafe(
                    channel.send(data.get("message", "Erreur, message non trouvé")), bot.loop
                )
                future.result()
        
        if data["type"] == "embed":
            bot = bot_instance.bot
            
            channel = bot.get_channel(int(data['channel']))  # ID du channel Discord
            if channel:
                
                contenu = data['contenu']
                embed = discord.Embed(title = contenu['titre'], description =contenu['desc'], color=0x80ff80)
                #embed.set_thumbnail(url="https://i.ibb.co/rHyn3Qs/sdfsdf.png")
                embed.add_field(name = "" , value = contenu['texte'] , inline = False)
                
                # Envoyer le message au channel Discord de manière asynchrone
                future = asyncio.run_coroutine_threadsafe(
                    channel.send(embed = embed), bot.loop
                )
                future.result()


        return jsonify({"message": "Données reçues avec succès", "data": data}), 200
    else:
        return jsonify({"message": "La requête doit contenir du JSON"}), 400



@app.route('/get/<string:forname>', methods=['GET'])
def handle_get(forname):
    if forname == "test":
        return {"Test" : "Prout"}
    
    if forname == "channel":
        return {"channel" : {"Salle du spam" :1173394070060666980, "Bot" :1158844051550904421}}

    return jsonify({"message": f"enpoint : {forname} non reconnu :( :("}), 400


    


def run_api():
    app.run(host='0.0.0.0', port=5000, debug= False)
