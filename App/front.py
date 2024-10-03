import discord
import math
from .dictionnaire import *    

async def ping_gambler_role(channel):
    # Recherche du rôle dans le serveur
    guild = channel.guild  # Récupère le serveur (guild) où le canal existe
    gambler_role = discord.utils.get(guild.roles, name=CONFIG['ROLE'])
    
    # Vérification si le rôle existe
    if gambler_role is not None:
        return f"{gambler_role.mention} faites vos jeux !"
    else:
        print("Le rôle 'Gambler' n'a pas été trouvé sur ce serveur.")
        return ""
    
async def afficher_resultat_partie(channel, summoner_name, result, winners, losers, summoner_ratings, bot):
    # Création de l'embed pour le résultat de la partie
    embed = discord.Embed(
        title="🎮 Game results",
        color=discord.Color.green() if result == 'win' else discord.Color.red()
    )
    
    # Ajouter les informations générales du joueur
    embed.add_field(name="Summoner", value=summoner_name, inline=True)
    embed.add_field(name="Result", value="Victory" if result == 'win' else "Defeat", inline=True)

    # Calcul des gains pour chaque parieur gagnant
    gain_text = ""
    for winner in winners:
        user = await bot.fetch_user(winner['user_id'])  # Récupérer l'utilisateur Discord
        gain_amount = int(winner['amount'] * (math.exp(2.5 * (1 - summoner_ratings.get(summoner_name, 0.5)) - (2.5 * summoner_ratings.get(summoner_name, 0.5)) - 0.15) + 1)) if result == 'win' else int(winner['amount'] * (math.exp((2.5 * summoner_ratings.get(summoner_name, 0.5)) - 2.5 * (1 - summoner_ratings.get(summoner_name, 0.5)) - 0.15) + 1))
        gain_text += f"{user.mention} a gagné {gain_amount} akhy coins.\n"
    
    if gain_text:
        embed.add_field(name="🤑 Winners", value=gain_text, inline=False)

    # Liste des perdants
    loss_text = ""
    for loser in losers:
        user = await bot.fetch_user(loser['user_id'])  # Récupérer l'utilisateur Discord
        loss_text += f"{user.mention} a perdu son pari.\n"
    
    if loss_text:
        embed.add_field(name="😢 Losers", value=loss_text, inline=False)

    embed.set_footer(text="Partie terminée")
    
    # Envoyer l'embed au channel
    await channel.send(embed=embed)

async def afficher_lancement_partie(channel, summoner_name, summoner_ratings, gambler_ping_message, gameQueueConfigId, draft):
    # Calcul des cotes
    cote_win = round((math.exp(2.5 * (1 - summoner_ratings.get(summoner_name, 0.5)) - (2.5 * summoner_ratings.get(summoner_name, 0.5)) - 0.15) + 1), 2)
    cote_lose = round((math.exp((2.5 * summoner_ratings.get(summoner_name, 0.5)) - 2.5 * (1 - summoner_ratings.get(summoner_name, 0.5)) - 0.15) + 1), 2)

    # Création de l'embed pour l'annonce du lancement de la partie
    embed = discord.Embed(
        title="🎮 Nouveau Match en cours !",
        description=f"🎲 **{gambler_ping_message}** 🎲",
        color=discord.Color.blue()
    )

    # Ajouter le nom du joueur qui a lancé la partie
    embed.add_field(
        name="Invocateur en jeu",
        value=f"**{summoner_name}** vient de lancer une partie de **League of Legends** !",
        inline=False
    )

    # Ajouter les cotes de pari
    embed.add_field(
        name="Cotes actuelles",
        value=f"Victoire (Win) : **{cote_win}**\nDéfaite (Lose) : **{cote_lose}**",
        inline=False
    )

    # Rappel des paris
    embed.add_field(
        name="Pariez maintenant !",
        value=f"💰 **Utilisez la commande :** `??bet <nom_ami> <montant> <win/lose>`\n"
              f"⏳ **Les paris sont ouverts pendant 3 minutes !**",
        inline=False
    )

    # Ajout des informations sur le mode de jeu
    embed.add_field(
        name="Mode de jeu",
        value=get_game_mode_display(gameQueueConfigId),
        inline=False
    )

    # Structuration de la draft en deux colonnes (équipes 1 et 2)
    embed.add_field(
        name="Équipe 1",
        value="\n".join(draft[:5]),  # Liste des joueurs de l'équipe 1
        inline=True
    )
    embed.add_field(
        name="Équipe 2",
        value="\n".join(draft[5:]),  # Liste des joueurs de l'équipe 2
        inline=True
    )

    # Envoyer l'embed au channel
    await channel.send(embed=embed)

def get_game_mode_display(gameQueueConfigId):
    queue_mapping = {
        400: "Normal Draft",
        420: "Ranked Solo/Duo",
        430: "Normal Blind",
        440: "Ranked Flex",
        450: "ARAM",
        700: "Clash",
        830: "Co-op vs. AI (Beginner)",
        840: "Co-op vs. AI (Intermediate)",
        850: "Co-op vs. AI (Intro)",
        900: "URF",
        1020: "One for All",
        1200: "Nexus Blitz",
        1400: "Ultimate Spellbook",
        # Add more mappings as needed
    }
    return queue_mapping.get(gameQueueConfigId, "Unknown Queue Type")