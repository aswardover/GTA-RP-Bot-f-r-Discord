# -*- coding: utf-8 -*-
import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import random
import json
from datetime import datetime, timedelta
from database import add_giveaway, get_giveaways, remove_giveaway, update_giveaway_participants

class GiveawayView(discord.ui.View):
    def __init__(self, giveaway_id):
        super().__init__(timeout=None)
        self.giveaway_id = giveaway_id

    @discord.ui.button(label="Teilnehmen", style=discord.ButtonStyle.green, custom_id="giveaway_join")
    async def join_giveaway(self, interaction: discord.Interaction, button: discord.ui.Button):
        giveaways = await get_giveaways()
        giveaway = next((g for g in giveaways if g[1] == str(self.giveaway_id)), None)

        if not giveaway:
            await interaction.response.send_message("Giveaway nicht gefunden.", ephemeral=True)
            return

        participants = json.loads(giveaway[6] or "[]")
        if interaction.user.id in participants:
            await interaction.response.send_message("Du nimmst bereits teil!", ephemeral=True)
        else:
            participants.append(interaction.user.id)
            await update_giveaway_participants(str(self.giveaway_id), json.dumps(participants))
            await interaction.response.send_message("Du nimmst jetzt am Giveaway teil!", ephemeral=True)

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_giveaways = {}
        self.check_giveaways.start()

    def cog_unload(self):
        self.check_giveaways.cancel()

    @app_commands.command(name="giveaway", description="Starte ein Giveaway")
    @app_commands.describe(item="Der Gegenstand", time="Zeitraum in Minuten")
    async def giveaway(self, interaction: discord.Interaction, item: str, time: int):
        settings = self.bot.get_settings()
        if not settings.get("giveaway_enabled", False):
            await interaction.response.send_message("Giveaway ist deaktiviert.", ephemeral=True)
            return

        end_time = datetime.now() + timedelta(minutes=time)
        giveaway_id = random.randint(1000, 9999)

        desc_text = settings.get("giveaway_embed_description", "Gegenstand: {item}\nEndet in: {time}").format(item=item, time=f"{time} Minuten")
        send_as_embed = bool(settings.get("giveaway_send_as_embed", True))
        embed = discord.Embed(
            title=settings.get("giveaway_embed_title", "🎉 Giveaway!"),
            description=desc_text,
            color=int(settings.get("giveaway_embed_color", "#ff4500").lstrip("#"), 16)
        )
        embed.set_footer(text=settings.get("giveaway_embed_footer", "Klicke auf Teilnehmen!"))

        view = GiveawayView(giveaway_id)
        if send_as_embed:
            await interaction.response.send_message(embed=embed, view=view)
        else:
            plain_text = f"{settings.get('giveaway_embed_title', '🎉 Giveaway!')}\n{desc_text}\n\n{settings.get('giveaway_embed_footer', 'Klicke auf Teilnehmen!')}"
            await interaction.response.send_message(content=plain_text, view=view)
        message = await interaction.original_response()

        await add_giveaway(str(giveaway_id), item, end_time.isoformat(), str(interaction.channel.id), str(message.id), json.dumps([]))

        self.active_giveaways[giveaway_id] = asyncio.create_task(self.end_giveaway(giveaway_id, time * 60))

    @tasks.loop(seconds=30)
    async def check_giveaways(self):
        giveaways = await get_giveaways()
        now = datetime.now()
        for g in giveaways:
            end_time = datetime.fromisoformat(g[2])
            if now >= end_time:
                await self.end_giveaway(g[1], 0)  # giveaway_id

    async def end_giveaway(self, giveaway_id, delay):
        if delay > 0:
            await asyncio.sleep(delay)

        giveaways = await get_giveaways()
        giveaway = next((g for g in giveaways if g[1] == str(giveaway_id)), None)

        if not giveaway:
            return

        participants = json.loads(giveaway[6] or "[]")

        if not participants:
            winner = None
        else:
            winner = random.choice(participants)

        channel = self.bot.get_channel(int(giveaway[3]))
        if channel:
            try:
                message = await channel.fetch_message(int(giveaway[4]))
                if winner:
                    winner_user = self.bot.get_user(winner)
                    winner_text = winner_user.mention if winner_user else f"<@{winner}>"
                else:
                    winner_text = "❌ Keine Teilnehmer."

                if message.embeds:
                    embed = message.embeds[0]
                    embed.description = f"{embed.description or ''}\n\n🏆 Gewinner: {winner_text}"
                    await message.edit(embed=embed, view=None)
                else:
                    final_text = f"{message.content or 'Giveaway beendet'}\n\n🏆 Gewinner: {winner_text}"
                    await message.edit(content=final_text, view=None)
            except Exception:
                pass

        await remove_giveaway(str(giveaway_id))

async def setup(bot):
    await bot.add_cog(Giveaway(bot))