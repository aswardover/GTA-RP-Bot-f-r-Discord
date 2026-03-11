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

    async def _respond(self, interaction: discord.Interaction, text: str, ok: bool = True, ephemeral: bool = True):
        settings = self.bot.get_settings()
        send_as_embed = bool(settings.get("server_tools_send_as_embed", True))
        if send_as_embed:
            embed = success_embed(text) if ok else error_embed(text)
            await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
        else:
            prefix = "✅ " if ok else "❌ "
            await interaction.response.send_message(content=f"{prefix}{text}", ephemeral=ephemeral)

    @app_commands.command(name="slowmode", description="Setzt Slowmode fuer einen Textkanal")
    @app_commands.describe(channel="Zielkanal", seconds="Sekunden (0-21600)")
    async def slowmode(self, interaction: discord.Interaction, channel: discord.TextChannel, seconds: int):
        if not self._tool_enabled("server_tools_slowmode_enabled"):
            await self._respond(interaction, "/slowmode ist deaktiviert.", ok=False, ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_channels:
            await self._respond(interaction, "Keine Berechtigung (Manage Channels).", ok=False, ephemeral=True)
            return
        if seconds < 0 or seconds > 21600:
            await self._respond(interaction, "Sekunden muessen zwischen 0 und 21600 liegen.", ok=False, ephemeral=True)
            return

        await channel.edit(slowmode_delay=seconds)
        text = "deaktiviert" if seconds == 0 else f"auf {seconds}s gesetzt"
        await self._respond(interaction, f"Slowmode in {channel.mention} {text}.", ok=True, ephemeral=True)

    @app_commands.command(name="lock", description="Sperrt einen Textkanal fuer @everyone")
    @app_commands.describe(channel="Zielkanal")
    async def lock(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not self._tool_enabled("server_tools_lock_enabled"):
            await self._respond(interaction, "/lock ist deaktiviert.", ok=False, ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_channels:
            await self._respond(interaction, "Keine Berechtigung (Manage Channels).", ok=False, ephemeral=True)
            return

        overwrite = channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await self._respond(interaction, f"Kanal {channel.mention} wurde gesperrt.", ok=True, ephemeral=True)

    @app_commands.command(name="unlock", description="Entsperrt einen Textkanal fuer @everyone")
    @app_commands.describe(channel="Zielkanal")
    async def unlock(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not self._tool_enabled("server_tools_unlock_enabled"):
            await self._respond(interaction, "/unlock ist deaktiviert.", ok=False, ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_channels:
            await self._respond(interaction, "Keine Berechtigung (Manage Channels).", ok=False, ephemeral=True)
            return

        overwrite = channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = None
        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await self._respond(interaction, f"Kanal {channel.mention} wurde entsperrt.", ok=True, ephemeral=True)

    @app_commands.command(name="timeout", description="Setzt ein Timeout fuer ein Mitglied")
    @app_commands.describe(member="Mitglied", minutes="Dauer in Minuten", reason="Grund")
    async def timeout_member(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Kein Grund"):
        if not self._tool_enabled("server_tools_timeout_enabled"):
            await self._respond(interaction, "/timeout ist deaktiviert.", ok=False, ephemeral=True)
            return
        if not interaction.user.guild_permissions.moderate_members:
            await self._respond(interaction, "Keine Berechtigung (Moderate Members).", ok=False, ephemeral=True)
            return
        if minutes < 1 or minutes > 40320:
            await self._respond(interaction, "Minuten muessen zwischen 1 und 40320 liegen.", ok=False, ephemeral=True)
            return

        try:
            await member.timeout(timedelta(minutes=minutes), reason=reason)
            await self._respond(interaction, f"{member.mention} hat jetzt Timeout ({minutes}m).", ok=True, ephemeral=True)
        except Exception as e:
            await self._respond(interaction, f"Timeout fehlgeschlagen: {e}", ok=False, ephemeral=True)

    @app_commands.command(name="untimeout", description="Entfernt ein Timeout von einem Mitglied")
    @app_commands.describe(member="Mitglied", reason="Grund")
    async def untimeout_member(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Kein Grund"):
        if not self._tool_enabled("server_tools_untimeout_enabled"):
            await self._respond(interaction, "/untimeout ist deaktiviert.", ok=False, ephemeral=True)
            return
        if not interaction.user.guild_permissions.moderate_members:
            await self._respond(interaction, "Keine Berechtigung (Moderate Members).", ok=False, ephemeral=True)
            return

        try:
            await member.timeout(None, reason=reason)
            await self._respond(interaction, f"Timeout von {member.mention} entfernt.", ok=True, ephemeral=True)
        except Exception as e:
            await self._respond(interaction, f"Untimeout fehlgeschlagen: {e}", ok=False, ephemeral=True)


async def setup(bot):
    await bot.add_cog(ServerTools(bot))
