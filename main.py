# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import os
import json
import logging
from config import TOKEN, SETTINGS_FILE

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('GTA-RP-Bot')

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.guilds = True
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    logger.info(f'Cog geladen: {filename}')
                except Exception as e:
                    logger.error(f'Fehler beim Laden von {filename}: {e}')

    async def on_ready(self):
        logger.info(f'{self.user} ist bereit und online!')
        try:
            # Globaler Sync fuer alle Server
            synced = await self.tree.sync()
            logger.info(f'{len(synced)} globale Slash-Befehle synchronisiert!')
        except Exception as e:
            logger.error(f'Fehler beim Synchronisieren: {e}')

bot = MyBot()

if __name__ == "__main__":
    bot.run(TOKEN)
