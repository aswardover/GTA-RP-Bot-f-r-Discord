# -*- coding: utf-8 -*-
import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
from datetime import datetime, timedelta
from embeds import success_embed, error_embed
from database import add_sanktion, get_sanktionen, remove_sanktion, add_warn, get_warns, remove_warn

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_expirations.start()

    def cog_unload(self):
        self.check_expirations.cancel()

    @tasks.loop(minutes=5)
    async def check_expirations(self):
        sanktionen = await get_sanktionen()
        now = datetime.now()
        for s in sanktionen:
            if datetime.fromisoformat(s[5]) <= now:  # end_time
                guild = self.bot.get_guild(int(s[6]))  # guild_id
                if guild:
                    member = guild.get_member(int(s[1]))  # user_id
                    if member and s[7]:  # role_id
                        role = guild.get_role(int(s[7]))
                        if role and role in member.roles:
                            await member.remove_roles(role)
                            # Log
                            log_channel = self.bot.get_channel(int(s[8])) if s[8] else None
                            if log_channel:
                                embed = discord.Embed(title="Sanktion abgelaufen", color=discord.Color.green())
                                embed.add_field(name="User", value=f"<@{s[1]}>")
                                embed.add_field(name="Grund", value=s[3])
                                await log_channel.send(embed=embed)
                await remove_sanktion(s[0])

        warns = await get_warns()
        for w in warns:
            if datetime.fromisoformat(w[4]) <= now:
                await remove_warn(w[0])

    @app_commands.command(name="sanktion", description="Vergebe eine Sanktion")
    @app_commands.describe(user="Der User", betrag="Betrag", grund="Grund", dauer="Dauer in Tagen")
    async def sanktion(self, interaction: discord.Interaction, user: discord.Member, betrag: str, grund: str, dauer: int):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message(embed=error_embed("Keine Berechtigung!"), ephemeral=True)
            return

        settings = self.bot.get_settings()
        role_id = settings.get("sanktion_role_id")
        if not role_id:
            await interaction.response.send_message(embed=error_embed("Sanktions-Rolle nicht konfiguriert!"), ephemeral=True)
            return

        role = interaction.guild.get_role(int(role_id))
        if not role:
            await interaction.response.send_message(embed=error_embed("Rolle nicht gefunden!"), ephemeral=True)
            return

        await user.add_roles(role)
        end_time = datetime.now() + timedelta(days=dauer)

        embed = discord.Embed(
            title=settings.get("sanktion_embed_title", "🚫 Sanktion"),
            description=settings.get("sanktion_embed_description", "User: {user}\nBetrag: {betrag}\nGrund: {grund}\nDauer: {dauer} Tage").format(
                user=user.mention, betrag=betrag, grund=grund, dauer=dauer
            ),
            color=int(settings.get("sanktion_embed_color", "#ff0000").lstrip("#"), 16)
        )
        embed.set_footer(text=settings.get("sanktion_embed_footer", "Sanktion erteilt"))

        await interaction.response.send_message(embed=embed)

        await add_sanktion(str(user.id), betrag, grund, dauer, end_time.isoformat(), str(interaction.guild.id), role_id, settings.get("moderation_log_channel"))

    @app_commands.command(name="warn", description="Vergebe eine Warnung")
    @app_commands.describe(user="Der User", grund="Grund", dauer="Dauer in Tagen")
    async def warn(self, interaction: discord.Interaction, user: discord.Member, grund: str, dauer: int):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message(embed=error_embed("Keine Berechtigung!"), ephemeral=True)
            return

        settings = self.bot.get_settings()
        end_time = datetime.now() + timedelta(days=dauer)

        embed = discord.Embed(
            title=settings.get("warn_embed_title", "⚠️ Warnung"),
            description=settings.get("warn_embed_description", "User: {user}\nGrund: {grund}\nDauer: {dauer} Tage").format(
                user=user.mention, grund=grund, dauer=dauer
            ),
            color=int(settings.get("warn_embed_color", "#ffa500").lstrip("#"), 16)
        )
        embed.set_footer(text=settings.get("warn_embed_footer", "Warnung erteilt"))

        await interaction.response.send_message(embed=embed)

        await add_warn(str(user.id), grund, dauer, end_time.isoformat(), str(interaction.guild.id), settings.get("moderation_log_channel"))

async def setup(bot):
    await bot.add_cog(Moderation(bot))