# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import json
import os

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

class RoleEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        settings = load_settings()
        if not settings.get("role_events_enabled", False):
            return

        # Check for role changes
        added_roles = [role for role in after.roles if role not in before.roles]
        removed_roles = [role for role in before.roles if role not in after.roles]

        event_configs = settings.get("role_event_configs", [])

        # Handle added roles
        for role in added_roles:
            for config in event_configs:
                if config.get("trigger_role_id") == role.id and config.get("type") == "add":
                    await self.execute_action(after, config)

        # Handle removed roles
        for role in removed_roles:
            for config in event_configs:
                if config.get("trigger_role_id") == role.id and config.get("type") == "remove":
                    await self.execute_action(after, config)

    async def execute_action(self, member, config):
        guild = member.guild
        
        # 1. Send Message
        if config.get("message_text") and config.get("channel_id"):
            channel = guild.get_channel(int(config.get("channel_id")))
            if channel:
                text = config.get("message_text").replace("{user}", member.mention).replace("{server}", guild.name)
                await channel.send(text)

        # 2. Give Role
        if config.get("give_role_id"):
            role_to_give = guild.get_role(int(config.get("give_role_id")))
            if role_to_give:
                await member.add_roles(role_to_give)

        # 3. Take Role
        if config.get("take_role_id"):
            role_to_take = guild.get_role(int(config.get("take_role_id")))
            if role_to_take:
                await member.remove_roles(role_to_take)

async def setup(bot):
    await bot.add_cog(RoleEvents(bot))
