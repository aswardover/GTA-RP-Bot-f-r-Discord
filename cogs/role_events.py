# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import datetime
import json

class RoleEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            settings = self.bot.get_settings()
            log_channel_id = settings.get("log_channel")
            
            if log_channel_id:
                log_channel = self.bot.get_channel(int(log_channel_id))
                if log_channel:
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

            # Benutzerdefinierte Wenn-Funktionen
            rules = settings.get("custom_rules", [])
            for rule in rules:
                if rule.get("event") == "role_remove":
                    removed_role_ids = [str(role.id) for role in removed_roles]
                    if rule.get("role") in removed_role_ids:
                        await self.execute_action(rule, after, before.roles, after.roles)
                elif rule.get("event") == "role_add":
                    added_role_ids = [str(role.id) for role in added_roles]
                    if rule.get("role") in added_role_ids:
                        await self.execute_action(rule, after, before.roles, after.roles)

    async def execute_action(self, rule, member, before_roles, after_roles):
        action = rule.get("action")
        if action == "send_message":
            channel_id = rule.get("channel")
            message = rule.get("message", "").format(user=member.mention, server=member.guild.name)
            if channel_id:
                channel = self.bot.get_channel(int(channel_id))
                if channel:
                    await channel.send(message)
        # Weitere Aktionen können hier hinzugefügt werden, z.B. add_role, remove_role, etc.

async def setup(bot):
    await bot.add_cog(RoleEvents(bot))
