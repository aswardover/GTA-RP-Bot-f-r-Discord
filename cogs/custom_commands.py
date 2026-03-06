# -*- coding: utf-8 -*-
import json
import os
import threading
from typing import Dict, Any, List
import discord
from discord import app_commands
from discord.ext import commands
import config
from embeds import create_embed

GUILD_ID = config.GUILD_ID
SETTINGS_FILE = "settings.json"

def load_settings() -> Dict[str, Any]:
    if not os.path.exists(SETTINGS_FILE): return {}
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f: return json.load(f)

class CustomCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="befoerdern", description="Befördert einen User")
    async def befoerdern(self, interaction: discord.Interaction, member: discord.Member, neue_rolle: discord.Role):
        settings = load_settings()
        if not settings.get("befoerdern_enabled", True):
            await interaction.response.send_message("Deaktiviert.", ephemeral=True)
            return
        await member.add_roles(neue_rolle)
        await interaction.response.send_message(f"{member.mention} befördert zu {neue_rolle.mention}!", ephemeral=True)

    @app_commands.command(name="rankup", description="Alte Rolle weg, neue Rolle her")
    async def rankup(self, interaction: discord.Interaction, member: discord.Member, alte_rolle: discord.Role, neue_rolle: discord.Role):
        settings = load_settings()
        if not settings.get("rankup_enabled", True):
            await interaction.response.send_message("Deaktiviert.", ephemeral=True)
            return
        await member.remove_roles(alte_rolle)
        await member.add_roles(neue_rolle)
        await interaction.response.send_message(f"Rankup: {member.mention} ist jetzt {neue_rolle.mention}!", ephemeral=True)

    @app_commands.command(name="drank", description="Rolle entfernen")
    async def drank(self, interaction: discord.Interaction, member: discord.Member, rolle: discord.Role):
        await member.remove_roles(rolle)
        await interaction.response.send_message(f"Rolle {rolle.name} von {member.mention} entfernt.", ephemeral=True)

    @app_commands.command(name="einstellen", description="User einstellen")
    async def einstellen(self, interaction: discord.Interaction, member: discord.Member, rolle: discord.Role):
        await member.add_roles(rolle)
        await interaction.response.send_message(f"{member.mention} wurde eingestellt.", ephemeral=True)

    @app_commands.command(name="kuendigen", description="User kündigen")
    async def kuendigen(self, interaction: discord.Interaction, member: discord.Member, rolle: discord.Role):
        await member.remove_roles(rolle)
        await interaction.response.send_message(f"{member.mention} wurde gekündigt.", ephemeral=True)

    @app_commands.command(name="clear", description="Nachrichten löschen")
    async def clear(self, interaction: discord.Interaction, anzahl: int):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("Keine Rechte!", ephemeral=True)
            return
        await interaction.channel.purge(limit=anzahl)
        await interaction.response.send_message(f"{anzahl} Nachrichten gelöscht.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(CustomCommands(bot))
