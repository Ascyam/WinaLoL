import discord
import requests
import asyncio
import os
import time
from App.WinaLoL.betting import close_betting_for_summoner, currently_ingame
from dotenv import load_dotenv
from discord.ext import commands
from App.friends import *
from App.interactions import *
from App.WinaLoL.betting import *

load_dotenv()  # Charger les variables d'environnement

TOKEN = os.getenv('TOKEN')
RIOT_API_KEY = os.getenv('RIOT_API_KEY')

# Vérifier si l'ami est en jeu
def is_friend_in_game(riot_puuid):
    try:
        game_url = f"https://{REGION_Lol}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{riot_puuid}?api_key={RIOT_API_KEY}"
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
    match_history_url = f"https://{REGION_Riot}.api.riotgames.com/lol/match/v5/matches/by-puuid/{riot_puuid}/ids?api_key={RIOT_API_KEY}"
    
    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }
    response = requests.get(match_history_url, headers=headers)

    if response.status_code == 200:
        return response.json()  # Retourne la liste des IDs de match
    return None

def get_game_result(riot_puuid, match_id):
    match_url = f"https://{REGION_Riot}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={RIOT_API_KEY}"
    
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

# Fonction qui surveille les amis et envoie une notification sur Discord
async def notify_if_friends_in_game():
    await bot.wait_until_ready()
    channel = discord.utils.get(bot.get_all_channels(), name=CHANNEL)  # Le nom du channel Discord
    previously_in_game = {}  # Dictionnaire pour suivre l'état des amis
    bet_timers = {}  # Dictionnaire pour suivre le temps des paris pour chaque ami

    while not bot.is_closed():
        friends_list = get_friends_list()  # Récupérer la liste des amis à chaque boucle
        
        for friend in friends_list:
            summoner_name = friend['name']
            puuid = friend['puuid']
            
            in_game = is_friend_in_game(puuid)
                
            # Si l'ami est en jeu et qu'il ne l'était pas auparavant, on envoie une notification
            if in_game and not previously_in_game.get(summoner_name, False):
                await channel.send(
                    f"------------------------------------------------------------------------------------------------------------\n\n"
                    f"🌟 **Nouveau Match !** 🌟\n\n"
                    f"🎮 **{summoner_name}** vient de lancer une partie de **League of Legends** !\n\n"
                    f"💰 **Vous pouvez parier dès maintenant avec la commande :** `??bet`\n\n"
                    f"📊 **Cotes actuelles :**\n"
                    f"   **Victoire (Win)** : **{round((math.exp(2.5 * (1 - summoner_ratings.get(summoner_name, 0.5)) - (2.5 * summoner_ratings.get(summoner_name, 0.5)) - 0.2) + 1), 2)}**\n"
                    f"   **Défaite (Lose)** : **{round((math.exp((2.5 * summoner_ratings.get(summoner_name, 0.5)) - 2.5 * (1 - summoner_ratings.get(summoner_name, 0.5)) - 0.2) + 1), 2)}**\n\n"
                    f"⏳ **N'oubliez pas** : Les paris sont ouverts uniquement pendant **3 minutes** après le lancement du match !\n\n"
                )
                
                # Démarrer un chronomètre pour fermer les paris après 3 minutes
                bet_timers[summoner_name] = time.time()
                # Le summoner est en jeu    
                currently_ingame.append(summoner_name)
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
                    await channel.send(f"{summoner_name} a terminé une partie. Résultat : {'Victoire' if result == 'win' else 'Défaite'}.")
                    winners, losers = distribute_gains(summoner_name, result)

                    for winner in winners:
                        user = await bot.fetch_user(winner['user_id'])  # Récupérer l'utilisateur Discord
                        if result == 'win' :
                            await channel.send(f"{user.mention} a récupéré {int(winner['amount'] * (math.exp(2.5*(1-summoner_ratings.get(summoner_name, 0.5)) - (2.5*summoner_ratings.get(summoner_name, 0.5)) - 0.2) + 1))} akhy coins grâce à {summoner_name}.")
                        else :
                            await channel.send(f"{user.mention} a récupéré {int(winner['amount'] * (math.exp((2.5*summoner_ratings.get(summoner_name, 0.5)) - 2.5*(1-summoner_ratings.get(summoner_name, 0.5)) - 0.2) + 1))} akhy coins grâce à {summoner_name}.")

                    for loser in losers:
                        user = await bot.fetch_user(loser['user_id'])  # Récupérer l'utilisateur Discord
                        await channel.send(f"{user.mention} a perdu son pari à cause {summoner_name}.")
                    
                    print(f"Gagnants : {winners}")
                    print(f"Perdants : {losers}")

                    # Supprimer les paris pour cet ami après la fin de la partie
                    remove_finished_bets(summoner_name)

                # Le summoner n'est plus en jeu    
                currently_ingame.remove(summoner_name)    

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
    asyncio.create_task(notify_if_friends_in_game())  # Exécuter ces tâches en asynchrone
    asyncio.create_task(update_summoner_ratings())

bot.run(TOKEN)