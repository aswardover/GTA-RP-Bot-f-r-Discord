# -*- coding: utf-8 -*-
# Dieser Cog exportiert beim Bot-Start alle Kanaele und Rollen
# in discord_data.json damit das Dashboard Dropdowns anzeigen kann.
import discord
from discord.ext import commands
import json
import os

DATA_FILE = "discord_data.json"

class DataExporter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.export_data()

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        await self.export_data()

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        await self.export_data()

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        await self.export_data()

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        await self.export_data()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.export_data()

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.export_data()

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        await self.export_data()

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        await self.export_data()

    async def export_data(self):
        data = {"channels": [], "roles": [], "categories": [], "guilds": []}
        for guild in self.bot.guilds:
            online_count = 0
            try:
                online_count = sum(1 for m in guild.members if not m.bot and getattr(m, "status", discord.Status.offline) != discord.Status.offline)
            except Exception:
                online_count = 0

            data["guilds"].append(
                {
                    "id": str(guild.id),
                    "name": guild.name,
                    "member_count": int(guild.member_count or 0),
                    "online_count": int(online_count),
                }
            )

            for channel in sorted(guild.text_channels, key=lambda c: c.position):
                data["channels"].append({
                    "id": str(channel.id),
                    "name": f"#{channel.name}",
                    "category": channel.category.name if channel.category else "Ohne Kategorie"
                })
            for channel in sorted(guild.voice_channels, key=lambda c: c.position):
                data["channels"].append({
                    "id": str(channel.id),
                    "name": f"🔊 {channel.name}",
                    "category": channel.category.name if channel.category else "Ohne Kategorie"
                })
            for role in sorted(guild.roles, key=lambda r: r.position, reverse=True):
                if role.name == "@everyone":
                    continue
                data["roles"].append({
                    "id": str(role.id),
                    "name": role.name
                })
            for cat in guild.categories:
                data["categories"].append({
                    "id": str(cat.id),
                    "name": cat.name
                })
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

async def setup(bot):
    await bot.add_cog(DataExporter(bot))
