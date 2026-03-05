# -*- coding: utf-8 -*-
"""
GTA RP Discord Bot - Hauptdatei
"""
import discord
from discord.ext import commands
import asyncio
import os
import json
import logging
from config import GUILD_ID, BOT_NAME

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('GTA-RP-Bot')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    logger.info(f'{bot.user.name} ist online!')
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        logger.info(f'{len(synced)} Slash-Commands synchronisiert.')
    except Exception as e:
        logger.error(f'Sync Fehler: {e}')

async def load_cogs():
    cogs = [
        'cogs.ankuendigung',
        'cogs.custom_commands',
        'cogs.role_events'
    ]
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            logger.info(f'Geladen: {cog}')
        except Exception as e:
            logger.error(f'Fehler bei {cog}: {e}')

async def main():
    token = ""
    if os.path.exists("token.txt"):
        with open("token.txt", "r") as f:
            token = f.read().strip()
    
    if not token:
        logger.error("Kein Token in token.txt gefunden!")
        return

    async with bot:
        await load_cogs()
        await bot.start(token)

if __name__ == '__main__':
    asyncio.run(main())
