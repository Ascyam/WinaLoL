import asyncio
import os

from dotenv import load_dotenv

from App.interactions import bot
from App.tracker import notify_if_friends_in_game

load_dotenv()  # Charger les variables d'environnement
TOKEN = os.getenv('TOKEN')


@bot.event
async def on_ready():
    print(f'{bot.user} est connecté à Discord !')
    asyncio.create_task(notify_if_friends_in_game())


bot.run(TOKEN)
