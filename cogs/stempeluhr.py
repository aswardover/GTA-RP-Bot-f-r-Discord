# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timezone
from config import SETTINGS_FILE

DATA_FILE = "stempeluhr_data.json"

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
    allowed_roles = settings.get(role_key, [])
    if not allowed_roles:
        return True
    return any(str(r.id) in [str(x) for x in allowed_roles] for r in member.roles)

class StempelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Einstempeln", style=discord.ButtonStyle.green, custom_id="stempel_ein")
    async def btn_ein(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = load_settings()
        if not has_stempel_role(interaction.user, settings, "stempeluhr_allowed_roles"):
            await interaction.response.send_message("Du hast keine Berechtigung zum Stempeln.", ephemeral=True)
            return
        data = load_data()
        uid = str(interaction.user.id)
        if uid in data and data[uid].get("eingestempelt"):
            await interaction.response.send_message("Du bist bereits eingestempelt!", ephemeral=True)
            return
        now = datetime.now(timezone.utc)
        if uid not in data:
            data[uid] = {"name": str(interaction.user), "sessions": [], "eingestempelt": None}
        data[uid]["eingestempelt"] = now.isoformat()
        data[uid]["name"] = str(interaction.user)
        save_data(data)
        await interaction.response.send_message(
            f"Eingestempelt um {now.strftime('%d.%m.%Y %H:%M:%S')} UTC", ephemeral=True
        )

    @discord.ui.button(label="Ausstempeln", style=discord.ButtonStyle.red, custom_id="stempel_aus")
    async def btn_aus(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = load_settings()
        if not has_stempel_role(interaction.user, settings, "stempeluhr_allowed_roles"):
            await interaction.response.send_message("Du hast keine Berechtigung zum Stempeln.", ephemeral=True)
            return
        data = load_data()
        uid = str(interaction.user.id)
        if uid not in data or not data[uid].get("eingestempelt"):
            await interaction.response.send_message("Du bist nicht eingestempelt!", ephemeral=True)
            return
        now = datetime.now(timezone.utc)
        start = datetime.fromisoformat(data[uid]["eingestempelt"])
        duration = now - start
        hours, rem = divmod(int(duration.total_seconds()), 3600)
        minutes = rem // 60
        session = {"start": data[uid]["eingestempelt"], "end": now.isoformat(), "dauer": f"{hours}h {minutes}m"}
        data[uid].setdefault("sessions", []).append(session)
        data[uid]["eingestempelt"] = None
        save_data(data)
        await interaction.response.send_message(
            f"Ausgestempelt! Arbeitszeit: **{hours}h {minutes}m**", ephemeral=True
        )

class Stempeluhr(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(StempelView())

    stempel = app_commands.Group(name="stempel", description="Stempeluhr-Befehle")

    @stempel.command(name="ein", description="Eine Person einstempeln")
    @app_commands.describe(member="Die Person die eingestempelt werden soll")
    async def stempel_ein(self, interaction: discord.Interaction, member: discord.Member):
        settings = load_settings()
        if not has_stempel_role(interaction.user, settings, "stempeluhr_admin_roles"):
            await interaction.response.send_message("Du hast keine Berechtigung fuer diesen Befehl.", ephemeral=True)
            return
        data = load_data()
        uid = str(member.id)
        if uid in data and data[uid].get("eingestempelt"):
            await interaction.response.send_message(f"{member.mention} ist bereits eingestempelt!", ephemeral=True)
            return
        now = datetime.now(timezone.utc)
        if uid not in data:
            data[uid] = {"name": str(member), "sessions": [], "eingestempelt": None}
        data[uid]["eingestempelt"] = now.isoformat()
        data[uid]["name"] = str(member)
        save_data(data)
        await interaction.response.send_message(
            f"{member.mention} wurde um {now.strftime('%d.%m.%Y %H:%M:%S')} UTC eingestempelt.", ephemeral=True
        )

    @stempel.command(name="aus", description="Eine Person ausstempeln")
    @app_commands.describe(member="Die Person die ausgestempelt werden soll")
    async def stempel_aus(self, interaction: discord.Interaction, member: discord.Member):
        settings = load_settings()
        if not has_stempel_role(interaction.user, settings, "stempeluhr_admin_roles"):
            await interaction.response.send_message("Du hast keine Berechtigung fuer diesen Befehl.", ephemeral=True)
            return
        data = load_data()
        uid = str(member.id)
        if uid not in data or not data[uid].get("eingestempelt"):
            await interaction.response.send_message(f"{member.mention} ist nicht eingestempelt!", ephemeral=True)
            return
        now = datetime.now(timezone.utc)
        start = datetime.fromisoformat(data[uid]["eingestempelt"])
        duration = now - start
        hours, rem = divmod(int(duration.total_seconds()), 3600)
        minutes = rem // 60
        session = {"start": data[uid]["eingestempelt"], "end": now.isoformat(), "dauer": f"{hours}h {minutes}m"}
        data[uid].setdefault("sessions", []).append(session)
        data[uid]["eingestempelt"] = None
        save_data(data)
        await interaction.response.send_message(
            f"{member.mention} wurde ausgestempelt! Arbeitszeit: **{hours}h {minutes}m**", ephemeral=True
        )

    @stempel.command(name="status", description="Deinen aktuellen Stempelstatus anzeigen")
    async def stempel_status(self, interaction: discord.Interaction):
        data = load_data()
        uid = str(interaction.user.id)
        if uid not in data:
            await interaction.response.send_message("Keine Stempeldaten fuer dich gefunden.", ephemeral=True)
            return
        eingestempelt = data[uid].get("eingestempelt")
        if eingestempelt:
            start = datetime.fromisoformat(eingestempelt)
            now = datetime.now(timezone.utc)
            duration = now - start
            hours, rem = divmod(int(duration.total_seconds()), 3600)
            minutes = rem // 60
            status_text = f"Eingestempelt seit {start.strftime('%d.%m.%Y %H:%M')} UTC (aktuell: {hours}h {minutes}m)"
        else:
            status_text = "Derzeit ausgestempelt."
        embed = discord.Embed(title="Dein Stempel-Status", description=status_text, color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @stempel.command(name="liste", description="Alle Stempelzeiten anzeigen")
    async def stempel_liste(self, interaction: discord.Interaction):
        settings = load_settings()
        if not has_stempel_role(interaction.user, settings, "stempeluhr_admin_roles"):
            await interaction.response.send_message("Du hast keine Berechtigung fuer diesen Befehl.", ephemeral=True)
            return
        data = load_data()
        if not data:
            await interaction.response.send_message("Keine Stempeldaten vorhanden.", ephemeral=True)
            return
        embed = discord.Embed(title="Stempelzeiten Uebersicht", color=discord.Color.gold())
        for uid, udata in data.items():
            sessions = udata.get("sessions", [])
            name = udata.get("name", uid)
            if not sessions:
                continue
            last = sessions[-1]
            total_secs = sum(
                int((datetime.fromisoformat(s["end"]) - datetime.fromisoformat(s["start"])).total_seconds())
                for s in sessions if "end" in s and "start" in s
            )
            total_h, rem = divmod(total_secs, 3600)
            total_m = rem // 60
            embed.add_field(
                name=name,
                value=f"Sitzungen: {len(sessions)} | Gesamt: {total_h}h {total_m}m | Letzte: {last.get('dauer', '?')}",
                inline=False
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="stempel_panel", description="Stempeluhr-Panel in einem Kanal posten")
    async def stempel_panel(self, interaction: discord.Interaction):
        settings = load_settings()
        if not has_stempel_role(interaction.user, settings, "stempeluhr_admin_roles"):
            await interaction.response.send_message("Du hast keine Berechtigung fuer diesen Befehl.", ephemeral=True)
            return
        panel_channel_id = settings.get("stempeluhr_panel_channel_id")
        if panel_channel_id:
            channel = interaction.guild.get_channel(int(panel_channel_id))
        else:
            channel = interaction.channel
        embed = discord.Embed(
            title="Stempeluhr",
            description="Klicke auf den Button um ein- oder auszustempeln.",
            color=discord.Color.green()
        )
        view = StempelView()
        if channel:
            await channel.send(embed=embed, view=view)
            await interaction.response.send_message(f"Stempeluhr-Panel wurde in {channel.mention} gepostet!", ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Stempeluhr(bot))
