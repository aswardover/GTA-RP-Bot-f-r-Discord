# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord import app_commands
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


def has_permission(member: discord.Member, allowed_role_ids: list) -> bool:
    """Prueft ob ein Mitglied eine der erlaubten Rollen hat."""
    if not allowed_role_ids:
        # Wenn keine Rollen konfiguriert: nur Admins
        return member.guild_permissions.administrator
    user_roles = {r.id for r in member.roles}
    return bool(user_roles.intersection(set(allowed_role_ids)))


class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── EINSTELLEN ──────────────────────────────────────────────────────────
    @app_commands.command(name="einstellen", description="Stellt ein Mitglied in der Fraktion ein")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(mitglied="Das Mitglied das eingestellt wird", position="Position/Rang")
    async def einstellen(self, interaction: discord.Interaction, mitglied: discord.Member, position: str):
        settings = load_settings()
        if not settings.get("einstellen_enabled", True):
            await interaction.response.send_message(
                embed=error_embed("Deaktiviert", "Der Einstellen-Befehl ist derzeit deaktiviert."),
                ephemeral=True
            )
            return
        allowed = settings.get("einstellen_allowed_roles", [])
        if not has_permission(interaction.user, allowed):
            await interaction.response.send_message(
                embed=error_embed("Keine Berechtigung", "Du hast keine Erlaubnis diesen Befehl zu nutzen."),
                ephemeral=True
            )
            return
        log_channel_id = settings.get("management_log_channel")
        embed = create_embed(
            title="✅ Mitglied eingestellt",
            description=(
                f"**Mitglied:** {mitglied.mention}\n"
                f"**Position:** {position}\n"
                f"**Eingestellt von:** {interaction.user.mention}"
            ),
            color=0x10b981
        )
        await interaction.response.send_message(embed=embed)
        if log_channel_id:
            ch = interaction.guild.get_channel(int(log_channel_id))
            if ch:
                await ch.send(embed=embed)

    # ── KUENDIGEN ────────────────────────────────────────────────────────────
    @app_commands.command(name="kuendigen", description="Kuendigt einem Mitglied in der Fraktion")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(mitglied="Das Mitglied das gekuendigt wird", grund="Grund der Kuendigung")
    async def kuendigen(self, interaction: discord.Interaction, mitglied: discord.Member, grund: str = "Kein Grund angegeben"):
        settings = load_settings()
        if not settings.get("kuendigen_enabled", True):
            await interaction.response.send_message(
                embed=error_embed("Deaktiviert", "Der Kuendigen-Befehl ist derzeit deaktiviert."),
                ephemeral=True
            )
            return
        allowed = settings.get("kuendigen_allowed_roles", [])
        if not has_permission(interaction.user, allowed):
            await interaction.response.send_message(
                embed=error_embed("Keine Berechtigung", "Du hast keine Erlaubnis diesen Befehl zu nutzen."),
                ephemeral=True
            )
            return
        log_channel_id = settings.get("management_log_channel")
        embed = create_embed(
            title="🔴 Mitglied gekuendigt",
            description=(
                f"**Mitglied:** {mitglied.mention}\n"
                f"**Grund:** {grund}\n"
                f"**Gekuendigt von:** {interaction.user.mention}"
            ),
            color=0xef4444
        )
        await interaction.response.send_message(embed=embed)
        if log_channel_id:
            ch = interaction.guild.get_channel(int(log_channel_id))
            if ch:
                await ch.send(embed=embed)

    # ── BEFOERDERN ───────────────────────────────────────────────────────────
    @app_commands.command(name="befoerdern", description="Befoerdert ein Mitglied auf einen hoeheren Rang")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(mitglied="Das Mitglied das befoerdert wird", neuer_rang="Der neue Rang")
    async def befoerdern(self, interaction: discord.Interaction, mitglied: discord.Member, neuer_rang: str):
        settings = load_settings()
        if not settings.get("befoerdern_enabled", True):
            await interaction.response.send_message(
                embed=error_embed("Deaktiviert", "Der Befoerdern-Befehl ist derzeit deaktiviert."),
                ephemeral=True
            )
            return
        allowed = settings.get("befoerdern_allowed_roles", [])
        if not has_permission(interaction.user, allowed):
            await interaction.response.send_message(
                embed=error_embed("Keine Berechtigung", "Du hast keine Erlaubnis diesen Befehl zu nutzen."),
                ephemeral=True
            )
            return
        log_channel_id = settings.get("management_log_channel")
        embed = create_embed(
            title="⬆️ Mitglied befoerdert",
            description=(
                f"**Mitglied:** {mitglied.mention}\n"
                f"**Neuer Rang:** {neuer_rang}\n"
                f"**Befoerdert von:** {interaction.user.mention}"
            ),
            color=0xf59e0b
        )
        await interaction.response.send_message(embed=embed)
        if log_channel_id:
            ch = interaction.guild.get_channel(int(log_channel_id))
            if ch:
                await ch.send(embed=embed)

    # ── RANKEN (RANKUP) ──────────────────────────────────────────────────────
    @app_commands.command(name="ranken", description="Setzt den Rang eines Mitglieds")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(mitglied="Das Mitglied", rang="Neuer Rang")
    async def ranken(self, interaction: discord.Interaction, mitglied: discord.Member, rang: str):
        settings = load_settings()
        if not settings.get("ranken_enabled", True):
            await interaction.response.send_message(
                embed=error_embed("Deaktiviert", "Der Ranken-Befehl ist derzeit deaktiviert."),
                ephemeral=True
            )
            return
        allowed = settings.get("ranken_allowed_roles", [])
        if not has_permission(interaction.user, allowed):
            await interaction.response.send_message(
                embed=error_embed("Keine Berechtigung", "Du hast keine Erlaubnis diesen Befehl zu nutzen."),
                ephemeral=True
            )
            return
        log_channel_id = settings.get("management_log_channel")
        embed = create_embed(
            title="🏅 Rang gesetzt",
            description=(
                f"**Mitglied:** {mitglied.mention}\n"
                f"**Rang:** {rang}\n"
                f"**Gesetzt von:** {interaction.user.mention}"
            ),
            color=0x818cf8
        )
        await interaction.response.send_message(embed=embed)
        if log_channel_id:
            ch = interaction.guild.get_channel(int(log_channel_id))
            if ch:
                await ch.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Management(bot))
