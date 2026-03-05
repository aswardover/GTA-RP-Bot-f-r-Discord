# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import json
import os
import config
from embeds import create_embed

SETTINGS_FILE = "settings.json"
GUILD_ID = config.GUILD_ID


def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        settings = load_settings()
        if not settings.get("welcome_enabled", False):
            return
        channel_id = settings.get("welcome_channel_id")
        if not channel_id:
            return
        channel = member.guild.get_channel(int(channel_id))
        if not channel or not isinstance(channel, discord.TextChannel):
            return
        msg_template = settings.get("welcome_message", "Willkommen auf dem Server, {user}!")
        msg = msg_template.format(
            user=member.mention,
            server=member.guild.name,
            name=member.display_name
        )
        embed = create_embed(
            title="🎉 Neues Mitglied!",
            description=msg,
            color=0x10b981
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        settings = load_settings()
        if not settings.get("goodbye_enabled", False):
            return
        channel_id = settings.get("goodbye_channel_id")
        if not channel_id:
            return
        channel = member.guild.get_channel(int(channel_id))
        if not channel or not isinstance(channel, discord.TextChannel):
            return
        msg_template = settings.get("goodbye_message", "{name} hat den Server verlassen.")
        msg = msg_template.format(
            user=member.mention,
            server=member.guild.name,
            name=member.display_name
        )
        embed = create_embed(
            title="👋 Auf Wiedersehen!",
            description=msg,
            color=0xef4444
        )
        await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Welcome(bot))
