# -*- coding: utf-8 -*-
import discord
from discord.ext import commands, tasks
import datetime
import asyncio

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_queue = asyncio.Queue()
        self.batch_send.start()

    def cog_unload(self):
        self.batch_send.cancel()

    @tasks.loop(seconds=10)
    async def batch_send(self):
        logs = []
        while not self.log_queue.empty():
            logs.append(await self.log_queue.get())
        if logs:
            settings = self.bot.get_settings()
            log_channel_id = settings.get("logging_channel_id")
            if log_channel_id:
                log_channel = self.bot.get_channel(int(log_channel_id))
                if log_channel:
                    for title, description in logs:
                        embed = discord.Embed(title=title, description=description, color=discord.Color.blue(), timestamp=datetime.datetime.now())
                        await log_channel.send(embed=embed)

    async def log_event(self, title, description):
        await self.log_queue.put((title, description))

async def setup(bot):
    await bot.add_cog(Logging(bot))