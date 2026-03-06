# -*- coding: utf-8 -*-
import json
import os
import threading
from typing import Dict, Any, List
import discord
from discord import app_commands
from discord.ext import commands
import config
from embeds import create_embed

GUILD_ID = config.GUILD_ID
SETTINGS_FILE = "settings.json"
settings_lock = threading.Lock()

def load_settings() -> Dict[str, Any]:
    if not os.path.exists(SETTINGS_FILE):
        return {}
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

class CustomCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.text_commands: Dict[str, Dict[str, Any]] = {}
        self.register_custom_commands()

    def register_custom_commands(self):
        settings = load_settings()
        custom_commands: List[Dict[str, Any]] = settings.get("custom_commands", [])
        to_remove = []
        for cmd in self.bot.tree.get_commands():
            if isinstance(cmd, app_commands.Command) and getattr(cmd.callback, "__custom_cmd__", False):
                to_remove.append(cmd)
        guild_obj = discord.Object(id=GUILD_ID)
        for cmd in to_remove:
            try:
                self.bot.tree.remove_command(cmd.name, guild=guild_obj)
            except Exception:
                pass
        self.text_commands.clear()
        for cmd_def in custom_commands:
            name = cmd_def.get("name")
            prefix = cmd_def.get("prefix", "!").strip()
            response = cmd_def.get("response", "")
            allowed_roles = cmd_def.get("allowed_roles", [])
            if not name:
                continue
            if prefix == "/":
                async def slash_callback(
                    interaction: discord.Interaction,
                    _response=response,
                    _allowed_roles=allowed_roles
                ):
                    if _allowed_roles:
                        if not interaction.user.guild_permissions.administrator:
                            user_role_ids = [r.id for r in interaction.user.roles]
                            if not any(rid in user_role_ids for rid in _allowed_roles):
                                await interaction.response.send_message("\u274c Du hast keine Berechtigung.", ephemeral=True)
                                return
                    text = format_placeholders(_response, user=interaction.user, guild=interaction.guild, channel=interaction.channel)
                    embed = create_embed(description=text, color=config.COLOR_INFO)
                    await interaction.response.send_message(embed=embed, ephemeral=False)
                slash_callback.__custom_cmd__ = True
                command = app_commands.Command(name=name, description=f"Custom Command: {name}", callback=slash_callback)
                command.guild_ids = [GUILD_ID]
                self.bot.tree.add_command(command)
            else:
                key = f"{prefix}{name}"
                self.text_commands[key] = {"response": response, "allowed_roles": allowed_roles}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        content = message.content.strip()
        if not content:
            return
        cmd_def = self.text_commands.get(content)
        if not cmd_def:
            return
        allowed_roles = cmd_def.get("allowed_roles", [])
        response = cmd_def.get("response", "")
        if allowed_roles:
            if not message.author.guild_permissions.administrator:
                user_role_ids = [r.id for r in message.author.roles]
                if not any(rid in user_role_ids for rid in allowed_roles):
                    await message.channel.send(f"{message.author.mention} \u274c Keine Berechtigung.")
                    return
        text = format_placeholders(response, user=message.author, guild=message.guild, channel=message.channel)
        embed = create_embed(description=text, color=config.COLOR_INFO)
        await message.channel.send(embed=embed)

    @staticmethod
    def _has_allowed_role(member: discord.Member, allowed_role_ids: List[int]) -> bool:
        if not allowed_role_ids:
            return True
        user_roles = {r.id for r in member.roles}
        return bool(user_roles.intersection(set(allowed_role_ids)))

    @app_commands.command(name="befoerdern", description="Befoerdert einen User (gibt Rolle)")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.checks.has_permissions(manage_roles=True)
    async def befoerdern(self, interaction: discord.Interaction, member: discord.Member, neue_rolle: discord.Role):
        settings = load_settings()
        if not settings.get("befoerdern_enabled", True):
            await interaction.response.send_message("\u274c Der /befoerdern Befehl ist deaktiviert.", ephemeral=True)
            return
        if not self._has_allowed_role(interaction.user, settings.get("befoerdern_allowed_roles", [])):
            await interaction.response.send_message("\u274c Keine Berechtigung fuer /befoerdern.", ephemeral=True)
            return
        await member.add_roles(neue_rolle)
        await interaction.response.send_message(f"{member.mention} wurde zu {neue_rolle.mention} befoerdert. \U0001f389", ephemeral=True)

    @app_commands.command(name="rankup", description="Rangaufstieg: Alte Rolle entfernen, neue Rolle geben")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rankup(self, interaction: discord.Interaction, member: discord.Member, alte_rolle: discord.Role, neue_rolle: discord.Role):
        settings = load_settings()
        if not settings.get("rankup_enabled", True):
            await interaction.response.send_message("\u274c Der /rankup Befehl ist deaktiviert.", ephemeral=True)
            return
        if not self._has_allowed_role(interaction.user, settings.get("rankup_allowed_roles", [])):
            await interaction.response.send_message("\u274c Keine Berechtigung fuer /rankup.", ephemeral=True)
            return
        await member.remove_roles(alte_rolle)
        await member.add_roles(neue_rolle)
        await interaction.response.send_message(f"{member.mention} wurde von {alte_rolle.mention} zu {neue_rolle.mention} befoerdert. \U0001f389", ephemeral=True)

    @app_commands.command(name="drank", description="Degradiert einen User (Rolle entfernen)")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.checks.has_permissions(manage_roles=True)
    async def drank(self, interaction: discord.Interaction, member: discord.Member, rolle: discord.Role):
        settings = load_settings()
        if not settings.get("drank_enabled", True):
            await interaction.response.send_message("\u274c Der /drank Befehl ist deaktiviert.", ephemeral=True)
            return
        if not self._has_allowed_role(interaction.user, settings.get("drank_allowed_roles", [])):
            await interaction.response.send_message("\u274c Keine Berechtigung fuer /drank.", ephemeral=True)
            return
        await member.remove_roles(rolle)
        await interaction.response.send_message(f"{rolle.mention} wurde von {member.mention} entfernt.", ephemeral=True)

    @app_commands.command(name="einstellen", description="Stellt einen User ein")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.checks.has_permissions(manage_roles=True)
    async def einstellen(self, interaction: discord.Interaction, member: discord.Member, job_rolle: discord.Role):
        settings = load_settings()
        if not settings.get("einstellen_enabled", True):
            await interaction.response.send_message("\u274c Der /einstellen Befehl ist deaktiviert.", ephemeral=True)
            return
        if not self._has_allowed_role(interaction.user, settings.get("einstellen_allowed_roles", [])):
            await interaction.response.send_message("\u274c Keine Berechtigung fuer /einstellen.", ephemeral=True)
            return
        await member.add_roles(job_rolle)
        await interaction.response.send_message(f"{member.mention} eingestellt als {job_rolle.mention}.", ephemeral=True)

    @app_commands.command(name="kuendigen", description="Kuendigt einen User")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.checks.has_permissions(manage_roles=True)
    async def kuendigen(self, interaction: discord.Interaction, member: discord.Member, job_rolle: discord.Role):
        settings = load_settings()
        if not settings.get("kuendigen_enabled", True):
            await interaction.response.send_message("\u274c Der /kuendigen Befehl ist deaktiviert.", ephemeral=True)
            return
        if not self._has_allowed_role(interaction.user, settings.get("kuendigen_allowed_roles", [])):
            await interaction.response.send_message("\u274c Keine Berechtigung fuer /kuendigen.", ephemeral=True)
            return
        await member.remove_roles(job_rolle)
        await interaction.response.send_message(f"{member.mention} wurde von {job_rolle.mention} gekuendigt.", ephemeral=True)

def format_placeholders(text: str, user, guild, channel) -> str:
    replacements = {
        "{user}": user.mention if hasattr(user, "mention") else str(user),
        "{server}": guild.name if guild else "",
        "{channel}": channel.mention if hasattr(channel, "mention") else "",
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text

async def setup(bot: commands.Bot):
    await bot.add_cog(CustomCommands(bot))
