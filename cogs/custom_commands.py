# -*- coding: utf-8 -*-
import json
import os
from typing import Dict, Any, List
import discord
from discord.ext import commands
import config
from embeds import create_embed

SETTINGS_FILE = "settings.json"

def load_settings() -> Dict[str, Any]:
    if not os.path.exists(SETTINGS_FILE):
        return {}
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

class CustomCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.text_commands: Dict[str, Dict[str, Any]] = {}

    def _build_text_commands(self, settings: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        built: Dict[str, Dict[str, Any]] = {}
        if not settings.get("commands_enabled", True):
            return built

        default_prefix = str(settings.get("custom_commands_prefix", settings.get("prefix", "!")) or "!").strip() or "!"
        custom_commands: List[Dict[str, Any]] = settings.get("custom_commands", [])
        if not isinstance(custom_commands, list):
            return built

        for cmd_def in custom_commands:
            name = str(cmd_def.get("name", "")).strip()
            if not name:
                continue
            response = str(cmd_def.get("response", ""))
            allowed_roles = [str(r) for r in (cmd_def.get("allowed_roles", []) if isinstance(cmd_def.get("allowed_roles"), list) else []) if str(r).strip()]
            send_as_embed = bool(cmd_def.get("send_as_embed", True))
            target_channel_id = str(cmd_def.get("target_channel_id", "") or "").strip()
            cmd_prefix = str(cmd_def.get("prefix", default_prefix) or default_prefix).strip() or default_prefix
            key = f"{cmd_prefix}{name}".lower()
            built[key] = {
                "response": response,
                "allowed_roles": allowed_roles,
                "send_as_embed": send_as_embed,
                "target_channel_id": target_channel_id,
            }
        return built

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        content = message.content.strip()
        if not content:
            return
        settings = load_settings()
        self.text_commands = self._build_text_commands(settings)
        cmd_def = self.text_commands.get(content.lower())
        if not cmd_def:
            return
        feature_roles = [str(r) for r in (settings.get("custom_commands_manager_roles", []) if isinstance(settings.get("custom_commands_manager_roles"), list) else []) if str(r).strip()]
        if feature_roles and not message.author.guild_permissions.administrator:
            user_role_ids = [str(r.id) for r in message.author.roles]
            if not any(rid in user_role_ids for rid in feature_roles):
                return

        allowed_roles = [str(r) for r in (cmd_def.get("allowed_roles", []) if isinstance(cmd_def.get("allowed_roles"), list) else []) if str(r).strip()]
        response = cmd_def.get("response", "")
        send_as_embed = bool(cmd_def.get("send_as_embed", True))
        target_channel_id = str(cmd_def.get("target_channel_id", "") or "").strip()
        if allowed_roles:
            if not message.author.guild_permissions.administrator:
                user_role_ids = [str(r.id) for r in message.author.roles]
                if not any(rid in user_role_ids for rid in allowed_roles):
                    await message.channel.send(f"{message.author.mention} \u274c Keine Berechtigung.")
                    return
        target_channel = message.channel
        if target_channel_id:
            try:
                parsed_channel_id = int(target_channel_id)
                resolved_channel = message.guild.get_channel(parsed_channel_id)
                if resolved_channel is not None:
                    target_channel = resolved_channel
            except (ValueError, TypeError):
                pass

        text = format_placeholders(response, user=message.author, guild=message.guild, channel=target_channel)
        if send_as_embed:
            embed = create_embed(description=text, color=config.COLOR_INFO)
            await target_channel.send(embed=embed)
        else:
            await target_channel.send(text)

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
