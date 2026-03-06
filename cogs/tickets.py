# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime

SETTINGS_FILE = "stempeluhr_settings.json"
STEMPEL_DATA_FILE = "stempel_data.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

def load_stempel_data():
    if os.path.exists(STEMPEL_DATA_FILE):
        with open(STEMPEL_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_stempel_data(data):
    with open(STEMPEL_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

class StempelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Stempeln", style=discord.ButtonStyle.primary, custom_id="stempel_button")
    async def stempel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        stempel_data = load_stempel_data()
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        
        if guild_id not in stempel_data:
            stempel_data[guild_id] = {}
        
        if user_id not in stempel_data[guild_id]:
            stempel_data[guild_id][user_id] = {"status": "out", "times": []}
        
        user_data = stempel_data[guild_id][user_id]
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if user_data["status"] == "out":
            user_data["status"] = "in"
            user_data["times"].append({"ein": current_time, "aus": None})
            save_stempel_data(stempel_data)
            await interaction.response.send_message(
                f"✅ Du hast dich um {current_time} eingestempelt!",
                ephemeral=True
            )
        else:
            user_data["status"] = "out"
            if user_data["times"]:
                user_data["times"][-1]["aus"] = current_time
            save_stempel_data(stempel_data)
            await interaction.response.send_message(
                f"✅ Du hast dich um {current_time} ausgestempelt!",
                ephemeral=True
            )

class Stempeluhr(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="stempel_ein", description="Stempelt einen Benutzer ein")
    async def stempel_ein(self, interaction: discord.Interaction, user: discord.Member):
        settings = load_settings()
        guild_id = str(interaction.guild.id)
        
        # Prüfe Berechtigungen
        if guild_id in settings and "stempel_ein_roles" in settings[guild_id]:
            allowed_roles = settings[guild_id]["stempel_ein_roles"]
            if not any(role.id in allowed_roles for role in interaction.user.roles):
                await interaction.response.send_message("❌ Du hast keine Berechtigung für diesen Befehl!", ephemeral=True)
                return
        
        stempel_data = load_stempel_data()
        user_id = str(user.id)
        
        if guild_id not in stempel_data:
            stempel_data[guild_id] = {}
        
        if user_id not in stempel_data[guild_id]:
            stempel_data[guild_id][user_id] = {"status": "out", "times": []}
        
        user_data = stempel_data[guild_id][user_id]
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if user_data["status"] == "out":
            user_data["status"] = "in"
            user_data["times"].append({"ein": current_time, "aus": None})
            save_stempel_data(stempel_data)
            await interaction.response.send_message(
                f"✅ {user.mention} wurde um {current_time} eingestempelt!",
                ephemeral=False
            )
        else:
            await interaction.response.send_message(
                f"⚠️ {user.mention} ist bereits eingestempelt!",
                ephemeral=True
            )
    
    @app_commands.command(name="stempel_aus", description="Stempelt einen Benutzer aus")
    async def stempel_aus(self, interaction: discord.Interaction, user: discord.Member):
        settings = load_settings()
        guild_id = str(interaction.guild.id)
        
        # Prüfe Berechtigungen
        if guild_id in settings and "stempel_aus_roles" in settings[guild_id]:
            allowed_roles = settings[guild_id]["stempel_aus_roles"]
            if not any(role.id in allowed_roles for role in interaction.user.roles):
                await interaction.response.send_message("❌ Du hast keine Berechtigung für diesen Befehl!", ephemeral=True)
                return
        
        stempel_data = load_stempel_data()
        user_id = str(user.id)
        
        if guild_id not in stempel_data or user_id not in stempel_data[guild_id]:
            await interaction.response.send_message(
                f"⚠️ {user.mention} hat noch keine Stempeldaten!",
                ephemeral=True
            )
            return
        
        user_data = stempel_data[guild_id][user_id]
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if user_data["status"] == "in":
            user_data["status"] = "out"
            if user_data["times"]:
                user_data["times"][-1]["aus"] = current_time
            save_stempel_data(stempel_data)
            await interaction.response.send_message(
                f"✅ {user.mention} wurde um {current_time} ausgestempelt!",
                ephemeral=False
            )
        else:
            await interaction.response.send_message(
                f"⚠️ {user.mention} ist bereits ausgestempelt!",
                ephemeral=True
            )
    
    @app_commands.command(name="stempel_status", description="Zeigt deinen aktuellen Stempelstatus")
    async def stempel_status(self, interaction: discord.Interaction):
        stempel_data = load_stempel_data()
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        
        if guild_id not in stempel_data or user_id not in stempel_data[guild_id]:
            await interaction.response.send_message(
                "📊 Du hast noch keine Stempeldaten!",
                ephemeral=True
            )
            return
        
        user_data = stempel_data[guild_id][user_id]
        status = "Eingestempelt ✅" if user_data["status"] == "in" else "Ausgestempelt ❌"
        
        await interaction.response.send_message(
            f"📊 Dein Status: {status}",
            ephemeral=True
        )
    
    @app_commands.command(name="stempel_zeiten", description="Zeigt alle deine Stempelzeiten an")
    async def stempel_zeiten(self, interaction: discord.Interaction):
        settings = load_settings()
        guild_id = str(interaction.guild.id)
        
        # Prüfe Berechtigungen
        if guild_id in settings and "stempel_zeiten_roles" in settings[guild_id]:
            allowed_roles = settings[guild_id]["stempel_zeiten_roles"]
            if not any(role.id in allowed_roles for role in interaction.user.roles):
                await interaction.response.send_message("❌ Du hast keine Berechtigung für diesen Befehl!", ephemeral=True)
                return
        
        stempel_data = load_stempel_data()
        user_id = str(interaction.user.id)
        
        if guild_id not in stempel_data or user_id not in stempel_data[guild_id]:
            await interaction.response.send_message(
                "📋 Du hast noch keine Stempelzeiten!",
                ephemeral=True
            )
            return
        
        user_data = stempel_data[guild_id][user_id]
        times = user_data.get("times", [])
        
        if not times:
            await interaction.response.send_message(
                "📋 Du hast noch keine Stempelzeiten!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="📋 Deine Stempelzeiten",
            color=discord.Color.blue()
        )
        
        for i, time_entry in enumerate(times[-10:], 1):  # Zeige die letzten 10 Einträge
            ein_time = time_entry.get("ein", "Unbekannt")
            aus_time = time_entry.get("aus", "Noch nicht ausgestempelt")
            embed.add_field(
                name=f"Eintrag {i}",
                value=f"**Ein:** {ein_time}\n**Aus:** {aus_time}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="stempeluhr_setup", description="Postet die Stempeluhr in einem Channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def stempeluhr_setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        embed = discord.Embed(
            title="🕐 Stempeluhr",
            description="Klicke auf den Button unten, um dich ein- oder auszustempeln.",
            color=discord.Color.green()
        )
        embed.add_field(
            name="ℹ️ Anleitung",
            value="• Beim ersten Klick stempelst du dich ein\n• Beim zweiten Klick stempelst du dich aus\n• Du kannst deinen Status mit `/stempel_status` prüfen",
            inline=False
        )
        
        view = StempelView()
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(
            f"✅ Stempeluhr wurde in {channel.mention} gepostet!",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Stempeluhr(bot))
    bot.add_view(StempelView())
