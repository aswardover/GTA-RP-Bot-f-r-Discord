# -*- coding: utf-8 -*-
import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime
import json
import os
import config
from embeds import create_embed, success_embed, error_embed

SETTINGS_FILE = "settings.json"
GUILD_ID = config.GUILD_ID


def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_settings(data: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


class Ankuendigung(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.check_announce_trigger.start()

    def cog_unload(self):
        self.check_announce_trigger.cancel()

    def _get_announce_settings(self) -> dict:
        settings = load_settings()
        return {
            "title": settings.get("announce_title", "📢 Ankuendigung"),
            "description_template": settings.get("announce_description", "{text}"),
            "color_hex": settings.get("announce_color", "#38bdf8"),
            "ping_role_id": settings.get("announce_ping_role_id"),
            "allowed_role_ids": settings.get("announce_allowed_roles", []),
        }

    @app_commands.command(name="ankuendigung", description="Sendet eine Ankuendigung")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(text="Inhalt der Ankuendigung")
    async def ankuendigung_cmd(self, interaction: discord.Interaction, text: str):
        settings = self._get_announce_settings()
        allowed_role_ids = settings["allowed_role_ids"]
        if allowed_role_ids:
            member = interaction.user
            if not isinstance(member, discord.Member):
                await interaction.response.send_message(embed=error_embed("Fehler", "Nur auf Servern nutzbar."), ephemeral=True)
                return
            user_role_ids = {r.id for r in member.roles}
            if not user_role_ids.intersection(set(allowed_role_ids)):
                await interaction.response.send_message(embed=error_embed("Keine Berechtigung", "Du darfst diesen Command nicht nutzen."), ephemeral=True)
                return

        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message(embed=error_embed("Fehler", "Ungueltiger Channel."), ephemeral=True)
            return

        now = datetime.now().strftime("%d.%m.%Y %H:%M")
        desc = settings["description_template"].format(
            text=text,
            user=interaction.user.mention,
            server=interaction.guild.name if interaction.guild else "Server",
            zeit=now
        )
        try:
            color_int = int(settings["color_hex"].replace("#", ""), 16)
        except Exception:
            color_int = None

        embed = create_embed(title=settings["title"], description=desc, color=color_int)
        ping_text = ""
        if settings["ping_role_id"]:
            role = interaction.guild.get_role(settings["ping_role_id"])
            if role:
                ping_text = role.mention

        await channel.send(content=ping_text or None, embed=embed)
        await interaction.response.send_message(embed=success_embed("Gesendet", f"Ankuendigung in {channel.mention} gepostet."), ephemeral=True)

    @tasks.loop(seconds=5)
    async def check_announce_trigger(self):
        await self.bot.wait_until_ready()
        settings = load_settings()
        trigger = settings.get("announce_trigger")
        if not trigger or not isinstance(trigger, dict):
            return

        channel_id = trigger.get("channel_id")
        text = trigger.get("text") or ""
        title = trigger.get("title") or settings.get("announce_title", "📢 Ankuendigung")
        channel = self.bot.get_channel(channel_id) if channel_id else None
        if not channel or not isinstance(channel, discord.TextChannel):
            settings["announce_trigger"] = None
            save_settings(settings)
            return

        desc_tpl = settings.get("announce_description", "{text}")
        color_hex = settings.get("announce_color", "#38bdf8")
        now = datetime.now().strftime("%d.%m.%Y %H:%M")
        desc = desc_tpl.format(text=text, user="Dashboard", server=channel.guild.name, zeit=now)
        try:
            color_int = int(color_hex.replace("#", ""), 16)
        except Exception:
            color_int = None

        embed = create_embed(title=title, description=desc, color=color_int)
        ping_role_id = settings.get("announce_ping_role_id")
        ping_text = ""
        if ping_role_id:
            role = channel.guild.get_role(ping_role_id)
            if role:
                ping_text = role.mention

        await channel.send(content=ping_text or None, embed=embed)
        settings["announce_trigger"] = None
        save_settings(settings)

    @check_announce_trigger.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Ankuendigung(bot))
