# -*- coding: utf-8 -*-
# Ticket-System Cog
# Liest Konfiguration aus settings.json (Dashboard) und erstellt Tickets Panel

import json
import os
from typing import Dict, Any, List
import discord
from discord.ext import commands, tasks
from discord import app_commands
import config
from embeds import create_embed

SETTINGS_FILE = "settings.json"

def load_settings() -> Dict[str, Any]:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

class TicketButton(discord.ui.Button):
    """Button zum Oeffnen eines Tickets"""
    def __init__(self, ticket_index: int, label: str):
        super().__init__(
            style=discord.ButtonStyle.primary,
            label=label,
            custom_id=f"ticket_{ticket_index}"
        )
        self.ticket_index = ticket_index

    async def callback(self, interaction: discord.Interaction):
        """Wird ausgefuehrt wenn Button geklickt wird"""
        guild = interaction.guild
        user = interaction.user

        # User-Ticket-Check
        existing_channel = discord.utils.get(guild.text_channels, name=f"ticket-{user.name.lower()}")
        if existing_channel:
            await interaction.response.send_message("Du hast bereits ein offenes Ticket!", ephemeral=True)
            return

        settings = load_settings()
        tickets_categories: List[Dict[str, Any]] = settings.get('tickets_categories', [])

        # Index-Sicherheit
        if self.ticket_index < 0 or self.ticket_index >= len(tickets_categories):
            await interaction.response.send_message("Dieses Ticket ist nicht mehr verfuegbar.", ephemeral=True)
            return

        ticket_config = tickets_categories[self.ticket_index]
        ticket_name = ticket_config.get('name', 'Ticket')
        category_channel_id = ticket_config.get('category_channel_id')
        auto_role_id = ticket_config.get('auto_role_id')

        # Kategorie-Channel ermitteln (Discord Kategorie, kein Textkanal)
        category = None
        if category_channel_id:
            category = guild.get_channel(category_channel_id)

        # Overwrites
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_channels=True
            )
        }

        # Staff-Rollen aus config hinzufuegen
        for role_id in getattr(config, 'TICKET_STAFF_ROLES', []):
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )

        try:
            # Ticket-Kanal erstellen
            ticket_channel = await guild.create_text_channel(
                name=f"ticket-{user.name}",
                category=category,
                overwrites=overwrites,
                topic=f"Ticket von {user.name} | Typ: {ticket_name}"
            )

            # Auto-Rolle aus Kategorie vergeben (optional)
            if auto_role_id:
                role = guild.get_role(auto_role_id)
                if role:
                    await user.add_roles(role)

            # Willkommens-Embed
            embed = create_embed(
                title=f"Ticket: {ticket_name}",
                description=(
                    f"Hallo {user.mention}!\n"
                    f"Vielen Dank fuer deine Anfrage.\n"
                    f"Ein Teammitglied wird sich in Kuerze um dein Anliegen kuemmern.\n"
                    f"Bitte beschreibe dein Anliegen so genau wie moeglich."
                ),
                color=config.COLOR_PRIMARY,
                thumbnail=getattr(config, 'BOT_LOGO_URL', None)
            )
            embed.add_field(name="Ticket-Typ", value=ticket_name, inline=True)
            embed.add_field(name="Erstellt von", value=user.mention, inline=True)

            # Close-Button
            close_button = discord.ui.Button(
                style=discord.ButtonStyle.danger,
                label="Ticket schliessen",
                emoji="🔒",
                custom_id="close_ticket"
            )

            async def close_callback(button_interaction: discord.Interaction):
                if button_interaction.user == user or any(
                    role.id in getattr(config, 'TICKET_STAFF_ROLES', [])
                    for role in button_interaction.user.roles
                ):
                    await button_interaction.response.send_message("Ticket wird geschlossen...", ephemeral=True)
                    await ticket_channel.delete(reason=f"Ticket geschlossen von {button_interaction.user.name}")
                else:
                    await button_interaction.response.send_message(
                        "Du hast keine Berechtigung, dieses Ticket zu schliessen!", ephemeral=True
                    )

            close_button.callback = close_callback
            view = discord.ui.View(timeout=None)
            view.add_item(close_button)

            await ticket_channel.send(embed=embed, view=view)

            # Bestaetigung an User
            await interaction.response.send_message(
                f"✅ Dein Ticket wurde erstellt: {ticket_channel.mention}",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(f"Fehler beim Erstellen des Tickets: {str(e)}", ephemeral=True)


class TicketView(discord.ui.View):
    """View mit allen Ticket-Buttons aus settings.json"""
    def __init__(self, tickets_categories: List[Dict[str, Any]]):
        super().__init__(timeout=None)
        for idx, cat in enumerate(tickets_categories):
            name = (cat.get('name') or '').strip()
            if not name:
                continue
            button = TicketButton(ticket_index=idx, label=name)
            self.add_item(button)


class Tickets(commands.Cog):
    """Ticket-System Cog (Dashboard-integriert)"""

    def __init__(self, bot):
        self.bot = bot
        self.check_publish_flag.start()

    def cog_unload(self):
        self.check_publish_flag.cancel()

    async def publish_panel(self, guild: discord.Guild):
        """Liest settings.json und postet das Panel in den eingestellten Channel"""
        settings = load_settings()
        if not settings.get('tickets_enabled', False):
            return
        panel_channel_id = settings.get('tickets_panel_channel_id')
        tickets_categories: List[Dict[str, Any]] = settings.get('tickets_categories', [])
        if not panel_channel_id or not isinstance(panel_channel_id, int):
            return
        if not tickets_categories:
            return
        channel = guild.get_channel(panel_channel_id)
        if not channel:
            return

        # Embed bauen
        embed = create_embed(
            title="Ticket-System",
            description="Waehle unten eine Kategorie aus, um ein Ticket zu oeffnen.\n\n**Verfuegbare Ticket-Kategorien**",
            color=config.COLOR_PRIMARY,
            thumbnail=getattr(config, 'BOT_LOGO_URL', None)
        )
        for cat in tickets_categories:
            name = (cat.get('name') or '').strip()
            if not name:
                continue
            embed.add_field(name=name, value="Klicke den passenden Button unten.", inline=True)

        view = TicketView(tickets_categories)

        # Optional vorherige Bot-Panel-Messages loeschen
        try:
            async for msg in channel.history(limit=50):
                if msg.author == guild.me and msg.components:
                    await msg.delete()
        except Exception:
            pass

        await channel.send(embed=embed, view=view)

    @tasks.loop(seconds=10)
    async def check_publish_flag(self):
        """Schaut alle 10s, ob tickets_panel_publish gesetzt wurde, und veroeffentlicht dann"""
        await self.bot.wait_until_ready()
        settings = load_settings()
        if not settings.get('tickets_panel_publish'):
            return

        # Flag zuruecksetzen
        settings['tickets_panel_publish'] = False
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)

        # Panel fuer alle Guilds
        if hasattr(config, 'GUILD_ID'):
            guild = self.bot.get_guild(config.GUILD_ID)
            if guild:
                await self.publish_panel(guild)
        else:
            for guild in self.bot.guilds:
                await self.publish_panel(guild)

    @check_publish_flag.before_loop
    async def before_check_publish_flag(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="ticket-close", description="Schliesst das aktuelle Ticket")
    async def ticket_close(self, interaction: discord.Interaction):
        """Schliesst ein Ticket manuell"""
        # Pruefe ob in einem Ticket-Kanal
        if not interaction.channel.name.startswith('ticket-'):
            await interaction.response.send_message(
                "Dieser Command funktioniert nur in Ticket-Kanaelen!", ephemeral=True
            )
            return

        # Pruefe Berechtigung
        if not any(role.id in getattr(config, 'TICKET_STAFF_ROLES', []) for role in interaction.user.roles):
            await interaction.response.send_message("Du hast keine Berechtigung dazu!", ephemeral=True)
            return

        await interaction.response.send_message("Ticket wird geschlossen...")
        await interaction.channel.delete(reason=f"Ticket geschlossen von {interaction.user.name}")


async def setup(bot):
    await bot.add_cog(Tickets(bot))
