# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import json
import os
from database import add_reaction_role, get_reaction_roles

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _allowed_for_reaction_role(self, guild: discord.Guild, member: discord.Member, message_id: str):
        settings = self.bot.get_settings()
        if member.guild_permissions.administrator:
            return True

        global_roles = [str(r) for r in (settings.get("reaction_roles_allowed_roles", []) if isinstance(settings.get("reaction_roles_allowed_roles"), list) else []) if str(r).strip()]
        meta_map = settings.get("reaction_role_message_meta", {}) if isinstance(settings.get("reaction_role_message_meta"), dict) else {}
        message_meta = meta_map.get(str(message_id), {}) if isinstance(meta_map.get(str(message_id)), dict) else {}
        message_roles = [str(r) for r in (message_meta.get("allowed_roles", []) if isinstance(message_meta.get("allowed_roles"), list) else []) if str(r).strip()]

        needed = list(dict.fromkeys(global_roles + message_roles))
        if not needed:
            return True

        member_role_ids = [str(role.id) for role in member.roles]
        return any(rid in member_role_ids for rid in needed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        reaction_roles = await get_reaction_roles()
        message_id = str(payload.message_id)
        rr = next((r for r in reaction_roles if r[1] == message_id), None)
        if rr:
            emoji_role_map = json.loads(rr[2])
            emoji = str(payload.emoji)
            if emoji in emoji_role_map:
                role_id = emoji_role_map[emoji]
                guild = self.bot.get_guild(payload.guild_id)
                if guild:
                    member = guild.get_member(payload.user_id)
                    role = guild.get_role(int(role_id))
                    if member and role:
                        if self._allowed_for_reaction_role(guild, member, message_id):
                            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        reaction_roles = await get_reaction_roles()
        message_id = str(payload.message_id)
        rr = next((r for r in reaction_roles if r[1] == message_id), None)
        if rr:
            emoji_role_map = json.loads(rr[2])
            emoji = str(payload.emoji)
            if emoji in emoji_role_map:
                role_id = emoji_role_map[emoji]
                guild = self.bot.get_guild(payload.guild_id)
                if guild:
                    member = guild.get_member(payload.user_id)
                    role = guild.get_role(int(role_id))
                    if member and role:
                        if self._allowed_for_reaction_role(guild, member, message_id):
                            await member.remove_roles(role)

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))