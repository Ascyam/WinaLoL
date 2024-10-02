import discord
import math
from .dictionnaire import *    

async def ping_gambler_role(channel):
    # Recherche du rôle dans le serveur
    guild = channel.guild  # Récupère le serveur (guild) où le canal existe
    gambler_role = discord.utils.get(guild.roles, name=CONFIG['ROLE'])
    
    # Vérification si le rôle existe
    if gambler_role is not None:
        return f"{gambler_role.mention} Nouveau match !"
    else:
        print("Le rôle 'Gambler' n'a pas été trouvé sur ce serveur.")
        return ""
    
async def afficher_resultat_partie(channel, summoner_name, result, winners, losers, summoner_ratings, bot):
    # Création de l'embed pour le résultat de la partie
    embed = discord.Embed(
        title="Game results",
        description="**Victory**" if result == 'win' else "**Defeat**",
        color=discord.Color.green() if result == 'win' else discord.Color.red()
    )
    
    # Ajouter les informations générales du joueur
    embed.add_field(name="Summoner", value=summoner_name, inline=True)
    embed.add_field(name="Result", value="Victory" if result == 'win' else "Defeat", inline=True)

    # Calcul des gains pour chaque parieur gagnant
    gain_text = ""
    for winner in winners:
        user = await bot.fetch_user(winner['user_id'])  # Récupérer l'utilisateur Discord
        gain_amount = int(winner['amount'] * (math.exp(2.5 * (1 - summoner_ratings.get(summoner_name, 0.5)) - (2.5 * summoner_ratings.get(summoner_name, 0.5)) - 0.2) + 1)) if result == 'win' else int(winner['amount'] * (math.exp((2.5 * summoner_ratings.get(summoner_name, 0.5)) - 2.5 * (1 - summoner_ratings.get(summoner_name, 0.5)) - 0.2) + 1))
        gain_text += f"{user.mention} a gagné {gain_amount} akhy coins.\n"
    
    if gain_text:
        embed.add_field(name="Winners", value=gain_text, inline=False)

    # Liste des perdants
    loss_text = ""
    for loser in losers:
        user = await bot.fetch_user(loser['user_id'])  # Récupérer l'utilisateur Discord
        loss_text += f"{user.mention} a perdu son pari.\n"
    
    if loss_text:
        embed.add_field(name="Losers", value=loss_text, inline=False)

    embed.set_footer(text="Partie terminée")
    
    # Envoyer l'embed au channel
    await channel.send(embed=embed)