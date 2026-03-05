# -*- coding: utf-8 -*-
import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        settings = self.bot.get_settings()
        channel_id = settings.get("welcome_channel")
        
        if not channel_id:
            return

        channel = member.guild.get_channel(int(channel_id))
        if not channel:
            return

        welcome_msg = settings.get("welcome_message", "Willkommen {user} auf {server}!")
        message = welcome_msg.format(user=member.mention, server=member.guild.name)
        
        await channel.send(message)
        
        # Auto-Rolle vergeben
        role_id = settings.get("auto_role")
        if role_id:
            role = member.guild.get_role(int(role_id))
            if role:
                await member.add_roles(role)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
