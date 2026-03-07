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
        await self._run_announcement(interaction, kanal, nachricht)

    @app_commands.command(name="ankündigung", description="Sendet eine Ankündigung in einen Kanal")
    @app_commands.describe(kanal="Der Kanal für die Ankündigung", nachricht="Die Nachricht")
    async def ankuendigung(self, interaction: discord.Interaction, kanal: discord.TextChannel, nachricht: str):
        await self._run_announcement(interaction, kanal, nachricht)

    async def _run_announcement(self, interaction: discord.Interaction, kanal: discord.TextChannel, nachricht: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(embed=error_embed("Du hast keine Berechtigung dafür!"), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        try:
            settings = self.bot.get_settings()
            if settings.get("announce_embed_enabled", False):
                color_raw = str(settings.get("announce_embed_color", "#38bdf8")).lstrip("#")
                try:
                    color_value = int(color_raw, 16)
                except ValueError:
                    color_value = int("38bdf8", 16)

                embed = discord.Embed(
                    title=settings.get("announce_embed_title", "📢 Ankündigung"),
                    description=settings.get("announce_embed_description", "{text}").format(text=nachricht),
                    color=color_value
                )
                embed.set_footer(text=settings.get("announce_embed_footer", f"Gesendet von {interaction.user.display_name}"))
                await kanal.send(embed=embed)
            else:
                await kanal.send(nachricht)

            await interaction.followup.send(embed=success_embed(f"Ankündigung in {kanal.mention} gesendet!"), ephemeral=True)
        except Exception as e:
            await interaction.followup.send(embed=error_embed(f"Ankündigung fehlgeschlagen: {e}"), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Ankuendigung(bot))
