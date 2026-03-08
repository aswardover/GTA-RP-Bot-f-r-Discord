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
