# -*- coding: utf-8 -*-
# Dieser Cog exportiert beim Bot-Start alle Kanaele und Rollen
# in discord_data.json damit das Dashboard Dropdowns anzeigen kann.
import discord
from discord.ext import commands
import json
import os
import datetime

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
        data = {"channels": [], "roles": [], "categories": [], "guilds": [], "meta": {}}
        for guild in self.bot.guilds:
            online_count = 0
            try:
                online_count = sum(1 for m in guild.members if not m.bot and getattr(m, "status", discord.Status.offline) != discord.Status.offline)
            except Exception:
                online_count = 0

            members = []
            try:
                for member in guild.members:
                    if member.bot:
                        continue
                    member_status = str(getattr(member, "status", discord.Status.offline))
                    members.append(
                        {
                            "id": str(member.id),
                            "name": str(member.name),
                            "display_name": str(member.display_name),
                            "status": member_status,
                            "online": member_status != "offline",
                        }
                    )
            except Exception:
                members = []

            members.sort(key=lambda item: str(item.get("display_name") or item.get("name") or "").lower())

            data["guilds"].append(
                {
                    "id": str(guild.id),
                    "name": guild.name,
                    "member_count": int(guild.member_count or 0),
                    "online_count": int(online_count),
                    "members": members,
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

        data["meta"] = {
            "exported_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "bot_user": str(getattr(self.bot.user, "name", "")) if self.bot.user else "",
            "bot_id": str(getattr(self.bot.user, "id", "")) if self.bot.user else "",
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

async def setup(bot):
    await bot.add_cog(DataExporter(bot))
