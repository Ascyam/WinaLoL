# Initialisation du portefeuille avec un solde de départ
INITIAL_BALANCE = 100

# Dictionnaire pour stocker les akhy coins des utilisateurs
user_wallets = {}

# Fonction pour initialiser un utilisateur avec 100 akhy coins s'il n'a pas de compte
def initialize_user(user_id):
    if user_id not in user_wallets:
        user_wallets[user_id] = INITIAL_BALANCE
        print(f"{user_id} a reçu {INITIAL_BALANCE} akhy coins au départ.")
        return True
    return False

# Fonction pour ajouter des akhy coins à un utilisateur
def add_coins(user_id, amount):
    initialize_user(user_id)  # S'assurer que l'utilisateur est initialisé
    user_wallets[user_id] += amount
    print(f"{amount} akhy coins ont été ajoutés à {user_id}. Total: {user_wallets[user_id]}")

# Fonction pour retirer des akhy coins à un utilisateur
def remove_coins(user_id, amount):
    initialize_user(user_id)  # S'assurer que l'utilisateur est initialisé
    if user_wallets[user_id] < amount:
        return False  # Pas assez de coins
    user_wallets[user_id] -= amount
    print(f"{amount} akhy coins ont été retirés à {user_id}. Total: {user_wallets[user_id]}")
    return True

# Fonction pour obtenir le solde d'un utilisateur
def get_balance(user_id):
    initialize_user(user_id)  # S'assurer que l'utilisateur est initialisé
    return user_wallets.get(user_id, 0)