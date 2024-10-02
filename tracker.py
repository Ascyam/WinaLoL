import discord
import requests
import asyncio
import os
import time
from App.WinaLoL.betting import close_betting_for_summoner, currently_ingame
from dotenv import load_dotenv
from App.friends import *
from App.interactions import *
from App.WinaLoL.betting import *
from App.front import *

load_dotenv()  # Charger les variables d'environnement

TOKEN = os.getenv('TOKEN')
RIOT_API_KEY = os.getenv('RIOT_API_KEY')

# Vérifier si l'ami est en jeu
def is_friend_in_game(riot_puuid):
    try:
        game_url = f"https://{CONFIG['REGION_Lol']}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{riot_puuid}?api_key={RIOT_API_KEY}"
        headers = {
            "X-Riot-Token": RIOT_API_KEY
        }
        response = requests.get(game_url, headers=headers)
        
        if response.status_code == 200:
            return True  # L'ami est en jeu
        elif response.status_code == 404:
            return False  # L'ami n'est pas en jeu
        else:
            print(f"Erreur lors de la vérification de l'état de jeu : {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Erreur lors de la requête à Riot API : {e}")
        return None

def get_match_history(riot_puuid):
    match_history_url = f"https://{CONFIG['REGION_Riot']}.api.riotgames.com/lol/match/v5/matches/by-puuid/{riot_puuid}/ids?api_key={RIOT_API_KEY}"
    
    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }
    response = requests.get(match_history_url, headers=headers)

    if response.status_code == 200:
        return response.json()  # Retourne la liste des IDs de match
    return None

def get_game_result(riot_puuid, match_id):
    match_url = f"https://{CONFIG['REGION_Riot']}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={RIOT_API_KEY}"
    
    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }
    match_response = requests.get(match_url, headers=headers)
    
    if match_response.status_code == 200:
        match_data = match_response.json()
        participant_info = next(
            (p for p in match_data['info']['participants'] if p['puuid'] == riot_puuid),
            None
        )
        if participant_info:
            return "win" if participant_info['win'] else "lose"
    return None

def get_first_20_games(riot_puuid):
    match_ids = get_match_history(riot_puuid)

    if match_ids:
        results = []
        for match_id in match_ids[:20]:  # Limiter à 20 matchs
            result = get_game_result(riot_puuid, match_id)
            results.append(result)
        return results
    return None

def calculate_winrate(puuid):
    results = get_first_20_games(puuid)

    if results:
        wins = results.count("win")  # Compte les victoires
        winrate = wins / len(results)  # Calcul du winrate
        return winrate
    return 0  # Retourne 0 si aucun résultat n'est disponible

def get_game_info(user_puuid):
    # URL pour obtenir les infos du match via l'API Spectator de Riot
    game_url = f"https://{CONFIG['REGION_Lol']}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{user_puuid}?api_key={RIOT_API_KEY}"

    try:
        response = requests.get(game_url)
        if response.status_code != 200:
            return f"Erreur : Impossible de récupérer les informations du match. Code: {response.status_code}"
        
        game_data = response.json()

        # Récupération du mode de jeu
        game_mode = game_data.get('gameMode', 'Inconnu')
        game_type = game_data.get('gameType', 'Inconnu')
        game_id = game_data.get('gameId', 'Inconnu')

        # Récupération de la liste des joueurs et des champions choisis
        players = game_data.get('participants', [])
        draft = []

        for player in players:
            summoner_name = player['riotId']
            champion_id = player['championId']
            champion_name = get_champion_name_from_api(champion_id)  
            draft.append(f"🔹 {summoner_name} - **{champion_name}**")

        # Création du message joli pour le mode de jeu et la draft
        draft_message = (
            f"🎮 **Mode de jeu :** {game_mode} ({game_type})\n\n"
            f"🌟 **Composition des équipes :**\n\n"
            f"{' - '.join(draft[:5])} (Équipe 1)\n\n"
            f"{' - '.join(draft[5:])} (Équipe 2)"
        )
        return draft_message, game_id

    except Exception as e:
        return f"Erreur lors de la récupération des informations du match : {e}"
    
def get_champion_name(champion_id):
    champions = {
        266: "Aatrox",
        103: "Ahri",
        84: "Akali",
        166: "Akshan",
        12: "Alistar",
        32: "Amumu",
        34: "Anivia",
        1: "Annie",
        523: "Aphelios",
        22: "Ashe",
        136: "Aurelion Sol",
        268: "Azir",
        432: "Bard",
        200: "Bel'Veth",
        53: "Blitzcrank",
        63: "Brand",
        201: "Braum",
        51: "Caitlyn",
        164: "Camille",
        69: "Cassiopeia",
        31: "Cho'Gath",
        42: "Corki",
        122: "Darius",
        131: "Diana",
        119: "Draven",
        36: "Dr. Mundo",
        245: "Ekko",
        60: "Elise",
        28: "Evelynn",
        81: "Ezreal",
        9: "Fiddlesticks",
        114: "Fiora",
        105: "Fizz",
        3: "Galio",
        41: "Gangplank",
        86: "Garen",
        150: "Gnar",
        79: "Gragas",
        104: "Graves",
        887: "Gwen",
        120: "Hecarim",
        74: "Heimerdinger",
        420: "Illaoi",
        39: "Irelia",
        427: "Ivern",
        40: "Janna",
        59: "Jarvan IV",
        24: "Jax",
        126: "Jayce",
        202: "Jhin",
        222: "Jinx",
        145: "Kai'Sa",
        429: "Kalista",
        43: "Karma",
        30: "Karthus",
        38: "Kassadin",
        55: "Katarina",
        10: "Kayle",
        141: "Kayn",
        85: "Kennen",
        121: "Kha'Zix",
        203: "Kindred",
        240: "Kled",
        96: "Kog'Maw",
        7: "LeBlanc",
        64: "Lee Sin",
        89: "Leona",
        876: "Lillia",
        127: "Lissandra",
        236: "Lucian",
        117: "Lulu",
        99: "Lux",
        54: "Malphite",
        90: "Malzahar",
        57: "Maokai",
        11: "Master Yi",
        21: "Miss Fortune",
        62: "Wukong",
        82: "Mordekaiser",
        25: "Morgana",
        267: "Nami",
        75: "Nasus",
        111: "Nautilus",
        518: "Neeko",
        76: "Nidalee",
        56: "Nocturne",
        20: "Nunu & Willump",
        2: "Olaf",
        61: "Orianna",
        516: "Ornn",
        80: "Pantheon",
        78: "Poppy",
        555: "Pyke",
        246: "Qiyana",
        133: "Quinn",
        497: "Rakan",
        33: "Rammus",
        421: "Rek'Sai",
        526: "Rell",
        58: "Renekton",
        107: "Rengar",
        92: "Riven",
        68: "Rumble",
        13: "Ryze",
        360: "Samira",
        113: "Sejuani",
        235: "Senna",
        147: "Seraphine",
        875: "Sett",
        35: "Shaco",
        98: "Shen",
        102: "Shyvana",
        27: "Singed",
        14: "Sion",
        15: "Sivir",
        72: "Skarner",
        37: "Sona",
        16: "Soraka",
        50: "Swain",
        517: "Sylas",
        134: "Syndra",
        223: "Tahm Kench",
        163: "Taliyah",
        91: "Talon",
        44: "Taric",
        17: "Teemo",
        412: "Thresh",
        18: "Tristana",
        48: "Trundle",
        23: "Tryndamere",
        4: "Twisted Fate",
        29: "Twitch",
        77: "Udyr",
        6: "Urgot",
        110: "Varus",
        67: "Vayne",
        45: "Veigar",
        161: "Vel'Koz",
        711: "Vex",
        254: "Vi",
        234: "Viego",
        112: "Viktor",
        8: "Vladimir",
        106: "Volibear",
        19: "Warwick",
        498: "Xayah",
        101: "Xerath",
        5: "Xin Zhao",
        157: "Yasuo",
        777: "Yone",
        83: "Yorick",
        350: "Yuumi",
        154: "Zac",
        238: "Zed",
        115: "Ziggs",
        26: "Zilean",
        142: "Zoe",
        143: "Zyra"
    }

    # Retourne le nom du champion correspondant à l'ID
    return champions.get(champion_id, "Champion Inconnu")

def get_champion_name_from_api(champion_id):
    url = "https://ddragon.leagueoflegends.com/cdn/13.19.1/data/en_US/champion.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        champions_data = response.json()['data']
        
        for champion in champions_data.values():
            if champion['key'] == str(champion_id):
                return champion['name']
    
    return "Champion Unknown"

# Fonction qui surveille les amis et envoie une notification sur Discord
async def notify_if_friends_in_game():
    await bot.wait_until_ready()
    channel = discord.utils.get(bot.get_all_channels(), name=CONFIG['CHANNEL'])  # Le nom du channel Discord
    previously_in_game = {}  # Dictionnaire pour suivre l'état des amis
    bet_timers = {}  # Dictionnaire pour suivre le temps des paris pour chaque ami
    
    gambler_ping_message = await ping_gambler_role(channel)

    while not bot.is_closed():
        friends_list = get_friends_list()  # Récupérer la liste des amis à chaque boucle
        
        for friend in friends_list:
            summoner_name = friend['name']
            puuid = friend['puuid']
            
            in_game = is_friend_in_game(puuid)
                
            # Si l'ami est en jeu et qu'il ne l'était pas auparavant, on envoie une notification
            if in_game and not previously_in_game.get(summoner_name, False):
                game_info_message, game_id = get_game_info(puuid)

                # Appel à la fonction pour afficher le message d'annonce du lancement de partie
                await afficher_lancement_partie(channel, summoner_name, summoner_ratings, gambler_ping_message, game_info_message, bot)

                # Démarrer un chronomètre pour fermer les paris après 3 minutes
                bet_timers[summoner_name] = time.time()
                # Le summoner est en jeu    
                currently_ingame.append({
                        'summoner_name': summoner_name,
                        'game_id': game_id
                    })
                 # Initialise les données associées au joueur
                add_summoner_to_active_bets(summoner_name)

            if in_game and summoner_name in bet_timers:
                elapsed_time = time.time() - bet_timers[summoner_name]

                if elapsed_time > 180:  # 180 secondes = 3 minutes
                    close_betting_for_summoner(summoner_name)  # Fermer les paris pour cet ami
                    await channel.send(f"⏳ Les paris pour {summoner_name} sont désormais fermés.")
                    del bet_timers[summoner_name]

            # Si l'ami vient de finir sa partie
            if not in_game and previously_in_game.get(summoner_name, False):
                history = get_match_history(puuid)
                result = get_game_result(puuid, history[0])

                if result:
                    winners, losers = distribute_gains(summoner_name, result)

                    # Appel à la nouvelle fonction pour afficher les résultats
                    await afficher_resultat_partie(channel, summoner_name, result, winners, losers, summoner_ratings, bot)

                    print(f"Gagnants : {winners}")
                    print(f"Perdants : {losers}")

                    # Supprimer les paris pour cet ami après la fin de la partie
                    remove_finished_bets(summoner_name)

                # Le summoner n'est plus en jeu    
                currently_ingame[:] = [player for player in currently_ingame if player['summoner_name'] != summoner_name]    

            # Met à jour l'état précédent
            previously_in_game[summoner_name] = in_game
        
        # Attendre 60 secondes avant de vérifier à nouveau
        await asyncio.sleep(60)

async def update_summoner_rating_for_player(summoner_name, puuid):
    while not bot.is_closed():
        try:
            # Calculer la cote du joueur
            cote = calculate_winrate(puuid)

            # Mettre à jour la cote du joueur dans le dictionnaire
            summoner_ratings[summoner_name] = cote
            print(f"Cote de {summoner_name} mise à jour : {cote}")
        
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la cote pour {summoner_name}: {e}")

        # Attendre un certain intervalle avant de vérifier à nouveau
        await asyncio.sleep(1800)  # 1800 secondes = 30 minutes

# Fonction pour surveiller et lancer des tâches asynchrones pour chaque joueur
async def update_summoner_ratings():
    await bot.wait_until_ready()
    
    # Dictionnaire pour stocker les tâches asynchrones pour chaque joueur
    tasks = {}
    
    while not bot.is_closed():
        # Obtenir la liste des amis surveillés
        friends_list = get_friends_list()

        for friend in friends_list:
            summoner_name = friend['name']
            puuid = friend['puuid']
            
            # Si une tâche n'existe pas déjà pour ce joueur, on en crée une
            if summoner_name not in tasks:
                # Créer une nouvelle tâche pour surveiller la cote du joueur en différé
                tasks[summoner_name] = asyncio.create_task(update_summoner_rating_for_player(summoner_name, puuid))
        
        # Attendre une période avant de relancer la boucle 
        await asyncio.sleep(60)  # On peut ajuster cet intervalle si nécessaire

@bot.event
async def on_ready():
    print(f'{bot.user} est connecté à Discord !')

    # Lancer la mise à jour des évaluations des invocateurs immédiatement
    asyncio.create_task(update_summoner_ratings())

    # Attendre 30 secondes avant de lancer notify_if_friends_in_game (temporaire car tableau des joueurs déjà préétablit nécéssite d'attendre le rating)
    await asyncio.sleep(30)

    # Lancer la notification des amis en jeu après le délai de 30 secondes
    asyncio.create_task(notify_if_friends_in_game())

bot.run(TOKEN)