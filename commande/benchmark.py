import requests
import json
from bs4 import BeautifulSoup
import discord
from config_logger import logger, SUCCESS

def recup_donnee_benchmark():
    LIEN_BENCHMARK_SNOW = 'https://snowcrows.com/benchmarks'

    requete = requests.get(LIEN_BENCHMARK_SNOW)

    page = requete.content
    soup = BeautifulSoup(page, features="html.parser")

    build_blocks = soup.find_all('div', class_= "flex-grow")

    dico_benchmark = {}

    for i, block in enumerate(build_blocks):
        
        #Extraction du nom du build & lien (incomplet)
        build_name_element = block.find('a', class_="font-medium line-clamp-1")
        build_name = build_name_element.text.strip() if build_name_element else "Nom non trouvé"
        build_link = build_name_element.get('href') if build_name_element else "Lien non trouvé"
        full_build_link = "https://snowcrows.com" + build_link
        
        #Extraction du DPS
        dps_element = block.find_next('div', class_="text-xs mt-1 text-neutral-300 px-2")
        dps_value = dps_element.text.strip() if dps_element else "DPS non trouvé"
        
        dico_benchmark[i] = {"nom_build" : build_name,
                            "lien_build": full_build_link,
                            "dps_build" : dps_value}
    
    return dico_benchmark

def embed_benchmark():
    
    dico_benchmark = recup_donnee_benchmark()
    
    embed_benchmark = discord.Embed(title="Classement des meilleurs DPS :", description= "Que pourrions nous faire sans eux ? (le neuvième est incroyable)", color=discord.Color.blue())
    embed_benchmark.set_thumbnail(url="https://i.ibb.co/rHyn3Qs/sdfsdf.png")
    embed_benchmark.add_field(name = "" , value = "\u200b" , inline = False)

    fail = 0
    valeur = ""
    premier = False
    for nbr, classe in enumerate(dico_benchmark.values()):
        
        if not classe['nom_build'] == "Nom non trouvé":
            if premier:
                valeur += f"ㅤ- [{classe['nom_build']}]({classe['lien_build']}): {classe['dps_build']} \n"
            else:
                premier = True
        else:
            fail -= 1
        
        if nbr + fail == 10:
            embed_benchmark.add_field(name = "Top 10 des builds: " , value = valeur , inline = False)
            break
        
    embed_benchmark.add_field(name = "\u200b" , value = "" , inline = False)
    embed_benchmark.set_footer(text="Donnée provennant de Snowcrows: https://snowcrows.com/", icon_url="https://assets.snowcrows.com/images/logo/logo.png")

    logger.log(SUCCESS, "Embed Benchmark crée")

    return embed_benchmark
