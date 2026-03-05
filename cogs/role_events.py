# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import datetime

class RoleEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            settings = self.bot.get_settings()
            log_channel_id = settings.get("log_channel")
            
            if not log_channel_id:
                return

            log_channel = self.bot.get_channel(int(log_channel_id))
            if not log_channel:
                return

            added_roles = [role for role in after.roles if role not in before.roles]
            removed_roles = [role for role in before.roles if role not in after.roles]

            embed = discord.Embed(
                title="Rollenänderung",
                description=f"Benutzer: {after.mention} ({after.id})",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now()
            )

            if added_roles:
                embed.add_field(name="Hinzugefügte Rollen", value=", ".join([role.mention for role in added_roles]), inline=False)
            if removed_roles:
                embed.add_field(name="Entfernte Rollen", value=", ".join([role.mention for role in removed_roles]), inline=False)

            await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RoleEvents(bot))
