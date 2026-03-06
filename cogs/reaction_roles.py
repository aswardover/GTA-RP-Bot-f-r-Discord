# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import json
import os
from database import add_reaction_role, get_reaction_roles

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
                        await member.remove_roles(role)

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))