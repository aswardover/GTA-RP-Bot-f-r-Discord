# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import asyncio
import re
from collections import defaultdict

class Automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_counts = defaultdict(dict)  # user -> channel -> {count,last_time}
        self.cleanup_task = self.bot.loop.create_task(self.cleanup_counts())

    def cog_unload(self):
        self.cleanup_task.cancel()

    async def cleanup_counts(self):
        while not self.bot.is_closed():
            await asyncio.sleep(60)  # Alle 60 Sekunden aufräumen
            self.message_counts.clear()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        settings = self.bot.get_settings()
        if not settings.get("automod_enabled", False):
            return

        guild = message.guild
        if not guild:
            return

        # Wortfilter
        banned_words = settings.get("automod_banned_words", [])
        if banned_words:
            content_lower = message.content.lower()
            for word in banned_words:
                if re.search(r'\b' + re.escape(word.lower()) + r'\b', content_lower):
                    await self.handle_violation(message, "Banned word", f"Verbotenes Wort: {word}")
                    return

        # Discord Invite Filter
        if settings.get("automod_block_invites", False):
            if re.search(r"discord(?:\.gg|app\.com/invite)/[A-Za-z0-9-]+", message.content, flags=re.IGNORECASE):
                await self.handle_violation(message, "Invite Link", "Discord-Einladungslink ist nicht erlaubt")
                return

        # URL / Link Filter
        if settings.get("automod_block_links", False):
            # Simple URL detector for common schemes and domains.
            if re.search(r"(https?://\S+|www\.\S+|\b\S+\.(com|net|org|gg|io|de)\b)", message.content, flags=re.IGNORECASE):
                await self.handle_violation(message, "Link", "Externer Link ist nicht erlaubt")
                return

        # Anti-Spam
        spam_threshold = settings.get("automod_spam_threshold", 5)
        spam_timeframe = settings.get("automod_spam_timeframe", 10)  # Sekunden

        user_id = message.author.id
        channel_id = message.channel.id
        now = asyncio.get_event_loop().time()

        # Zähle Nachrichten pro User pro Channel
        state = self.message_counts[user_id].get(channel_id)
        if state is None:
            self.message_counts[user_id][channel_id] = {"count": 1, "last_time": now}
        else:
            if now - state["last_time"] > spam_timeframe:
                self.message_counts[user_id][channel_id] = {"count": 1, "last_time": now}
            else:
                state["count"] += 1
                state["last_time"] = now

        if self.message_counts[user_id][channel_id]["count"] >= spam_threshold:
            await self.handle_violation(message, "Spam", f"Zu viele Nachrichten in {spam_timeframe}s")
            self.message_counts[user_id][channel_id]["count"] = 0  # Reset

        # Caps-Lock Filter
        if settings.get("automod_caps_enabled", True):
            caps_ratio = sum(1 for c in message.content if c.isupper()) / len(message.content) if message.content else 0
            if caps_ratio > settings.get("automod_caps_threshold", 0.7) and len(message.content) > 10:
                await self.handle_violation(message, "Caps Abuse", "Zu viele Großbuchstaben")

    async def handle_violation(self, message, reason, details):
        settings = self.bot.get_settings()
        action = settings.get("automod_action", "delete")  # delete, warn, mute, ban

        if action == "delete":
            await message.delete()
        elif action == "warn":
            await message.channel.send(f"{message.author.mention}, Warnung: {reason} - {details}", delete_after=10)
        elif action == "mute":
            mute_role_id = settings.get("automod_mute_role")
            try:
                mute_role_id = int(mute_role_id) if mute_role_id is not None else None
            except (TypeError, ValueError):
                mute_role_id = None
            mute_role = message.guild.get_role(mute_role_id) if mute_role_id else None
            if mute_role:
                await message.author.add_roles(mute_role)
                await message.channel.send(f"{message.author.mention} wurde gemutet für: {reason}", delete_after=10)
        elif action == "ban":
            await message.guild.ban(message.author, reason=f"{reason}: {details}")

        # Log
        log_channel_id = settings.get("automod_log_channel")
        if log_channel_id:
            try:
                log_channel = self.bot.get_channel(int(log_channel_id))
            except (TypeError, ValueError):
                log_channel = None
            if log_channel:
                embed = discord.Embed(title="Automod Verstoß", color=discord.Color.red())
                embed.add_field(name="User", value=message.author.mention)
                embed.add_field(name="Channel", value=message.channel.mention)
                embed.add_field(name="Reason", value=f"{reason}: {details}")
                embed.add_field(name="Message", value=message.content[:1000])
                await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Automod(bot))