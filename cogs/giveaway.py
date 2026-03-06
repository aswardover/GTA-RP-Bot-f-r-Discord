# -*- coding: utf-8 -*-
import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import random
from datetime import datetime, timedelta
from database import add_giveaway, get_giveaways, remove_giveaway

class GiveawayView(discord.ui.View):
    def __init__(self, giveaway_id):
        super().__init__(timeout=None)
        self.giveaway_id = giveaway_id

    @discord.ui.button(label="Teilnehmen", style=discord.ButtonStyle.green, custom_id="giveaway_join")
    async def join_giveaway(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_giveaway_data()
        if str(self.giveaway_id) not in data:
            await interaction.response.send_message("Giveaway nicht gefunden.", ephemeral=True)
            return

        giveaway = data[str(self.giveaway_id)]
        if interaction.user.id in giveaway["participants"]:
            await interaction.response.send_message("Du nimmst bereits teil!", ephemeral=True)
        else:
            giveaway["participants"].append(interaction.user.id)
            save_giveaway_data(data)
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

        embed = discord.Embed(
            title=settings.get("giveaway_embed_title", "🎉 Giveaway!"),
            description=settings.get("giveaway_embed_description", "Gegenstand: {item}\nEndet in: {time}").format(item=item, time=f"{time} Minuten"),
            color=int(settings.get("giveaway_embed_color", "#ff4500").lstrip("#"), 16)
        )
        embed.set_footer(text=settings.get("giveaway_embed_footer", "Klicke auf Teilnehmen!"))

        view = GiveawayView(giveaway_id)
        message = await interaction.response.send_message(embed=embed, view=view)

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
                await remove_giveaway(g[1])

    async def end_giveaway(self, giveaway_id, delay):
        if delay > 0:
            await asyncio.sleep(delay)

        data = load_giveaway_data()
        if str(giveaway_id) not in data:
            return

        giveaway = data[str(giveaway_id)]
        participants = giveaway["participants"]

        if not participants:
            winner = None
        else:
            winner = random.choice(participants)

        channel = self.bot.get_channel(giveaway["channel_id"])
        if channel:
            try:
                message = await channel.fetch_message(giveaway["message_id"])
                embed = message.embeds[0]
                if winner:
                    winner_user = self.bot.get_user(winner)
                    embed.description += f"\n\n🏆 Gewinner: {winner_user.mention}"
                else:
                    embed.description += "\n\n❌ Keine Teilnehmer."
                await message.edit(embed=embed, view=None)
            except:
                pass

        del data[str(giveaway_id)]
        save_giveaway_data(data)

async def setup(bot):
    await bot.add_cog(Giveaway(bot))