# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import logging
from embeds import success_embed, error_embed
from config import SETTINGS_FILE

logger = logging.getLogger('GTA-RP-Bot')

# ─── HILFSFUNKTIONEN ──────────────────────────────────────────────
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def has_permission(interaction, settings, cmd_name):
    """Prueft ob Nutzer berechtigt ist (admin oder in allowed_roles)"""
    if interaction.user.guild_permissions.administrator:
        return True
    allowed = settings.get(f"{cmd_name}_allowed_roles", [])
    if not allowed:
        return False
    return any(str(r.id) in [str(x) for x in allowed] for r in interaction.user.roles)

async def log_action(bot, settings, embed):
    """Sendet Log-Nachricht in konfigurierten Log-Kanal"""
    try:
        log_channel_id = settings.get("log_channel")
        if log_channel_id:
            channel = bot.get_channel(int(log_channel_id))
            if channel:
                await channel.send(embed=embed)
    except Exception as e:
        logger.error(f"Log-Action Fehler: {e}")

class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ─── CLEAR COMMAND ────────────────────────────────────────────────────
    @app_commands.command(name="clear", description="Loescht eine bestimmte Anzahl an Nachrichten")
    @app_commands.describe(anzahl="Anzahl der Nachrichten (1-100)")
    async def clear(self, interaction: discord.Interaction, anzahl: int):
        settings = load_settings()
        
        if not interaction.user.guild_permissions.manage_messages:
            embed = error_embed("🚫 Keine Berechtigung", "Du hast keine Berechtigung zum Loeschen von Nachrichten.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if anzahl < 1 or anzahl > 100:
            embed = error_embed("❌ Ungueltige Anzahl", "Bitte gib eine Zahl zwischen 1 und 100 an.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=anzahl)
        
        embed = success_embed(
            "✅ Nachrichten geloescht",
            f"{len(deleted)} Nachrichten wurden erfolgreich geloescht."
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        log_embed = discord.Embed(
            title="🗑️ Nachrichten geloescht",
            description=f"{interaction.user.mention} hat **{len(deleted)}** Nachrichten in {interaction.channel.mention} geloescht.",
            color=0xf59e0b
        )
        await log_action(self.bot, settings, log_embed)

    # ─── KICK COMMAND ─────────────────────────────────────────────────────
    @app_commands.command(name="kick", description="Kickt einen Benutzer vom Server")
    @app_commands.describe(member="Der Benutzer der gekickt werden soll", grund="Grund fuer den Kick")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, grund: str = "Kein Grund angegeben"):
        settings = load_settings()
        
        if not interaction.user.guild_permissions.kick_members:
            embed = error_embed("🚫 Keine Berechtigung", "Du hast keine Berechtigung Mitglieder zu kicken.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if member.top_role >= interaction.user.top_role:
            embed = error_embed("❌ Aktion nicht moeglich", "Du kannst keine Mitglieder kicken die eine hoehere oder gleiche Rolle haben.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            await member.kick(reason=grund)
            embed = success_embed(
                "✅ Mitglied gekickt",
                f"{member.mention} wurde vom Server gekickt.\\n\\n**Grund:** {grund}"
            )
            await interaction.response.send_message(embed=embed)
            
            log_embed = discord.Embed(
                title="👢 Kick",
                description=f"{interaction.user.mention} hat {member.mention} gekickt.\\n**Grund:** {grund}",
                color=0xf59e0b
            )
            await log_action(self.bot, settings, log_embed)
        except Exception as e:
            embed = error_embed("❌ Fehler", f"Konnte Mitglied nicht kicken: {str(e)}")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    # ─── BAN COMMAND ─────────────────────────────────────────────────────
    @app_commands.command(name="ban", description="Bannt einen Benutzer vom Server")
    @app_commands.describe(member="Der Benutzer der gebannt werden soll", grund="Grund fuer den Ban")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, grund: str = "Kein Grund angegeben"):
        settings = load_settings()
        
        if not interaction.user.guild_permissions.ban_members:
            embed = error_embed("🚫 Keine Berechtigung", "Du hast keine Berechtigung Mitglieder zu bannen.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if member.top_role >= interaction.user.top_role:
            embed = error_embed("❌ Aktion nicht moeglich", "Du kannst keine Mitglieder bannen die eine hoehere oder gleiche Rolle haben.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            await member.ban(reason=grund)
            embed = success_embed(
                "✅ Mitglied gebannt",
                f"{member.mention} wurde vom Server gebannt.\\n\\n**Grund:** {grund}"
            )
            await interaction.response.send_message(embed=embed)
            
            log_embed = discord.Embed(
                title="🔨 Ban",
                description=f"{interaction.user.mention} hat {member.mention} gebannt.\\n**Grund:** {grund}",
                color=0xef4444
            )
            await log_action(self.bot, settings, log_embed)
        except Exception as e:
            embed = error_embed("❌ Fehler", f"Konnte Mitglied nicht bannen: {str(e)}")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    # ─── BEFOERDERN ────────────────────────────────────────────────────────
    @app_commands.command(name="befoerdern", description="Befoerdere ein Mitglied")
    @app_commands.describe(member="Das Mitglied das befoerdert werden soll", rolle="Die neue hoehere Rolle")
    async def befoerdern(self, interaction: discord.Interaction, member: discord.Member, rolle: discord.Role):
        settings = load_settings()
        
        if not settings.get("befoerdern_enabled", True):
            embed = error_embed("❌ Deaktiviert", "Dieser Befehl ist aktuell deaktiviert.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not has_permission(interaction, settings, "befoerdern"):
            embed = error_embed("🚫 Keine Berechtigung", "Du hast keine Berechtigung um Mitglieder zu befoerdern.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            await member.add_roles(rolle)
            embed = success_embed(
                "⬆️ Befoerderung",
                f"{member.mention} wurde zur Rolle {rolle.mention} befoerdert! Glueckwunsch!"
            )
            await interaction.response.send_message(embed=embed)
            
            log_embed = discord.Embed(
                title="⬆️ Befoerderung",
                description=f"{interaction.user.mention} hat {member.mention} zu {rolle.mention} befoerdert.",
                color=0x22c55e
            )
            await log_action(self.bot, settings, log_embed)
        except Exception as e:
            embed = error_embed("❌ Fehler", f"Fehler beim Befoerdern: {str(e)}")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    # ─── RANKUP ──────────────────────────────────────────────────────────
    @app_commands.command(name="rankup", description="Gebe einem Mitglied einen Rang-Aufstieg")
    @app_commands.describe(member="Das Mitglied das einen Rankup erhaelt")
    async def rankup(self, interaction: discord.Interaction, member: discord.Member):
        settings = load_settings()
        
        if not settings.get("rankup_enabled", True):
            embed = error_embed("❌ Deaktiviert", "Dieser Befehl ist aktuell deaktiviert.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not has_permission(interaction, settings, "rankup"):
            embed = error_embed("🚫 Keine Berechtigung", "Du hast keine Berechtigung fuer Rankups.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = success_embed(
            "📈 Rank Up",
            f"{member.mention} hat einen Rangaufstieg erhalten! Weiter so!"
        )
        await interaction.response.send_message(embed=embed)
        
        log_embed = discord.Embed(
            title="📈 Rank Up",
            description=f"{interaction.user.mention} hat {member.mention} ein Rank-Up gegeben.",
            color=0x22c55e
        )
        await log_action(self.bot, settings, log_embed)

    # ─── DEGRADIEREN ────────────────────────────────────────────────────────
    @app_commands.command(name="drank", description="Degradiere ein Mitglied")
    @app_commands.describe(member="Das Mitglied das degradiert werden soll", rolle="Die Rolle die entfernt werden soll")
    async def drank(self, interaction: discord.Interaction, member: discord.Member, rolle: discord.Role):
        settings = load_settings()
        
        if not settings.get("drank_enabled", True):
            embed = error_embed("❌ Deaktiviert", "Dieser Befehl ist aktuell deaktiviert.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not has_permission(interaction, settings, "drank"):
            embed = error_embed("🚫 Keine Berechtigung", "Du hast keine Berechtigung um Mitglieder zu degradieren.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            await member.remove_roles(rolle)
            embed = success_embed(
                "⬇️ Degradierung",
                f"{member.mention} wurde von der Rolle {rolle.mention} degradiert."
            )
            await interaction.response.send_message(embed=embed)
            
            log_embed = discord.Embed(
                title="⬇️ Degradierung",
                description=f"{interaction.user.mention} hat {member.mention} von {rolle.mention} degradiert.",
                color=0xf59e0b
            )
            await log_action(self.bot, settings, log_embed)
        except Exception as e:
            embed = error_embed("❌ Fehler", f"Fehler beim Degradieren: {str(e)}")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    # ─── EINSTELLEN ────────────────────────────────────────────────────────
    @app_commands.command(name="einstellen", description="Stelle ein neues Mitglied offiziell ein")
    @app_commands.describe(member="Das neue Mitglied das eingestellt werden soll", rolle="Die Rolle des neuen Mitglieds")
    async def einstellen(self, interaction: discord.Interaction, member: discord.Member, rolle: discord.Role):
        settings = load_settings()
        
        if not settings.get("einstellen_enabled", True):
            embed = error_embed("❌ Deaktiviert", "Dieser Befehl ist aktuell deaktiviert.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not has_permission(interaction, settings, "einstellen"):
            embed = error_embed("🚫 Keine Berechtigung", "Du hast keine Berechtigung um Mitglieder einzustellen.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            await member.add_roles(rolle)
            embed = success_embed(
                "✅ Mitglied eingestellt",
                f"{member.mention} wurde als {rolle.mention} eingestellt! Willkommen im Team!"
            )
            await interaction.response.send_message(embed=embed)
            
            log_embed = discord.Embed(
                title="➕ Einstellung",
                description=f"{interaction.user.mention} hat {member.mention} als {rolle.mention} eingestellt.",
                color=0x22c55e
            )
            await log_action(self.bot, settings, log_embed)
        except Exception as e:
            embed = error_embed("❌ Fehler", f"Fehler beim Einstellen: {str(e)}")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    # ─── KUENDIGEN ─────────────────────────────────────────────────────────
    @app_commands.command(name="kuendigen", description="Kuendige einem Mitglied / entferne aus dem Team")
    @app_commands.describe(member="Das Mitglied das gekuendigt werden soll", rolle="Die Rolle die entfernt werden soll")
    async def kuendigen(self, interaction: discord.Interaction, member: discord.Member, rolle: discord.Role):
        settings = load_settings()
        
        if not settings.get("kuendigen_enabled", True):
            embed = error_embed("❌ Deaktiviert", "Dieser Befehl ist aktuell deaktiviert.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not has_permission(interaction, settings, "kuendigen"):
            embed = error_embed("🚫 Keine Berechtigung", "Du hast keine Berechtigung um Mitglieder zu kuendigen.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            await member.remove_roles(rolle)
            embed = success_embed(
                "❌ Kuendigung",
                f"{member.mention} wurde die Rolle {rolle.mention} entfernt (Kuendigung)."
            )
            await interaction.response.send_message(embed=embed)
            
            log_embed = discord.Embed(
                title="❌ Kuendigung",
                description=f"{interaction.user.mention} hat {member.mention} die Rolle {rolle.mention} entzogen (Kuendigung).",
                color=0xef4444
            )
            await log_action(self.bot, settings, log_embed)
        except Exception as e:
            embed = error_embed("❌ Fehler", f"Fehler beim Kuendigen: {str(e)}")
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Management(bot))
