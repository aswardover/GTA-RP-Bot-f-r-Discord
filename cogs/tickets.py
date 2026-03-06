# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from config import SETTINGS_FILE

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

class TicketCategorySelect(discord.ui.Select):
    def __init__(self, categories):
        options = [
            discord.SelectOption(label=cat, value=cat)
            for cat in categories
        ]
        super().__init__(placeholder="Kategorie wählen...", options=options, custom_id="ticket_category_select")

    async def callback(self, interaction: discord.Interaction):
        category_name = self.values[0]
        settings = load_settings()
        guild = interaction.guild
        
        # Ziel-Kategorie (Discord Folder)
        target_cat_id = settings.get("tickets_category_id")
        target_cat = guild.get_channel(int(target_cat_id)) if target_cat_id else None
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        
        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}-{category_name}",
            overwrites=overwrites,
            category=target_cat
        )
        
        ticket_msg = settings.get("tickets_ticket_message", "Wir melden uns bald bei dir!")
        embed = discord.Embed(
            title=f"Ticket: {category_name}",
            description=ticket_msg,
            color=discord.Color.blue()
        )
        
        from cogs.tickets import TicketCloseView
        await channel.send(content=interaction.user.mention, embed=embed, view=TicketCloseView())
        
        await interaction.response.send_message(
            f"Dein Ticket wurde erstellt: {channel.mention}", ephemeral=True
        )

class TicketPanelView(discord.ui.View):
    def __init__(self, categories):
        super().__init__(timeout=None)
        if categories:
            self.add_item(TicketCategorySelect(categories))

    @discord.ui.button(label="Ticket öffnen", style=discord.ButtonStyle.primary, custom_id="ticket_open_btn")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = load_settings()
        categories = settings.get("tickets_categories", [])
        if categories:
            await interaction.response.send_message(
                "Bitte wähle eine Kategorie:", view=TicketPanelView(categories), ephemeral=True
            )
        else:
            # Fallback wenn keine Kategorien definiert sind
            guild = interaction.guild
            target_cat_id = settings.get("tickets_category_id")
            target_cat = guild.get_channel(int(target_cat_id)) if target_cat_id else None
            
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            }
            channel = await guild.create_text_channel(
                name=f"ticket-{interaction.user.name}",
                overwrites=overwrites,
                category=target_cat
            )
            embed = discord.Embed(title="Ticket", description="Support wird sich melden.", color=discord.Color.blue())
            await channel.send(content=interaction.user.mention, embed=embed, view=TicketCloseView())
            await interaction.response.send_message(f"Ticket erstellt: {channel.mention}", ephemeral=True)

class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket schließen", style=discord.ButtonStyle.red, custom_id="ticket_close_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket wird geschlossen...", ephemeral=True)
        await interaction.channel.delete()

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(TicketCloseView())
        self.bot.add_view(TicketPanelView([])) # Für Persistenz

    @app_commands.command(name="ticket_panel", description="Ticket-Panel manuell posten")
    @app_commands.default_permissions(administrator=True)
    async def ticket_panel(self, interaction: discord.Interaction):
        settings = load_settings()
        categories = settings.get("tickets_categories", [])
        title = settings.get("tickets_panel_title", "Ticket-System")
        
        embed = discord.Embed(title=title, description="Klicke auf den Button um ein Ticket zu öffnen.", color=discord.Color.blurple())
        view = TicketPanelView(categories)
        
        await interaction.response.send_message("Panel wird gesendet...", ephemeral=True)
        await interaction.channel.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
