import asyncio
import math
import time

from .WinaLoL.betting import *
from .friends import *
from .front import *
from .interactions import *

load_dotenv()  # Charger les variables d'environnement
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
    return 0.5  # Retourne 0.5 si aucun résultat n'est disponible


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
        gameQueueConfigId = game_data.get('gameQueueConfigId', 'Inconnu')
        game_id = game_data.get('gameId', 'Inconnu')

        # Récupération de la liste des joueurs et des champions choisis
        players = game_data.get('participants', [])
        draft = []

        for player in players:
            summoner_name = player['riotId']
            champion_id = player['championId']
            champion_name = get_champion_name_from_api(champion_id)
            draft.append(f"🔹 {summoner_name} - **{champion_name}**")

        return game_mode, gameQueueConfigId, draft, game_id

    except Exception as e:
        return f"Erreur lors de la récupération des informations du match : {e}"


def calculate_match_ranks(riot_id):
    # URL pour récupérer les informations de la partie
    match_url = f"https://{CONFIG['REGION_Lol']}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{riot_id}?api_key={RIOT_API_KEY}"
    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }

    response = requests.get(match_url, headers=headers)

    if response.status_code != 200:
        return None, "Erreur lors de la récupération de la partie"

    match_data = response.json()

    # Séparer les équipes
    team_1 = []
    team_2 = []
    team_summoner = None  # Initialise la variable avant de l'utiliser

    for participant in match_data['participants']:
        summoner_id = participant['puuid']
        encryptedId = participant['summonerId']
        summoner_rank = get_summoner_rank(encryptedId)

        if summoner_rank is None:
            continue  # Si le rang n'est pas trouvé, on ignore ce joueur

        # Ajouter les joueurs à leur équipe respective
        if participant['teamId'] == 100:
            team_1.append(summoner_rank)
        else:
            team_2.append(summoner_rank)

        if summoner_id == riot_id:
            team_summoner = participant['teamId']

    if team_summoner == 100:
        return team_1, team_2
    else:
        return team_2, team_1

    # Fonction pour calculer la moyenne des rangs (convertis en valeurs numériques)


def rank_to_value(rank_data):
    tier_values = {
        'IRON': 100, 'BRONZE': 108, 'SILVER': 116, 'GOLD': 124, 'PLATINUM': 132, 'EMERALD': 140,
        'DIAMOND': 148, 'MASTER': 152, 'GRANDMASTER': 156, 'CHALLENGER': 160
    }
    rank_values = {'IV': 2, 'III': 4, 'II': 6, 'I': 8}

    # Convertir le rang et le palier en une valeur numérique
    tier_value = tier_values.get(rank_data['tier'], 1)
    rank_value = rank_values.get(rank_data['rank'], 1)
    return tier_value + rank_value

    # Calcul de la moyenne des rangs


def calculate_team_average(team):
    if not team:
        return 0  # Cas où il n'y a pas de données pour l'équipe
    return round(sum(rank_to_value(elo) for elo in team) / len(team), 4)


def get_champion_name_from_api(champion_id):
    ddragon = "https://ddragon.leagueoflegends.com/api/versions.json"
    response_dd = requests.get(ddragon)
    version = response_dd.json()[0]

    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
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
    oddw = 1.89
    oddl = 1.89

    gambler_ping_message = await ping_gambler_role(channel)

    while not bot.is_closed():
        friends_list = get_friends_list()  # Récupérer la liste des amis à chaque boucle

        for friend in friends_list:
            summoner_name = friend['name']
            puuid = friend['puuid']

            in_game = is_friend_in_game(puuid)

            # Si l'ami est en jeu et qu'il ne l'était pas auparavant, on envoie une notification
            if in_game and not previously_in_game.get(summoner_name, False):
                game_mode, gameQueueConfigId, draft, game_id = get_game_info(puuid)

                team_1, team_2 = calculate_match_ranks(puuid)

                avg_team_1 = calculate_team_average(team_1)
                avg_team_2 = calculate_team_average(team_2)

                if (avg_team_1 != 0) & (avg_team_2 != 0):
                    oddw = round(math.exp(25 * (1 - avg_team_1 / (avg_team_1 + avg_team_2)) - (
                            25 * avg_team_1 / (avg_team_1 + avg_team_2)) - 0.12) + 1, 2)
                    oddl = round(math.exp((25 * avg_team_1 / (avg_team_1 + avg_team_2)) - 25 * (
                            1 - avg_team_1 / (avg_team_1 + avg_team_2)) - 0.12) + 1, 2)

                    # Appel à la fonction pour afficher le message d'annonce du lancement de partie
                await afficher_lancement_partie(channel, summoner_name, oddw, oddl, gambler_ping_message,
                                                gameQueueConfigId, draft)

                # Démarrer un chronomètre pour fermer les paris après 3 minutes
                bet_timers[summoner_name] = time.time()
                # Le summoner est en jeu    
                currently_ingame.append({
                    'summoner_name': summoner_name,
                    'game_id': game_id,
                    'gameQueueConfigId': gameQueueConfigId
                })
                # Initialise les données associées au joueur
                add_summoner_to_active_bets(summoner_name)

            if in_game and summoner_name in bet_timers:
                elapsed_time = time.time() - bet_timers[summoner_name]

                if elapsed_time > 180:  # 180 secondes = 3 minutes
                    close_betting_for_summoner(summoner_name)  # Fermer les paris pour cet ami
                    await channel.send(f"⏳ Les paris pour **{summoner_name}** sont désormais fermés.")
                    del bet_timers[summoner_name]

            # Si l'ami vient de finir sa partie
            if not in_game and previously_in_game.get(summoner_name, False):
                history = get_match_history(puuid)
                result = get_game_result(puuid, history[0])

                if result:
                    winners, losers = distribute_gains(summoner_name, result, oddw, oddl)

                    # Appel à la nouvelle fonction pour afficher les résultats
                    await afficher_resultat_partie(channel, summoner_name, result, winners, losers, oddw, oddl, bot)

                    print(f"Gagnants : {winners}")
                    print(f"Perdants : {losers}")

                    # Supprimer les paris pour cet ami après la fin de la partie
                    remove_finished_bets(summoner_name)

                # Le summoner n'est plus en jeu    
                currently_ingame[:] = [player for player in currently_ingame if
                                       player['summoner_name'] != summoner_name]

                # Met à jour l'état précédent
            previously_in_game[summoner_name] = in_game

        # Attendre 60 secondes avant de vérifier à nouveau
        await asyncio.sleep(60)
