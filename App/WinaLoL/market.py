import random

from .wallet import remove_coins, get_balance

user_inventories = {}

# Définir les niveaux de rareté
RARITIES = {
    "Common": ["Skin Commun 1", "Skin Commun 2", "Skin Commun 3"],
    "Uncommon": ["Skin Peu Commun 1", "Skin Peu Commun 2"],
    "Rare": ["Skin Rare 1", "Skin Rare 2"],
    "Super Rare": ["Skin Très Rare 1"],
    "Epic": ["Skin Epique 1"],
    "Legendary": ["Skin Légendaire 1"],
    "Invaluable": ["Skin Inestimable 1"]
}

# Définir les chances de drop pour chaque type de coffre
DROP_CHANCES = {
    "Common": {
        "Common": 50.0,
        "Uncommon": 30.0,
        "Rare": 15.0,
        "Super Rare": 4,
        "Epic": 0.8,
        "Legendary": 0.19,
        "Invaluable": 0.01
    },
    "Rare": {
        "Rare": 50.0,
        "Super Rare": 30.0,
        "Epic": 15.0,
        "Legendary": 4.5,
        "Invaluable": 0.5
    },
    "Epic": {
        "Epic": 60.0,
        "Legendary": 30.0,
        "Invaluable": 10.0
    }
}

# Prix des coffres
CHEST_PRICES = {
    "Common": 1000,  # Coffre commun
    "Rare": 10000,  # Coffre avec minimum un skin rare
    "Epic": 100000  # Coffre avec minimum un skin Epique
}


# Fonction pour acheter un coffre
def buy_chest(user_id, chest_type):
    # Vérifier le solde de l'utilisateur
    if get_balance(user_id) < CHEST_PRICES[chest_type]:
        return False, "Solde insuffisant pour acheter ce coffre."

    # Retirer le prix du coffre
    remove_coins(user_id, CHEST_PRICES[chest_type])

    # Ouvrir le coffre et obtenir un skin
    skin = open_chest(chest_type)

    # Ajouter le skin à l'inventaire de l'utilisateur
    add_to_inventory(user_id, skin)

    return True, f"Félicitations ! Vous avez obtenu le skin : {skin}"


# Fonction pour ouvrir un coffre et retourner un skin en fonction du type
def open_chest(chest_type):
    rarity_chances = DROP_CHANCES[chest_type]
    rand = random.randint(1, 100)

    cumulative_probability = 0.0
    for rarity, chance in rarity_chances.items():
        cumulative_probability += chance
        if rand <= cumulative_probability:
            # Retourner un skin aléatoire de la rareté obtenue
            return random.choice(RARITIES[rarity])


# Fonction pour ajouter un skin à l'inventaire de l'utilisateur
def add_to_inventory(user_id, skin):
    # Vérifiez si l'utilisateur a déjà un inventaire
    if user_id not in user_inventories:
        user_inventories[user_id] = []  # Crée un nouvel inventaire s'il n'existe pas

    # Ajoutez le skin à l'inventaire de l'utilisateur
    user_inventories[user_id].append(skin)
    print(f"{skin} a été ajouté à l'inventaire de l'utilisateur {user_id}.")
