# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timezone
from config import SETTINGS_FILE
from embeds import success_embed, error_embed

DATA_FILE = "stempeluhr_data.json"

# ─── HILFSFUNKTIONEN ──────────────────────────────────────────────
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def has_stempel_role(member, settings, role_key="stempeluhr_allowed_roles"):
    """Prueft ob ein Mitglied die benoetigte Rolle hat."""
    allowed = settings.get(role_key, [])
    if not allowed:
        return True
    return any(str(r.id) in [str(x) for x in allowed] for r in member.roles)

def format_time(dt):
    """Formatiert ein Datetime-Objekt zu lesbarem String."""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    return dt.strftime('%d.%m.%Y %H:%M:%S')

def calc_duration(start, end):
    """Berechnet Dauer zwischen zwei Zeitpunkten."""
    if isinstance(start, str):
        start = datetime.fromisoformat(start)
    if isinstance(end, str):
        end = datetime.fromisoformat(end)
    duration = end - start
    hours, rem = divmod(int(duration.total_seconds()), 3600)
    minutes = rem // 60
    return hours, minutes

# ─── BUTTON VIEW ────────────────────────────────────────────────
class StempelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="⏱ Einstempeln", style=discord.ButtonStyle.green, custom_id="stempel_ein_btn")
    async def btn_ein(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = load_settings()
        if not has_stempel_role(interaction.user, settings, "stempeluhr_allowed_roles"):
            embed = error_embed("🚫 Keine Berechtigung", "Du hast keine Berechtigung zum Stempeln.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        data = load_data()
        uid = str(interaction.user.id)
        
        if uid in data and data[uid].get("eingestempelt"):
            embed = error_embed("⚠️ Bereits eingestempelt", "Du bist bereits eingestempelt! Bitte erst ausstempeln.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        now = datetime.now(timezone.utc)
        if uid not in data:
            data[uid] = {"name": str(interaction.user), "sessions": [], "eingestempelt": None}
        
        data[uid]["eingestempelt"] = now.isoformat()
        data[uid]["name"] = str(interaction.user)
        save_data(data)
        
        embed = success_embed(
            "✅ Eingestempelt",
            f"Du hast dich um **{format_time(now)} UTC** eingestempelt.\\n\\n👉 Vergiss nicht auszustempeln wenn du fertig bist!"
        )
        embed.set_footer(text="GTA-RP Zeiterfassung")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="⏱ Ausstempeln", style=discord.ButtonStyle.red, custom_id="stempel_aus_btn")
    async def btn_aus(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = load_settings()
        if not has_stempel_role(interaction.user, settings, "stempeluhr_allowed_roles"):
            embed = error_embed("🚫 Keine Berechtigung", "Du hast keine Berechtigung zum Stempeln.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        data = load_data()
        uid = str(interaction.user.id)
        
        if uid not in data or not data[uid].get("eingestempelt"):
            embed = error_embed("⚠️ Nicht eingestempelt", "Du bist nicht eingestempelt! Bitte erst einstempeln.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        now = datetime.now(timezone.utc)
        start = datetime.fromisoformat(data[uid]["eingestempelt"])
        hours, minutes = calc_duration(start, now)
        
        session = {
            "start": data[uid]["eingestempelt"],
            "end": now.isoformat(),
            "dauer": f"{hours}h {minutes}m"
        }
        data[uid].setdefault("sessions", []).append(session)
        data[uid]["eingestempelt"] = None
        save_data(data)
        
        embed = success_embed(
            "✅ Ausgestempelt",
            f"Du hast dich um **{format_time(now)} UTC** ausgestempelt.\\n\\n⏱️ **Arbeitszeit:** {hours}h {minutes}m"
        )
        embed.set_footer(text="GTA-RP Zeiterfassung")
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ─── COG ───────────────────────────────────────────────────────
class Stempeluhr(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(StempelView())
    
    stempel = app_commands.Group(name="stempel", description="Stempeluhr-Befehle")
    
    @stempel.command(name="ein", description="Eine Person einstempeln (Admin)")
    @app_commands.describe(member="Die Person die eingestempelt werden soll")
    async def stempel_ein(self, interaction: discord.Interaction, member: discord.Member):
        settings = load_settings()
        if not has_stempel_role(interaction.user, settings, "stempeluhr_admin_roles"):
            embed = error_embed("🚫 Keine Berechtigung", "Nur Admins duerfen andere einstempeln.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        data = load_data()
        uid = str(member.id)
        
        if uid in data and data[uid].get("eingestempelt"):
            embed = error_embed("⚠️ Bereits eingestempelt", f"{member.mention} ist bereits eingestempelt!")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        now = datetime.now(timezone.utc)
        if uid not in data:
            data[uid] = {"name": str(member), "sessions": [], "eingestempelt": None}
        
        data[uid]["eingestempelt"] = now.isoformat()
        data[uid]["name"] = str(member)
        save_data(data)
        
        embed = success_embed(
            "✅ Person eingestempelt",
            f"{member.mention} wurde um **{format_time(now)} UTC** eingestempelt."
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @stempel.command(name="aus", description="Eine Person ausstempeln (Admin)")
    @app_commands.describe(member="Die Person die ausgestempelt werden soll")
    async def stempel_aus(self, interaction: discord.Interaction, member: discord.Member):
        settings = load_settings()
        if not has_stempel_role(interaction.user, settings, "stempeluhr_admin_roles"):
            embed = error_embed("🚫 Keine Berechtigung", "Nur Admins duerfen andere ausstempeln.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        data = load_data()
        uid = str(member.id)
        
        if uid not in data or not data[uid].get("eingestempelt"):
            embed = error_embed("⚠️ Nicht eingestempelt", f"{member.mention} ist nicht eingestempelt!")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        now = datetime.now(timezone.utc)
        start = datetime.fromisoformat(data[uid]["eingestempelt"])
        hours, minutes = calc_duration(start, now)
        
        session = {
            "start": data[uid]["eingestempelt"],
            "end": now.isoformat(),
            "dauer": f"{hours}h {minutes}m"
        }
        data[uid].setdefault("sessions", []).append(session)
        data[uid]["eingestempelt"] = None
        save_data(data)
        
        embed = success_embed(
            "✅ Person ausgestempelt",
            f"{member.mention} wurde ausgestempelt.\\n\\n⏱️ **Arbeitszeit:** {hours}h {minutes}m"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @stempel.command(name="status", description="Deinen aktuellen Stempelstatus anzeigen")
    async def stempel_status(self, interaction: discord.Interaction):
        data = load_data()
        uid = str(interaction.user.id)
        
        if uid not in data:
            embed = error_embed("❌ Keine Daten", "Es wurden noch keine Stempeldaten fuer dich gefunden. Stempel dich zuerst ein!")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(title="⏱️ Dein Stempel-Status", color=0x3b82f6)
        eingestempelt = data[uid].get("eingestempelt")
        
        if eingestempelt:
            start = datetime.fromisoformat(eingestempelt)
            now = datetime.now(timezone.utc)
            hours, minutes = calc_duration(start, now)
            embed.description = (
                f"✅ **Derzeit eingestempelt**\\n\\n"
                f"🕒 **Seit:** {format_time(start)} UTC\\n"
                f"⏱️ **Dauer:** {hours}h {minutes}m"
            )
            embed.color = 0x22c55e
        else:
            embed.description = "❌ **Derzeit ausgestempelt**\\n\\n👉 Stempel dich ein um die Zeiterfassung zu starten!"
            embed.color = 0xef4444
        
        sessions = data[uid].get("sessions", [])
        if sessions:
            total_secs = sum(
                int((datetime.fromisoformat(s["end"]) - datetime.fromisoformat(s["start"])).total_seconds())
                for s in sessions if "end" in s and "start" in s
            )
            total_h, rem = divmod(total_secs, 3600)
            total_m = rem // 60
            embed.add_field(
                name="📈 Gesamtstatistik",
                value=f"Sitzungen: **{len(sessions)}**\\nGesamtzeit: **{total_h}h {total_m}m**",
                inline=False
            )
        
        embed.set_footer(text="GTA-RP Zeiterfassung")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @stempel.command(name="liste", description="Alle Stempelzeiten anzeigen (Admin)")
    async def stempel_liste(self, interaction: discord.Interaction):
        settings = load_settings()
        if not has_stempel_role(interaction.user, settings, "stempeluhr_admin_roles"):
            embed = error_embed("🚫 Keine Berechtigung", "Nur Admins duerfen die Liste einsehen.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        data = load_data()
        if not data:
            embed = error_embed("❌ Keine Daten", "Es wurden noch keine Stempeldaten erfasst.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📄 Stempelzeiten Uebersicht",
            description="Alle erfassten Arbeitszeiten der Mitglieder.",
            color=0xf59e0b
        )
        
        for uid, udata in list(data.items())[:10]:  # Max 10 um Limit zu vermeiden
            sessions = udata.get("sessions", [])
            name = udata.get("name", uid)
            
            if not sessions:
                continue
            
            total_secs = sum(
                int((datetime.fromisoformat(s["end"]) - datetime.fromisoformat(s["start"])).total_seconds())
                for s in sessions if "end" in s and "start" in s
            )
            total_h, rem = divmod(total_secs, 3600)
            total_m = rem // 60
            
            status = "✅ Eingestempelt" if udata.get("eingestempelt") else "❌ Ausgestempelt"
            
            embed.add_field(
                name=f"{name}",
                value=(
                    f"Status: {status}\\n"
                    f"Sitzungen: **{len(sessions)}**\\n"
                    f"Gesamt: **{total_h}h {total_m}m**"
                ),
                inline=True
            )
        
        if len(data) > 10:
            embed.set_footer(text=f"Zeige 10 von {len(data)} Mitarbeitern | GTA-RP Zeiterfassung")
        else:
            embed.set_footer(text="GTA-RP Zeiterfassung")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="stempelliste", description="Alle Stempelzeiten anzeigen (Admin)")
    async def stempel_liste_alias(self, interaction: discord.Interaction):
        await self.stempel_liste(interaction)

async def setup(bot):
    await bot.add_cog(Stempeluhr(bot))
