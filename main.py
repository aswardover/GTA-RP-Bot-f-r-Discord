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

    def get_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    async def setup_hook(self):
        # Alle Cogs automatisch laden
        if not os.path.exists('./cogs'):
            os.makedirs('./cogs')
            
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    logger.info(f'Cog geladen: {filename}')
                except Exception as e:
                    logger.error(f'Fehler beim Laden von {filename}: {e}')

    async def on_ready(self):
        logger.info(f'{self.user} ist bereit und online!')

bot = MyBot()

if __name__ == "__main__":
    bot.run(TOKEN)
