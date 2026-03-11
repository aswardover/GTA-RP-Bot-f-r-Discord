# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
from embeds import success_embed, error_embed


class ServerTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _enabled(self):
        settings = self.bot.get_settings()
        return settings.get("server_tools_enabled", True)

    def _tool_enabled(self, key: str):
        settings = self.bot.get_settings()
        legacy_default = settings.get("server_tools_enabled", True)
        return settings.get(key, legacy_default)

    @app_commands.command(name="slowmode", description="Setzt Slowmode fuer einen Textkanal")
    @app_commands.describe(channel="Zielkanal", seconds="Sekunden (0-21600)")
    async def slowmode(self, interaction: discord.Interaction, channel: discord.TextChannel, seconds: int):
        if not self._tool_enabled("server_tools_slowmode_enabled"):
            await interaction.response.send_message(embed=error_embed("/slowmode ist deaktiviert."), ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message(embed=error_embed("Keine Berechtigung (Manage Channels)."), ephemeral=True)
            return
        if seconds < 0 or seconds > 21600:
            await interaction.response.send_message(embed=error_embed("Sekunden muessen zwischen 0 und 21600 liegen."), ephemeral=True)
            return

        await channel.edit(slowmode_delay=seconds)
        text = "deaktiviert" if seconds == 0 else f"auf {seconds}s gesetzt"
        await interaction.response.send_message(embed=success_embed(f"Slowmode in {channel.mention} {text}."), ephemeral=True)

    @app_commands.command(name="lock", description="Sperrt einen Textkanal fuer @everyone")
    @app_commands.describe(channel="Zielkanal")
    async def lock(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not self._tool_enabled("server_tools_lock_enabled"):
            await interaction.response.send_message(embed=error_embed("/lock ist deaktiviert."), ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message(embed=error_embed("Keine Berechtigung (Manage Channels)."), ephemeral=True)
            return

        overwrite = channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message(embed=success_embed(f"Kanal {channel.mention} wurde gesperrt."), ephemeral=True)

    @app_commands.command(name="unlock", description="Entsperrt einen Textkanal fuer @everyone")
    @app_commands.describe(channel="Zielkanal")
    async def unlock(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not self._tool_enabled("server_tools_unlock_enabled"):
            await interaction.response.send_message(embed=error_embed("/unlock ist deaktiviert."), ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message(embed=error_embed("Keine Berechtigung (Manage Channels)."), ephemeral=True)
            return

        overwrite = channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = None
        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message(embed=success_embed(f"Kanal {channel.mention} wurde entsperrt."), ephemeral=True)

    @app_commands.command(name="timeout", description="Setzt ein Timeout fuer ein Mitglied")
    @app_commands.describe(member="Mitglied", minutes="Dauer in Minuten", reason="Grund")
    async def timeout_member(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Kein Grund"):
        if not self._tool_enabled("server_tools_timeout_enabled"):
            await interaction.response.send_message(embed=error_embed("/timeout ist deaktiviert."), ephemeral=True)
            return
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message(embed=error_embed("Keine Berechtigung (Moderate Members)."), ephemeral=True)
            return
        if minutes < 1 or minutes > 40320:
            await interaction.response.send_message(embed=error_embed("Minuten muessen zwischen 1 und 40320 liegen."), ephemeral=True)
            return

        try:
            await member.timeout(timedelta(minutes=minutes), reason=reason)
            await interaction.response.send_message(embed=success_embed(f"{member.mention} hat jetzt Timeout ({minutes}m)."), ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(embed=error_embed(f"Timeout fehlgeschlagen: {e}"), ephemeral=True)

    @app_commands.command(name="untimeout", description="Entfernt ein Timeout von einem Mitglied")
    @app_commands.describe(member="Mitglied", reason="Grund")
    async def untimeout_member(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Kein Grund"):
        if not self._tool_enabled("server_tools_untimeout_enabled"):
            await interaction.response.send_message(embed=error_embed("/untimeout ist deaktiviert."), ephemeral=True)
            return
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message(embed=error_embed("Keine Berechtigung (Moderate Members)."), ephemeral=True)
            return

        try:
            await member.timeout(None, reason=reason)
            await interaction.response.send_message(embed=success_embed(f"Timeout von {member.mention} entfernt."), ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(embed=error_embed(f"Untimeout fehlgeschlagen: {e}"), ephemeral=True)


async def setup(bot):
    await bot.add_cog(ServerTools(bot))
