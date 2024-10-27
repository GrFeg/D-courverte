#https://dps.report/WYgm-20240828-161513_golem

import requests
import pprint
import json
from bs4 import BeautifulSoup


requete = requests.get("https://dps.report/1MvY-20240907-181942_golem")
chemin = "debug_rota.json"
page = requete.content
soup = BeautifulSoup(page, features="html.parser")
soup = str(soup)
soup = soup[soup.index("var _logData = ") + 15:]
soup = soup[:soup.index(";")]

soup_json = json.loads(soup)

with open('debug_rota.json', 'w', encoding='utf-8') as fichier:
        json.dump(soup_json, fichier, indent=4, ensure_ascii=False)

rotation = soup_json["players"][0]["details"]["rotation"]

def ouvrir_fichier_infos_skill_id():

    with open('info_skill_id.json', 'r', encoding='utf-8') as fichier:
        contenu_json_info_skill = json.load(fichier)
    
    print("Fichier info_skill_id.json ouvert")
    
    return contenu_json_info_skill

def reecrire_fichier_infos_skill_id(contenu_json_info_skill: json):
    with open('info_skill_id.json', 'w', encoding='utf-8') as fichier:
        json.dump(contenu_json_info_skill, fichier, indent=4, ensure_ascii=False)
    
    print("Fichier info_skill_id.json actualisé")
        
def recherche_skills_api_gw(rotation: list[list]):
    
    print("Actualisation du fichier JSON infos sur les skills . . .")
    
    contenu_json_info_skill = ouvrir_fichier_infos_skill_id()
    
    rotation = rotation[0]
    for competence in rotation:
        
        id_competence = str(competence[1])
        
        if id_competence in contenu_json_info_skill:
            print(f"Skill {contenu_json_info_skill[id_competence]["name"]} trouvé")
        else:
            print(f"ID: {id_competence} non trouvé, recherche dans l'API GW2")
            requete_api_id_skill = requests.get(f"https://api.guildwars2.com/v2/skills?ids={competence[1]},5809&lang=fr")
            
            if requete_api_id_skill.status_code == 200:
                contenu_json_info_skill[id_competence] = requete_api_id_skill.json()[0]
                print(f"Skill {contenu_json_info_skill[id_competence]["name"]} Ajouté")
            else:
                print(f"Skill ID: {id_competence} non reconnu par l'API GW2")
                contenu_json_info_skill[id_competence] = {"name" : "Inconnu"}
        print("")
    
    reecrire_fichier_infos_skill_id(contenu_json_info_skill)

def comptage_occurence_skill_dans_rota(rotation: list[list]):
    
    contenu_json_info_skill = ouvrir_fichier_infos_skill_id()
    
    dico_nbr_occurence_skills = {}
    rotation_0 = rotation[0]
    for competence in rotation_0:
        id_competence = str(competence[1])
        
        if not id_competence in contenu_json_info_skill:
            print("Compétence Inconnu rencontré . . . Début de la demande à l'API GW")
            recherche_skills_api_gw(rotation)
            
            contenu_json_info_skill = ouvrir_fichier_infos_skill_id()
        
        nom_competence = contenu_json_info_skill[id_competence]["name"]
        
        if nom_competence not in dico_nbr_occurence_skills:
            dico_nbr_occurence_skills[nom_competence] = 1
        else:
            dico_nbr_occurence_skills[nom_competence] += 1
    
    pprint.pprint(sorted(dico_nbr_occurence_skills.items(), key=lambda item: item[1], reverse=True))
    
        
def temps_perdu_spell_cancel(rotation):
     
    contenu_json_info_skill = ouvrir_fichier_infos_skill_id()
    
    temps_cast_interrupted_total = 0
    temps_cast_interrupted_auto_attack = 0
    rotation_0 = rotation[0]
    for competence in rotation_0:
        id_competence = str(competence[1])
        temps_cast = competence[2]
        type_cast = competence[3]
        
        if not id_competence in contenu_json_info_skill:
            print("Compétence Inconnu rencontré . . . Début de la demande à l'API GW")
            recherche_skills_api_gw(rotation)
            
            contenu_json_info_skill = ouvrir_fichier_infos_skill_id()
        
        
        if "slot" in contenu_json_info_skill[id_competence]:
            slot = contenu_json_info_skill[id_competence]["slot"]
        else:
            slot = None
        
        if type_cast == 2: #Cast Interrupted pour dps.report
            temps_cast_interrupted_total += temps_cast
            
            if slot == "Weapon_1":
                temps_cast_interrupted_auto_attack += temps_cast
    
    print(f"Temps perdu: {temps_cast_interrupted_total} ms")
    print(f"Dont {temps_cast_interrupted_auto_attack} ms d'auto attack")


temps_perdu_spell_cancel(rotation)










