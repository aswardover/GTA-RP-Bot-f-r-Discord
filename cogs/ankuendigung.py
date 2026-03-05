# -*- coding: utf-8 -*-
import discord
from discord.ext import commands, tasks
from discord import app_commands
import datetime
import json
import os
from embeds import success_embed, error_embed

class Ankuendigung(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_announce_trigger.start()

    def cog_unload(self):
        self.check_announce_trigger.cancel()

    @tasks.loop(minutes=1)
    async def check_announce_trigger(self):
        # Hier könnte Logik für zeitgesteuerte Ankündigungen rein
        pass

    @app_commands.command(name="ankündigen", description="Sendet eine Ankündigung in einen Kanal")
    @app_commands.describe(kanal="Der Kanal für die Ankündigung", nachricht="Die Nachricht")
    async def ankuendigen(self, interaction: discord.Interaction, kanal: discord.TextChannel, nachricht: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(embed=error_embed("Du hast keine Berechtigung dafür!"), ephemeral=True)
            return

        embed = discord.Embed(
            title="📢 Ankündigung",
            description=nachricht,
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Gesendet von {interaction.user.display_name}")
        
        await kanal.send(embed=embed)
        await interaction.response.send_message(embed=success_embed(f"Ankündigung in {kanal.mention} gesendet!"), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Ankuendigung(bot))
