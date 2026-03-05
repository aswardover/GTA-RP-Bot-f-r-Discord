# -*- coding: utf-8 -*-
"""
GTA RP Discord Bot - Hauptdatei
Starte den Bot mit: python main.py
"""
import discord
from discord.ext import commands
import asyncio
import os
import json
import logging
from config import GUILD_ID, BOT_NAME

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger('GTA-RP-Bot')

# Settings laden
def load_settings():
    try:
        with open('settings.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Bot Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True

# Bot erstellen
bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    help_command=None
)

@bot.event
async def on_ready():
    logger.info(f'{bot.user.name} ist online!')
    logger.info(f'Guild ID: {GUILD_ID}')
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f'GTA RP Server'
        )
    )
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        logger.info(f'{len(synced)} Slash-Commands synchronisiert.')
    except Exception as e:
        logger.error(f'Fehler beim Synchronisieren: {e}')

async def load_cogs():
    cog_files = [
        'cogs.ankuendigung',
        'cogs.custom_commands',
    ]
    for cog in cog_files:
        try:
            await bot.load_extension(cog)
            logger.info(f'Cog geladen: {cog}')
        except Exception as e:
            logger.error(f'Fehler beim Laden von {cog}: {e}')

async def main():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        try:
            with open('token.txt', 'r') as f:
                token = f.read().strip()
        except FileNotFoundError:
            logger.error('Kein Token gefunden! Setze DISCORD_TOKEN als Umgebungsvariable oder erstelle token.txt')
            return
    async with bot:
        await load_cogs()
        await bot.start(token)

if __name__ == '__main__':
    asyncio.run(main())
