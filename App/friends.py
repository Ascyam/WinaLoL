import os

import requests
from dotenv import load_dotenv

from .dictionnaire import *

load_dotenv()

RIOT_API_KEY = os.getenv('RIOT_API_KEY')
MAX_SUMMONERS = 30  # Limite de 30 invocateurs

# Liste initiale
friends_list = [
    {'name': 'YoyoRapido', 'tag': 'RAPH',
     'puuid': 'OhuKnL6B5T69Q3d6Z5qRik5f4Hh0H7L4RWbz7aPSHlX5lbkV_y9LLtSM8VsNiSEPJ5wMn5xBO0F_eQ',
     'summoner_encryptedSummonerId': 'lmgfh_Xd-8Fh8OEajlv6Dej-NUodyKIfuyoUNPydtNjUjpQhwIPgj7VAgA'},
    {'name': 'CasusPlay', 'tag': 'K2ARS',
     'puuid': 'djTO3H7lTeOBiGXn3lSh_XVxKpJ4hW4cx85jJ1eu0HLSqzLXcMaMU2CBDPO5uzFuXFtOxVVVkoQV8A',
     'summoner_encryptedSummonerId': 'INIaFtgAT9vcZMagQH7yDyBYFAbBeHaqkqAmKovWkY53EYo'},
    {'name': 'Roi DΣMON', 'tag': 'EUW',
     'puuid': 'qIjjZ-xDBwE2I5wd0bHHKT8NGIgJEPPH64DshwpfRYPFjaZQYhN8QkdJx7L0RoiysnSjtvFbmMifRw',
     'summoner_encryptedSummonerId': '26qFsbaoHShLUUumC1mQxOyO3-q9xs8fLKn9Ny1bZZR2pGg'},
    {'name': 'wao', 'tag': '0000',
     'puuid': 'G8vzsrU5zZ6ADEhKp-v_sRvAVN-gH4tPaCgEBobQ6cezaYxuBaM0Z5RoXFjNgyDgoC1taWyMjiwE0g',
     'summoner_encryptedSummonerId': 'y5yRKN6DfBI6ba3EOPUxfontF0AwQcec-mPqo93QQZmKv0Rh'},
    {'name': 'V4L4KK', 'tag': 'EUW',
     'puuid': 'ZlYej6PXXiuOmyJb59Y68c5qVREEtwQEHAlgqx1btBlp7tJlZ0LnUJ7vNIDpmAVFbcv7VeRXqn1Z4Q',
     'summoner_encryptedSummonerId': 'NjZjIa-tScWhf_BcXwYuFx9emZl98AcUj_IXHFkNfd8NSYkH'},
    {'name': 'Attaque Mortelle', 'tag': '5PAx2',
     'puuid': 'jpPKPdZRpUKwPAtnnkk77O-6XYIzVlcXQbJoME3LLyPe5LkWyE9lJXxavLk93DFVPZBvYweajx5zhg',
     'summoner_encryptedSummonerId': 'Y0WUQmIaTQbuoBhw_upGXGoWgKLhC3Jg324WSwPff7gDuTA'},
    {'name': 'Yąnnøx', 'tag': 'EUW',
     'puuid': '_vE1VE8mzUT-ijrHdKgDdLIGzwNBrKyrdAy-Qk9xDgmEXVrCYPdnjOBWNVy6ktRrVWyBylhWMUSQhw',
     'summoner_encryptedSummonerId': '0pSZrBSoOMozgOb46PAkezKfH_XrUVbQX1ZvM-LssBYtVRK3'}
]


# Getter liste
def get_friends_list():
    return friends_list


# Fonction pour récupérer le PUUID via l'API Riot
def get_summoner_puuid(summoner_name, tag_line):
    try:
        riotAccount_url = f"https://{CONFIG['REGION_Riot']}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag_line}?api_key={RIOT_API_KEY}"
        headers = {
            "X-Riot-Token": RIOT_API_KEY
        }
        response = requests.get(riotAccount_url, headers=headers)

        if response.status_code == 200:
            return response.json()['puuid']
        else:
            print(f"Erreur lors de la récupération de l'ID de l'invocateur {summoner_name}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception lors de la requête pour {summoner_name}: {e}")
        return None


# Fonction pour récupérer l'encryptedSummonerId via l'API Riot
def get_summoner_encryptedSummonerId(puuid):
    try:
        riotAccount_url = f"https://{CONFIG['REGION_Lol']}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={RIOT_API_KEY}"
        headers = {
            "X-Riot-Token": RIOT_API_KEY
        }
        response = requests.get(riotAccount_url, headers=headers)

        if response.status_code == 200:
            return response.json()['id']
        else:
            print(f"Erreur lors de la récupération de l'ID de l'invocateur {puuid}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception lors de la requête pour {puuid}: {e}")
        return None


# Ajout d'un summoner_id et de son PUUID
def add_friend(summoner_name, tag_line):
    # Vérifier si la limite de 30 invocateurs est atteinte
    if len(friends_list) >= MAX_SUMMONERS:
        print(
            f"Tu ne peux pas ajouter plus de {MAX_SUMMONERS} invocateurs. Supprime-en un avant d'en ajouter un autre.")
        return

    # Vérifie que l'ami n'existe pas déjà
    if not any(f['name'] == summoner_name and f['tag'] == tag_line for f in friends_list):
        puuid = get_summoner_puuid(summoner_name, tag_line)
        encryptedSummonerId = get_summoner_encryptedSummonerId(puuid)

        if puuid:
            friends_list.append({'name': summoner_name, 'tag': tag_line, 'puuid': puuid,
                                 'summoner_encryptedSummonerId': encryptedSummonerId})
            print(f"{summoner_name}#{tag_line} a été ajouté avec PUUID {puuid} et ID {encryptedSummonerId}.")
        else:
            print(f"Impossible d'ajouter {summoner_name}#{tag_line} : joueur introuvable.")
    else:
        print(f"{summoner_name}#{tag_line} est déjà dans la liste des amis.")


# Retrait d'un summoner_id
def remove_friend(summoner_name, tag_line):
    friends_list[:] = [f for f in friends_list if f['name'] != summoner_name or f['tag'] != tag_line]
    print(f"{summoner_name}#{tag_line} a été retiré de la liste des amis.")


# Récupérer le rang Elo d'un invocateur
def get_summoner_rank(summoner_encryptedSummonerId):
    try:
        # URL pour récupérer les informations de classement d'un invocateur
        rank_url = f"https://{CONFIG['REGION_Lol']}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_encryptedSummonerId}?api_key={RIOT_API_KEY}"
        headers = {
            "X-Riot-Token": RIOT_API_KEY
        }
        response = requests.get(rank_url, headers=headers)

        if response.status_code == 200:
            ranked_data = response.json()
            # On cherche la queue Solo/Duo pour le classement Elo
            for queue in ranked_data:
                if queue['queueType'] == 'RANKED_SOLO_5x5':
                    return {
                        'tier': queue['tier'],  # Ex: Gold, Silver, Diamond...
                        'rank': queue['rank'],  # Ex: I, II, III, IV
                        'lp': queue['leaguePoints']  # Nombre de points de ligue
                    }
        return None
    except Exception as e:
        print(f"Erreur lors de la récupération du rang pour {summoner_encryptedSummonerId}: {e}")
        return None
