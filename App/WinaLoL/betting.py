import math
from .wallet import add_coins, remove_coins, get_balance

# Structure pour stocker les paris en cours
active_bets = {}
currently_ingame=[]
summoner_ratings = {}  # Dictionnaire pour stocker les cotes des joueurs

def add_summoner_to_active_bets(summoner_name):
    # Vérifie si le joueur est déjà dans active_bets
    if summoner_name not in active_bets:
        # Initialise les données associées au joueur
        active_bets[summoner_name] = {
            'bets': [],       # Liste des paris associés à ce joueur
            'closed': False,  # Indicateur pour savoir si les paris sont fermés
            'win': [],        # Liste des gagnants
            'lose': []        # Liste des perdants
        }
        print(f"Summoner {summoner_name} ajouté dans active_bets.")
    else:
        print(f"Summoner {summoner_name} est déjà présent dans active_bets.")

# Fermer les paris pour un ami
def close_betting_for_summoner(summoner_name):
    if summoner_name in active_bets:
        active_bets[summoner_name]['closed'] = True  # Marque que les paris sont fermés pour cet ami

# Fonction pour récupérer le game_id du joueur en fonction de son nom
def get_game_id_for_summoner(summoner_name):
    for player in currently_ingame:
        if player['summoner_name'] == summoner_name:
            return player['game_id']
    return None

# Placer un pari avec vérification de la fermeture des paris
def place_bet(user_id, summoner_name, amount, choice):
    # Vérifier si le summoner joue
    if not any(player['summoner_name'] == summoner_name for player in currently_ingame):
        return False, "Le joueur ne joue pas ou tu n'as pas écrit correctement son pseudo."
    
    # Vérifier si les paris sont déjà fermés
    if active_bets[summoner_name].get('closed', False):
        return False, "Les paris sont fermés pour cette partie."
    
    # Récupérer l'identifiant unique de la partie
    game_id = get_game_id_for_summoner(summoner_name)

    # Vérifier si le game_id est valide
    if game_id is None:
        return False, f"Impossible de trouver une partie active pour {summoner_name}."
    
    # Vérifier si l'utilisateur a déjà parié sur un autre joueur dans la même partie
    for bet_summoner, bet_info in active_bets.items():
        # Récupérer le game_id du joueur lié au pari
        bet_game_id = get_game_id_for_summoner(bet_summoner)

        # Vérifier si le joueur lié au pari est dans la même partie
        if bet_game_id == game_id:
            # Rechercher si l'utilisateur a déjà parié dans cette partie
            if any(bet['user_id'] == user_id for bet in bet_info['win'] + bet_info['lose']):
                return False, f"Tu as déjà parié sur un joueur dans cette partie ({bet_summoner})."

    # Vérifier le solde de l'utilisateur
    if get_balance(user_id) < amount:
        return False, "Solde insuffisant pour placer ce pari."
    
    if amount > 100000:
        return False, "Tu ne peux parier que 100000 akhy coins maximum."

    # Retirer les coins de l'utilisateur
    remove_coins(user_id, amount)

    # Ajouter le pari à la liste des paris actifs
    if summoner_name not in active_bets:
        active_bets[summoner_name] = {'win': [], 'lose': [], 'closed': False}  # Initialiser avec "closed" à False
        print(f"Summoner {summoner_name} ajouté dans active_bets.")

    # Enregistrer le pari
    active_bets[summoner_name][choice].append({'user_id': user_id, 'amount': amount})

    return True, f"Tu as parié {amount} akhy coins sur la {'victoire' if choice == 'win' else 'défaite'} de {summoner_name}."

# Calcul des gains à la fin d'une partie
def distribute_gains(friend_name, result):
    if friend_name not in active_bets:
        return

     # Récupérer la cote du joueur stockée dans summoner_ratings
    odds = summoner_ratings.get(friend_name, 0.5)  # Valeur par défaut de 0.5 si la cote n'est pas trouvée

    # Récupérer les parieurs qui ont misé sur cette partie
    bets = active_bets.pop(friend_name, None)
    if not bets:
        return

    winners = bets[result]  # Liste des gagnants (ceux qui ont parié sur le bon résultat)
    losers = bets['win' if result == 'lose' else 'lose']  # Ceux qui ont perdu

    # Répartir les gains : on multiplie la mise gagnée 
    for winner in winners:
        if result == 'win':
            winnings = int(winner['amount'] * (math.exp(2.5*(1-odds) - (2.5*odds) - 0.2) + 1))
        else:
            winnings = int(winner['amount'] * (math.exp((2.5*odds) - 2.5*(1-odds) - 0.2) + 1))

        add_coins(winner['user_id'], winnings)
        print(f"{winner['user_id']} a gagné {winnings} akhy coins grâce à {friend_name}.")

    return winners, losers

    # Rien à faire pour les perdants, ils ont déjà perdu leurs mises

# Fonction pour récupérer les paris fermés mais dont la partie n'est pas encore finie
def get_active_bets():
    active_bets_list = []
    
    # Parcourir les paris actifs
    for friend_name, bets_data in active_bets.items():
        if 'result' not in bets_data:  # Si le résultat n'est pas encore connu
            for bet_type in ['win', 'lose']:
                for bet in bets_data[bet_type]:
                    active_bets_list.append({
                        'friend_name': friend_name,
                        'user_id': bet['user_id'],
                        'amount': bet['amount'],
                        'bet_type': bet_type
                    })

    # Trier par montant décroissant
    sorted_bets = sorted(active_bets_list, key=lambda x: x['amount'], reverse=True)
    
    # Limiter à 20 paris
    return sorted_bets[:20]

# Ajouter une fonction pour supprimer les paris après la fin de la partie
def remove_finished_bets(friend_name):
    if friend_name in active_bets:
        del active_bets[friend_name]
