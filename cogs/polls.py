# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from database import add_poll, get_polls, update_poll_votes

class PollButton(discord.ui.Button):
    def __init__(self, label, poll_id, option_index):
        super().__init__(label=label, style=discord.ButtonStyle.primary, custom_id=f"poll_{poll_id}_{option_index}")
        self.poll_id = poll_id
        self.option_index = option_index

    async def callback(self, interaction):
        polls = await get_polls()
        poll = next((p for p in polls if p[1] == str(self.poll_id)), None)
        if poll:
            votes = json.loads(poll[5])
            counts = json.loads(poll[6])
            user_id = str(interaction.user.id)
            if user_id not in votes:
                votes[user_id] = self.option_index
                counts[self.option_index] += 1
                await update_poll_votes(str(self.poll_id), json.dumps(votes), json.dumps(counts))
                await interaction.response.send_message("Stimme abgegeben!", ephemeral=True)
            else:
                await interaction.response.send_message("Du hast bereits abgestimmt!", ephemeral=True)

class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="poll", description="Erstelle eine Umfrage")
    @app_commands.describe(question="Die Frage", options="Optionen (kommasepariert)", anonymous="Anonym?")
    async def poll(self, interaction: discord.Interaction, question: str, options: str, anonymous: bool = False):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("Keine Berechtigung!", ephemeral=True)
            return

        option_list = [opt.strip() for opt in options.split(",") if opt.strip()]
        if len(option_list) < 2 or len(option_list) > 10:
            await interaction.response.send_message("2-10 Optionen!", ephemeral=True)
            return

        settings = self.bot.get_settings()
        send_as_embed = bool(settings.get("poll_send_as_embed", True))
        embed = discord.Embed(
            title=settings.get("poll_embed_title", "📊 Umfrage"),
            description=f"**{question}**\n\n" + "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(option_list)]),
            color=int(settings.get("poll_embed_color", "#8a2be2").lstrip("#"), 16)
        )
        embed.set_footer(text=settings.get("poll_embed_footer", "Stimme ab!"))

        view = discord.ui.View()
        for i, opt in enumerate(option_list):
            view.add_item(PollButton(opt, interaction.id, i))

        if send_as_embed:
            await interaction.response.send_message(embed=embed, view=view)
        else:
            plain_text = f"{settings.get('poll_embed_title', '📊 Umfrage')}\n\n{question}\n" + "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(option_list)])
            await interaction.response.send_message(content=plain_text, view=view)
        message = await interaction.original_response()

        await add_poll(str(interaction.id), question, json.dumps(option_list), anonymous, json.dumps({}), json.dumps([0] * len(option_list)), str(interaction.channel.id), str(message.id))

async def setup(bot):
    await bot.add_cog(Polls(bot))