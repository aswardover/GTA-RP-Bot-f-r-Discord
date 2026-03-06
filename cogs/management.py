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

    @app_commands.command(name="kick_user", description="Kickt einen Benutzer vom Server")
    async def kick_user(self, interaction: discord.Interaction, member: discord.Member, grund: str = "Kein Grund angegeben"):
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message(embed=error_embed("Keine Berechtigung!"), ephemeral=True)
            return
        await member.kick(reason=grund)
        await interaction.response.send_message(embed=success_embed(f"{member.name} wurde gekickt. Grund: {grund}"))

async def setup(bot):
    await bot.add_cog(Management(bot))
