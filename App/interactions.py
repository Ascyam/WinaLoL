import discord
from discord.ext import commands
from datetime import datetime, timedelta
from .friends import add_friend, remove_friend, get_friends_list, get_summoner_rank
from .WinaLoL.betting import active_bets, place_bet, get_active_bets, currently_ingame
from .WinaLoL.wallet import get_balance, add_coins, user_wallets
from .dictionnaire import *

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
bot = commands.Bot(command_prefix="??", intents=intents)

# Variable globale pour suivre si la configuration a été effectuée
config_initialized = False

user_claim_data  = {}

@bot.command(name='aide', help="Affiche toutes les commandes disponibles.")
async def afficher_aide(ctx):
    aide_message = """
    **Commandes disponibles :**

    **??add_summoner <nom> <tag>** - Ajoute un ami à la liste des invocateurs surveillés.
    Exemple : `??add_summoner YoyoRapido RAPH`

    **??remove_summoner <nom> <tag>** - Retire un ami de la liste des invocateurs surveillés.
    Exemple : `??remove_summoner YoyoRapido RAPH`

    **??list_summoners** - Affiche la liste actuelle des invocateurs surveillés.
    Exemple : `??list_summoners`

    **??bet <nom_ami> <montant> <win/lose>** - Parie des akhy coins sur la victoire ou la défaite d'un ami.
    Exemple : `??bet YoyoRapido 50 win`

    **??bet_options** - Affiche l'état actuel des paris.
    Exemple : `??bet_options`

    **??balance** - Affiche ton solde actuel d'akhy coins.
    Exemple : `??balance`

    **??current_bets** - Affiche la liste des paris encore actifs, du plus gros au plus petit, jusqu'à 20 paris.
    Exemple : `??current_bets`

    **??rankings** - Affiche le classement Elo des invocateurs suivis du meilleur au moins bon.
    Exemple : `??rankings`

    **??leaderboard** - Affiche le classement des meilleurs parieurs en fonction de leur nombre de jetons.
    Exemple : `??leaderboard`

    **??daily** - Récupère 10 akhy coins une fois par jour. Après 10, 30 et 100 jours consécutifs, tu peux recevoir un bonus de 50, 100 ou 1000 akhy coins respectivement.
    Exemple : `??daily`

    **??show_config** - Affiche les paramètres de configuration actuels du bot.
    Exemple : `??show_config`

    **??aide** - Affiche cette aide détaillée.
    """
    await ctx.send(aide_message)

@bot.command(name='add_summoner', help="Ajoute un ami à la liste des idiots. Usage: ??add_summoner <nom> <tag>")
async def ajouter_ami(ctx, *args):
    # Vérifier que le nombre d'arguments est suffisant (au moins 2 : nom et tag)
    if len(args) < 2:
        await ctx.send("Utilisation incorrecte. Usage: ??add_summoner <nom_composé> <tag>")
        return

    # Séparer le nom et le tag
    summoner_name = " ".join(args[:-1])  # Le nom composé est tout sauf le dernier argument
    tag_line = args[-1]  # Le dernier argument est le tag

    # Ajout du joueur
    add_friend(summoner_name, tag_line)
    await ctx.send(f"Tentative d'ajout de {summoner_name}#{tag_line} à la liste des amis.")

@bot.command(name='remove_summoner', help="Retire un ami de la liste des idiots. Usage: ??remove_summoner <nom> <tag>")
async def retirer_ami(ctx, *args):
    # Vérifier que le nombre d'arguments est suffisant (au moins 2 : nom et tag)
    if len(args) < 2:
        await ctx.send("Utilisation incorrecte. Usage: ??remove_summoner <nom_composé> <tag>")
        return

    # Séparer le nom et le tag
    summoner_name = " ".join(args[:-1])  # Le nom composé est tout sauf le dernier argument
    tag_line = args[-1]  # Le dernier argument est le tag

    # Retrait du joueur
    remove_friend(summoner_name, tag_line)
    await ctx.send(f"{summoner_name}#{tag_line} a été retiré de la liste des amis.")


@bot.command(name='list_summoners', help="Affiche la liste actuelle des idiots.")
async def lister(ctx):
    friends_list = get_friends_list()

    if not friends_list:
        await ctx.send("Il n'y a encore aucun ami.")
    else:
        liste = "\n".join([f"{friend['name']}#{friend['tag']}" for friend in friends_list])
        await ctx.send(f"Voici la liste actuelle des amis : \n{liste}")

@bot.command(name='bet', help="Parier sur la victoire ou la défaite d'un ami. Usage: ??bet <nom_ami> <montant> <win/lose>")
@commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
async def bet(ctx, *args):
    # Vérifier que le nombre d'arguments est suffisant (au moins 3)
    if len(args) < 3:
        await ctx.send("Utilisation incorrecte. Usage: ??bet <nom_ami> <montant> <win/lose>")
        return

    # Séparer le montant et le choix du reste des arguments
    friend_name = " ".join(args[:-2])  # Les mots avant les 2 derniers sont le nom de l'ami
    try:
        amount = int(args[-2])  # L'avant-dernier argument est le montant
    except ValueError:
        await ctx.send("Le montant doit être un nombre valide.")
        return
    choice = args[-1].lower()  # Le dernier argument est le choix (win/lose)

    # Vérifier si le choix est valide
    if choice not in ['win', 'lose']:
        await ctx.send("Choix invalide. Utilise 'win' ou 'lose'.")
        return

    user_id = str(ctx.author.id)

    # Appel à la fonction de placement de pari
    success, message = place_bet(user_id, friend_name, amount, choice)
    await ctx.send(message)

@bot.command(name='balance', help="Voir ton solde d'akhy coins.")
async def balance(ctx):
    user_id = str(ctx.author.id)
    balance = get_balance(user_id)
    await ctx.send(f"Tu as {balance} akhy coins.")

@bot.command(name='current_bets', help="Affiche les 20 plus gros paris encore actifs.")
async def current_bets(ctx):
    active_bets_list = get_active_bets()
    
    if not active_bets_list:
        await ctx.send("Il n'y a actuellement aucun pari actif.")
        return

    # Construire le message à envoyer
    bets_message = "**Les 20 plus gros paris encore actifs :**\n"
    for bet in active_bets_list:
        user = await bot.fetch_user(bet['user_id'])  # Récupérer l'utilisateur via l'ID
        bets_message += f"**{user.name}** a parié **{bet['amount']} akhy coins** sur la {'victoire' if bet['bet_type'] == 'win' else 'défaite'} de **{bet['friend_name']}**.\n"

    await ctx.send(bets_message)

@bot.command(name='rankings', help="Affiche le classement Elo des invocateurs surveillés du meilleur au moins bon.")
@commands.cooldown(rate=1, per=30.0, type=commands.BucketType.user)
async def afficher_ranking(ctx):
    friends_list = get_friends_list()
    ranked_friends = []

    for friend in friends_list:
        summoner_name = friend['name']
        encryptedSummonerId = friend['summoner_encryptedSummonerId']

        # Récupérer les informations de classement de l'invocateur
        summoner_rank = get_summoner_rank(encryptedSummonerId)
        if summoner_rank:
            ranked_friends.append({
                'name': summoner_name,
                'tier': summoner_rank['tier'],
                'rank': summoner_rank['rank'],
                'lp': summoner_rank['lp']
            })
    
    # Trier les invocateurs par tier, rank et league points (lp)
    ranked_friends.sort(
        key=lambda x: (
            TIER_ORDER.get(x['tier'], 0),         # Trier par tier (numérique)
            RANK_ORDER.get(x['rank'], 0),         # Trier par rank (numérique)
            x['lp']                               # Trier par league points (lp)
        ),
        reverse=True
    )

    if not ranked_friends:
        await ctx.send("Aucun invocateur surveillé n'a de classement Elo.")
    else:
        # Créer un joli message pour afficher les informations triées
        classement_message = "**Classement Elo des invocateurs suivis :**\n"
        for i, summoner in enumerate(ranked_friends, 1):
            tier = summoner['tier']
            icon = TIER_ICONS.get(tier, '')  # Récupérer l'icône du rang ou une chaîne vide si non trouvé
            classement_message += f"{i}. **{summoner['name']}** - {icon} {tier} {summoner['rank']} ({summoner['lp']} LP) {icon}\n"

        await ctx.send(classement_message)

@bot.command(name='leaderboard', help="Affiche le classement des meilleurs parieurs en fonction de leur nombre de jetons.")
async def leaderboard(ctx):
    # Récupère les soldes de tous les parieurs
    balances = user_wallets
    
    # Si aucun parieur n'a été trouvé
    if not balances:
        await ctx.send("Il n'y a pas encore de parieurs.")
        return

    # Trie les parieurs par solde décroissant
    sorted_balances = sorted(balances.items(), key=lambda x: x[1], reverse=True)

    # Limite à 10 (ou changez selon vos besoins)
    top_parieurs = sorted_balances[:10]

    # Créer le message avec le classement
    leaderboard_message = "**Classement des parieurs :**\n\n"
    for i, (user_id, balance) in enumerate(top_parieurs, start=1):
        # Obtenir l'objet membre Discord pour le nom de l'utilisateur
        user = await bot.fetch_user(user_id)
        leaderboard_message += f"{i}. {user.display_name} - **{balance} Akhy coins**\n"

    # Envoie le classement
    await ctx.send(leaderboard_message)

@bot.command(name='daily', help="Récupère 10 akhy coins une fois par jour, avec des bonus de jetons après 10, 30, et 100 jours consécutifs.")
async def daily(ctx):
    user_id = str(ctx.author.id)
    current_time = datetime.now()

    # Vérifier si l'utilisateur est déjà dans le dictionnaire
    if user_id not in user_claim_data:
        # Si c'est la première fois qu'il réclame, on initialise ses données
        user_claim_data[user_id] = {
            'last_claim': current_time,
            'consecutive_days': 1
        }
        add_coins(user_id, 10)
        await ctx.send("Tu as récupéré 10 akhy coins ! Reviens demain pour continuer ta série.")
        return

    # Récupérer les informations de l'utilisateur
    last_claim_time = user_claim_data[user_id]['last_claim']
    consecutive_days = user_claim_data[user_id]['consecutive_days']

     # Vérifier si plus de 24 heures se sont écoulées depuis la dernière réclamation
    if current_time - last_claim_time >= timedelta(days=1):
        # Vérifier si la réclamation est consécutive ou non
        if current_time - last_claim_time <= timedelta(days=2):
            consecutive_days += 1  # Incrémenter les jours consécutifs
        else:
            consecutive_days = 1  # Réinitialiser à 1 si la série est brisée

        # Donner les 10 jetons journaliers
        add_coins(user_id, 10)
        
        # Vérifier les bonus en fonction des jours consécutifs
        bonus = 0
        if consecutive_days % 100 == 0 and consecutive_days > 0:
            bonus = 1000  # Bonus de 1000 jetons après chaque 100 jours
        elif consecutive_days % 30 == 0 and consecutive_days > 0:
            bonus = 100  # Bonus de 100 jetons après chaque 30 jours
        elif consecutive_days % 10 == 0 and consecutive_days > 0:
            bonus = 50  # Bonus de 50 jetons après chaque 10 jours
        
        # Appliquer le bonus s'il existe
        if bonus > 0:
            add_coins(user_id, bonus)  # Ajout du bonus au portefeuille de l'utilisateur
            await ctx.send(f"Félicitations ! Tu as récupéré un bonus de {bonus} akhy coins pour {consecutive_days} jours consécutifs de réclamations !")
        
        # Mise à jour des informations de l'utilisateur
        user_claim_data[user_id]['last_claim'] = current_time
        user_claim_data[user_id]['consecutive_days'] = consecutive_days

        await ctx.send(f"Tu as récupéré 10 akhy coins ! ({consecutive_days} jours consécutifs)")
    
    else:
        # Si l'utilisateur a déjà réclamé des jetons dans les dernières 24 heures
        time_remaining = (last_claim_time + timedelta(days=1)) - current_time
        hours, remainder = divmod(time_remaining.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        await ctx.send(f"Tu as déjà récupéré tes jetons aujourd'hui. Reviens dans {hours}h{minutes}m.")

@bot.command(name='bet_options', help="Affiche l'état actuel des paris.")
async def bet_options(ctx):
    possible_bets_message = "**État des paris en cours :**\n"

    if not currently_ingame:
        await ctx.send("Aucun ami ne joue actuellement.")
        return

    # Vérifier les paris actifs et possibles
    for friend in active_bets:
        # Vérifier si les paris sont ouverts pour ce joueur
        if not active_bets[friend].get('closed', False):
            possible_bets_message += f"- {friend} : Les paris sont ouverts\n"
        else:
            possible_bets_message += f"- {friend} : Les paris sont fermés.\n"

    await ctx.send(possible_bets_message)

@bot.command(name='show_config', help="Affiche les paramètres actuels du bot.")
async def show_config(ctx):
    config_message = "\n".join([f"**{key}**: {value}" for key, value in CONFIG.items()])
    await ctx.send(f"**Configuration actuelle du bot :**\n{config_message}")