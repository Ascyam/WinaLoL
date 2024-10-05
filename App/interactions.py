from datetime import datetime, timedelta

import discord
from discord.ext import commands

from .WinaLoL.betting import active_bets, place_bet, get_active_bets, currently_ingame
from .WinaLoL.wallet import get_balance, add_coins, user_wallets
from .dictionnaire import *
from .friends import add_friend, remove_friend, get_friends_list, get_summoner_rank

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="??", intents=intents)

# Variable globale pour suivre si la configuration a été effectuée
config_initialized = False

user_claim_data = {}


@bot.command(name='aide', help="Affiche toutes les commandes disponibles.")
@commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
async def print_help(ctx):
    embed = discord.Embed(
        title="📜 Commandes disponibles",
        description="Voici la liste des commandes que vous pouvez utiliser avec le bot.",
        color=discord.Color.gold()
    )

    # Ajout des différentes commandes avec des champs
    embed.add_field(
        name="🟢 **??add_summoner <nom> <tag>**",
        value="Ajoute un ami à la liste des invocateurs surveillés.\nExemple : `??add_summoner YoyoRapido RAPH`",
        inline=False
    )

    embed.add_field(
        name="🔴 **??remove_summoner <nom> <tag>**",
        value="Retire un ami de la liste des invocateurs surveillés.\nExemple : `??remove_summoner YoyoRapido RAPH`",
        inline=False
    )

    embed.add_field(
        name="👥 **??list_summoners**",
        value="Affiche la liste actuelle des invocateurs surveillés.\nExemple : `??list_summoners`",
        inline=False
    )

    embed.add_field(
        name="🎰 **??bet <nom_ami> <montant> <win/lose>**",
        value="Parie des akhy coins sur la victoire ou la défaite d'un ami.\nExemple : `??bet YoyoRapido 50 win`",
        inline=False
    )

    embed.add_field(
        name="🤑 **??bet_options**",
        value="Affiche l'état actuel des paris.\nExemple : `??bet_options`",
        inline=False
    )

    embed.add_field(
        name="💰 **??balance**",
        value="Affiche ton solde actuel d'akhy coins.\nExemple : `??balance`",
        inline=False
    )

    embed.add_field(
        name="📝 **??current_bets**",
        value="Affiche la liste des paris encore actifs, du plus gros au plus petit, jusqu'à 20 paris.\nExemple : `??current_bets`",
        inline=False
    )

    embed.add_field(
        name="🏆 **??rankings**",
        value="Affiche le classement Elo des invocateurs suivis du meilleur au moins bon.\nExemple : `??rankings`",
        inline=False
    )

    embed.add_field(
        name="🏅 **??leaderboard**",
        value="Affiche le classement des meilleurs parieurs en fonction de leur nombre de jetons.\nExemple : `??leaderboard`",
        inline=False
    )

    embed.add_field(
        name="🎁 **??daily**",
        value="Récupère 10 akhy coins une fois par jour. Après 10, 30 et 100 jours consécutifs, tu peux recevoir un bonus de 100, 1000 ou 10000 akhy coins.\nExemple : `??daily`",
        inline=False
    )

    embed.add_field(
        name="⚙️ **??show_config**",
        value="Affiche les paramètres de configuration actuels du bot.\nExemple : `??show_config`",
        inline=False
    )

    embed.add_field(
        name="🔧 **??config**",
        value="Modifie la configuration du bot. Exemples : `!config REGION_Lol euw1`, `!config REGION_Riot europe`, `!config ROLE Gambler` ou `!config CHANNEL winalol`.",
        inline=False
    )

    embed.add_field(
        name="❓ **??aide**",
        value="Affiche cette aide détaillée.",
        inline=False
    )

    # Envoie l'embed dans le channel
    await ctx.send(embed=embed)


@bot.command(name='add_summoner', help="Ajoute un ami à la liste des idiots. Usage: ??add_summoner <nom> <tag>")
@commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
async def add_summoner(ctx, *args):
    # Vérifier que le nombre d'arguments est suffisant (au moins 2 : nom et tag)
    if len(args) < 2:
        await ctx.send("Utilisation incorrecte. Usage: ??add_summoner <nom_composé> <tag>")
        return

    # Séparer le nom et le tag
    summoner_name = " ".join(args[:-1])  # Le nom composé est tout sauf le dernier argument
    tag_line = args[-1]  # Le dernier argument est le tag

    # Ajout du joueur
    add_friend(summoner_name, tag_line)
    await ctx.send(f"Ajout de {summoner_name}#{tag_line} à la liste des amis.")


@bot.command(name='remove_summoner', help="Retire un ami de la liste des idiots. Usage: ??remove_summoner <nom> <tag>")
@commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
async def remove_summoner(ctx, *args):
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


@bot.command(name='list_summoners', help="Affiche la liste actuelle des invocateurs.")
@commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
async def list_summoners(ctx):
    friends_list = get_friends_list()

    if not friends_list:
        embed = discord.Embed(
            title="👥 Liste des invocateurs :",
            description="Il n'y a encore aucun ami.",
            color=discord.Color.dark_purple()  # Couleur violet foncé
        )
    else:
        liste = "\n".join([f"{friend['name']}#{friend['tag']}" for friend in friends_list])
        embed = discord.Embed(
            title="👥 Liste des invocateurs suivis :",
            description=f"{liste}",
            color=discord.Color.dark_purple()  # Couleur violet foncé
        )

    await ctx.send(embed=embed)


@bot.command(name='bet',
             help="Parier sur la victoire ou la défaite d'un ami. Usage: ??bet <nom_ami> <montant> <win/lose>")
@commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
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
@commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
async def balance(ctx):
    user_id = str(ctx.author.id)
    balance = get_balance(user_id)
    await ctx.send(f"Tu as {balance} akhy coins.")


@bot.command(name='current_bets', help="Affiche les 20 plus gros paris encore actifs.")
@commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
async def current_bets(ctx):
    active_bets_list = get_active_bets()

    if not active_bets_list:
        embed = discord.Embed(
            title="💸 Paris actifs :",
            description="Il n'y a actuellement aucun pari actif.",
            color=discord.Color.dark_purple()  # Couleur violet foncé
        )
        await ctx.send(embed=embed)
        return

    # Construire le message à envoyer sous forme d'embed
    embed = discord.Embed(
        title="💸 Les 20 plus gros paris encore actifs :",
        color=discord.Color.dark_purple()  # Couleur violet foncé
    )

    # Ajouter chaque pari comme un champ dans l'embed
    for bet in active_bets_list[:20]:  # Limiter à 20 paris
        user = await bot.fetch_user(bet['user_id'])  # Récupérer l'utilisateur via l'ID
        bet_description = f"{user.name} a parié **{bet['amount']} akhy coins** sur la {'victoire' if bet['bet_type'] == 'win' else 'défaite'} de **{bet['friend_name']}**."
        embed.add_field(name=f"Pari #{active_bets_list.index(bet) + 1}", value=bet_description, inline=False)

    await ctx.send(embed=embed)


@bot.command(name='rankings', help="Affiche le classement Elo des invocateurs surveillés du meilleur au moins bon.")
@commands.cooldown(rate=1, per=30.0, type=commands.BucketType.user)
async def show_rankings(ctx):
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
            TIER_ORDER.get(x['tier'], 0),  # Trier par tier (numérique)
            RANK_ORDER.get(x['rank'], 0),  # Trier par rank (numérique)
            x['lp']  # Trier par league points (lp)
        ),
        reverse=True
    )

    if not ranked_friends:
        embed = discord.Embed(
            title="📊 Classement Elo :",
            description="Aucun invocateur surveillé n'a de classement Elo.",
            color=discord.Color.dark_purple()  # Couleur violet foncé
        )
        await ctx.send(embed=embed)
    else:
        # Créer l'embed pour afficher les informations triées
        embed = discord.Embed(
            title="📊 Classement Elo des invocateurs suivis :",
            color=discord.Color.dark_purple()  # Couleur violet foncé
        )

        # Ajouter chaque invocateur et son classement comme champ dans l'embed
        for i, summoner in enumerate(ranked_friends, 1):
            tier = summoner['tier']
            icon = TIER_ICONS.get(tier, '')  # Récupérer l'icône du rang ou une chaîne vide si non trouvé
            classement = f"**{summoner['name']}** - {icon} {tier} {summoner['rank']} ({summoner['lp']} LP) {icon}"
            embed.add_field(name=f"Invocateur #{i}", value=classement, inline=False)

        await ctx.send(embed=embed)


@bot.command(name='leaderboard',
             help="Affiche le classement des meilleurs parieurs en fonction de leur nombre de jetons.")
@commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
async def leaderboard(ctx):
    # Récupère les soldes de tous les parieurs
    balances = user_wallets

    # Si aucun parieur n'a été trouvé
    if not balances:
        embed = discord.Embed(
            title="🏆 Classement des parieurs :",
            description="Il n'y a pas encore de parieurs.",
            color=discord.Color.dark_purple()  # Couleur violet foncé
        )
        await ctx.send(embed=embed)
        return

    # Trie les parieurs par solde décroissant
    sorted_balances = sorted(balances.items(), key=lambda x: x[1], reverse=True)

    # Limite à 10 (ou changez selon vos besoins)
    top_parieurs = sorted_balances[:10]

    # Créer un embed pour le classement
    embed = discord.Embed(
        title="🏆 Classement des parieurs :",
        color=discord.Color.dark_purple()  # Couleur violet foncé
    )

    # Ajouter chaque parieur avec son classement dans l'embed
    for i, (user_id, balance) in enumerate(top_parieurs, start=1):
        user = await bot.fetch_user(user_id)  # Obtenir l'utilisateur Discord
        embed.add_field(
            name=f"Parieur #{i}",
            value=f"**{user.display_name}** - {balance} Akhy coins",
            inline=False
        )

    # Envoie le classement sous forme d'embed
    await ctx.send(embed=embed)


@bot.command(name='daily',
             help="Récupère 10 akhy coins une fois par jour, avec des bonus de jetons après 10, 30, et 100 jours consécutifs.")
@commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
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
            bonus = 10000  # Bonus de 10000 jetons après chaque 100 jours
        elif consecutive_days % 30 == 0 and consecutive_days > 0:
            bonus = 1000  # Bonus de 1000 jetons après chaque 30 jours
        elif consecutive_days % 10 == 0 and consecutive_days > 0:
            bonus = 100  # Bonus de 100 jetons après chaque 10 jours

        # Appliquer le bonus s'il existe
        if bonus > 0:
            add_coins(user_id, bonus)  # Ajout du bonus au portefeuille de l'utilisateur
            await ctx.send(
                f"Félicitations ! Tu as récupéré un bonus de {bonus} akhy coins pour {consecutive_days} jours consécutifs de réclamations !")

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
@commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
async def bet_options(ctx):
    # Créer un embed pour le message d'état des paris
    embed = discord.Embed(
        title="💰 État des paris en cours :",
        color=discord.Color.dark_purple()  # Couleur violet foncé
    )

    # Listes pour les paris ouverts et fermés
    paris_ouverts = []
    paris_fermes = []

    # Vérifier s'il y a des joueurs actuellement en jeu
    if not currently_ingame:
        embed.description = "Aucun ami ne joue actuellement."
        await ctx.send(embed=embed)
        return

    # Parcourir les amis avec des paris actifs et les classer selon leur état
    for friend in active_bets:
        if not active_bets[friend].get('closed', False):
            paris_ouverts.append(friend)
        else:
            paris_fermes.append(friend)

    # Ajouter la section "Les paris ouverts" dans l'embed
    if paris_ouverts:
        embed.add_field(
            name="🔓 Les paris ouverts :",
            value="\n".join(paris_ouverts),
            inline=False
        )
    else:
        embed.add_field(
            name="🔓 Les paris ouverts :",
            value="Aucun pari ouvert",
            inline=False
        )

    # Ajouter la section "Les paris fermés" dans l'embed
    if paris_fermes:
        embed.add_field(
            name="🔒 Les paris fermés :",
            value="\n".join(paris_fermes),
            inline=False
        )
    else:
        embed.add_field(
            name="🔒 Les paris fermés :",
            value="Aucun pari fermé",
            inline=False
        )

    # Envoyer l'embed
    await ctx.send(embed=embed)


@bot.command(name='show_config', help="Affiche les paramètres actuels du bot.")
@commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
async def show_config(ctx):
    config_message = "\n".join([f"**{key}**: {value}" for key, value in CONFIG.items()])
    await ctx.send(f"**Configuration actuelle du bot :**\n{config_message}")


@bot.command(name='config', help="Modifie la configuration du bot.")
@commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
async def config(ctx, key: str, value: str):
    # Vérifier si la clé existe dans la configuration
    if key not in CONFIG:
        await ctx.send(f"La clé `{key}` n'existe pas dans la configuration.")
        return

    # Vérification de la valeur de la clé spécifique
    if key == 'REGION_Lol' and value not in VALID_REGION_LOL:
        await ctx.send(f"Région LoL invalide. Les valeurs valides sont: {', '.join(VALID_REGION_LOL)}")
        return

    if key == 'REGION_Riot' and value not in VALID_REGION_RIOT:
        await ctx.send(f"Région Riot invalide. Les valeurs valides sont: {', '.join(VALID_REGION_RIOT)}")
        return

    # Mise à jour de la configuration
    CONFIG[key] = value
    await ctx.send(f"Configuration `{key}` modifiée à `{value}`.")
