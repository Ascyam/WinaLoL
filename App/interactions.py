import discord
from discord.ext import commands
from .friends import add_friend, remove_friend, get_friends_list, get_summoner_rank
from .WinaLoL.betting import place_bet, get_active_bets
from .WinaLoL.wallet import get_balance
from .dictionnaire import *

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
bot = commands.Bot(command_prefix="??", intents=intents)

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

    **??balance** - Affiche ton solde actuel d'akhy coins.
    Exemple : `??balance`

    **??active_bets** - Affiche la liste des paris encore actifs, du plus gros au plus petit, jusqu'à 30 paris.
    Exemple : `??active_bets`

    **??rankings** - Affiche le classement Elo des invocateurs suivis du meilleur au moins bon.
    Exemple : `??rankings`

    **??aide** - Affiche cette aide détaillée.
    """
    await ctx.send(aide_message)


@bot.command(name='add_summoner', help="Ajoute un ami à la liste des idiots. Usage: ??add_summoner <nom> <tag>")
async def ajouter_ami(ctx, summoner_name: str, tag_line: str):
    add_friend(summoner_name, tag_line)
    await ctx.send(f"Tentative d'ajout de {summoner_name}#{tag_line} à la liste des amis.")

@bot.command(name='remove_summoner', help="Retire un ami de la liste des idiots. Usage: ??remove_summoner <nom> <tag>")
async def supprimer_ami(ctx, summoner_name: str, tag_line: str):
    remove_friend(summoner_name, tag_line)
    await ctx.send(f"{summoner_name}#{tag_line} a été retiré de la liste des amis.")


@bot.command(name='list_summoners', help="Affiche la liste actuelle des idiots.")
async def lister(ctx):
    friends_list = get_friends_list()

    if not friends_list:
        await ctx.send("Il n'y a encore aucun ami.")
    else:
        liste = "\n".join([f"{friend['name']}#{friend['tag']})" for friend in friends_list])
        await ctx.send(f"Voici la liste actuelle des amis : \n{liste}")

@bot.command(name='bet', help="Parier sur la victoire ou la défaite d'un ami. Usage: ??bet <nom_ami> <montant> <win/lose>")
@commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
async def bet(ctx, friend_name: str, amount: int, choice: str):
    user_id = str(ctx.author.id)
    if choice not in ['win', 'lose']:
        await ctx.send("Choix invalide. Utilise 'win' ou 'lose'.")
        return

    success, message = place_bet(user_id, friend_name, amount, choice)
    await ctx.send(message)

@bot.command(name='balance', help="Voir ton solde d'akhy coins.")
async def balance(ctx):
    user_id = str(ctx.author.id)
    balance = get_balance(user_id)
    await ctx.send(f"Tu as {balance} akhy coins.")

@bot.command(name='active_bets', help="Affiche les 30 plus gros paris encore actifs.")
async def active_bets(ctx):
    active_bets_list = get_active_bets()
    
    if not active_bets_list:
        await ctx.send("Il n'y a actuellement aucun pari actif.")
        return

    # Construire le message à envoyer
    bets_message = "**Les 30 plus gros paris encore actifs :**\n"
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
        classement_message = "**Classement Elo des invocateurs suivis (du meilleur au moins bon) :**\n"
        for i, summoner in enumerate(ranked_friends, 1):
            classement_message += f"{i}. **{summoner['name']}** - {summoner['tier']} {summoner['rank']} ({summoner['lp']} LP)\n"

        await ctx.send(classement_message)
