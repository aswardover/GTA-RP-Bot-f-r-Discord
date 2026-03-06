# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from embeds import success_embed, error_embed

class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear", description="Loescht eine bestimmte Anzahl an Nachrichten")
    @app_commands.describe(anzahl="Anzahl der Nachrichten (1-100)")
    async def clear(self, interaction: discord.Interaction, anzahl: int):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(embed=error_embed("Keine Berechtigung!"), ephemeral=True)
            return

        if anzahl < 1 or anzahl > 100:
            await interaction.response.send_message(embed=error_embed("Bitte eine Zahl zwischen 1 und 100 angeben."), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=anzahl)
        await interaction.followup.send(embed=success_embed(f"{len(deleted)} Nachrichten wurden geloescht!"))

    @app_commands.command(name="kick", description="Kickt einen Benutzer vom Server")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, grund: str = "Kein Grund angegeben"):
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message(embed=error_embed("Keine Berechtigung!"), ephemeral=True)
            return

        await member.kick(reason=grund)
        await interaction.response.send_message(embed=success_embed(f"{member.name} wurde gekickt. Grund: {grund}"))

async def setup(bot):
    await bot.add_cog(Management(bot))
