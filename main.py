# -*- coding: utf-8 -*-
import discord
from discord.ext import commands, tasks
import os
import json
import logging
import asyncio
import datetime
from config import TOKEN, SETTINGS_FILE
from embeds import success_embed, error_embed
from collections import defaultdict
import time
from database import init_db

BOT_RUNTIME_FILE = "bot_runtime.json"

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('GTA-RP-Bot')

# ── Settings-Watcher Hilfsfunktionen ──────────────────────────
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

def write_runtime_status(online: bool, detail: str = ""):
    payload = {
        "online": bool(online),
        "detail": str(detail or ""),
        "last_seen": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
    try:
        with open(BOT_RUNTIME_FILE, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.presences = True
        intents.message_content = True
        intents.guilds = True
        intents.reactions = True  # Für Reaction Roles
        super().__init__(command_prefix='!', intents=intents, help_command=None)
        self.rate_limits = defaultdict(float)

    def get_settings(self):
        # Cache settings
        if not hasattr(self, '_settings_cache') or not self._settings_cache:
            self._settings_cache = load_settings()
        return self._settings_cache

    def invalidate_settings_cache(self):
        self._settings_cache = None

    async def on_interaction(self, interaction):
        # Rate limiting for slash commands
        user_id = interaction.user.id
        command_name = interaction.command.name if interaction.command else "unknown"
        key = f"{user_id}_{command_name}"
        now = time.time()
        if now - self.rate_limits[key] < 1:  # 1 second cooldown per command per user
            await interaction.response.send_message("Zu schnell! Warte einen Moment.", ephemeral=True)
            return
        self.rate_limits[key] = now
        await super().on_interaction(interaction)

    async def setup_hook(self):
        await init_db()
        # Alle Cogs laden
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    logger.info(f'Cog geladen: {filename}')
                except Exception as e:
                    logger.error(f'Fehler beim Laden von {filename}: {e}')
        # Settings-Watcher starten
        self.settings_watcher.start()
        # Cleanup-Task starten
        self.cleanup_rate_limits.start()

    async def on_ready(self):
        logger.info(f'{self.user} ist bereit und online!')
        write_runtime_status(True, "ready")
        try:
            synced = await self.tree.sync()
            logger.info(f'{len(synced)} globale Slash-Befehle synchronisiert!')
        except Exception as e:
            logger.error(f'Fehler beim Synchronisieren: {e}')
        # Status setzen
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="GTA RP Server"
            )
        )

    async def on_disconnect(self):
        write_runtime_status(False, "disconnect")

    async def on_resumed(self):
        write_runtime_status(True, "resumed")

    @tasks.loop(seconds=5)
    async def settings_watcher(self):
        """Prueft alle 5 Sekunden ob das Dashboard einen Publish-Trigger gesetzt hat."""
        try:
            write_runtime_status(True, "heartbeat")
            settings = load_settings()
            changed = False

            # ── Ticket-Panel veroeffentlichen ──
            if settings.get('tickets_publish_trigger'):
                try:
                    ticket_cog = self.cogs.get('Tickets')
                    if ticket_cog and hasattr(ticket_cog, 'publish_panel'):
                        for guild in self.guilds:
                            await ticket_cog.publish_panel(guild)
                        logger.info('Ticket-Panel ueber Tickets-Cog veroeffentlicht.')
                    else:
                        logger.warning('Tickets-Cog nicht verfuegbar, Ticket-Panel konnte nicht veroeffentlicht werden.')
                except Exception as e:
                    logger.error(f'Fehler beim Ticket-Panel senden: {e}')
                settings['tickets_publish_trigger'] = False
                changed = True

            # ── Stempeluhr-Panel veroeffentlichen ──
            if settings.get('stempeluhr_publish_trigger'):
                try:
                    channel_id = settings.get('stempeluhr_panel_channel_id')
                    if channel_id:
                        channel = self.get_channel(int(channel_id))
                        if channel:
                            embed = discord.Embed(
                                title='⏱️ Stempeluhr',
                                description='Klicke auf **Einstempeln** wenn du mit der Arbeit beginnst und auf **Ausstempeln** wenn du aufhoerst.',
                                color=0x22c55e
                            )
                            from cogs.stempeluhr import StempelView
                            view = StempelView()
                            await channel.send(embed=embed, view=view)
                            logger.info(f'Stempeluhr-Panel in #{channel.name} gepostet.')
                except Exception as e:
                    logger.error(f'Fehler beim Stempeluhr-Panel senden: {e}')
                settings['stempeluhr_publish_trigger'] = False
                changed = True

            # ── Ankuendigung senden ──
            if settings.get('announce_publish_trigger'):
                try:
                    channel_id = settings.get('announce_channel_id')
                    if channel_id:
                        channel = self.get_channel(int(channel_id))
                        if channel:
                            title = settings.get('announce_title', 'Ankuendigung')
                            message = settings.get('announce_message', '')
                            if message:
                                embed = discord.Embed(
                                    title=f'📢 {title}',
                                    description=message,
                                    color=0xf59e0b
                                )
                                await channel.send(embed=embed)
                                logger.info(f'Ankuendigung in #{channel.name} gepostet.')
                except Exception as e:
                    logger.error(f'Fehler beim Ankuendigung senden: {e}')
                settings['announce_publish_trigger'] = False
                changed = True

            # ── Discord-Daten fuer Dashboard synchronisieren ──
            if settings.get('discord_data_sync_trigger'):
                try:
                    exporter = self.cogs.get('DataExporter')
                    if exporter and hasattr(exporter, 'export_data'):
                        await exporter.export_data()
                        logger.info('Discord-Daten fuer Dashboard wurden synchronisiert.')
                    else:
                        logger.warning('DataExporter-Cog nicht verfuegbar, Sync uebersprungen.')
                except Exception as e:
                    logger.error(f'Fehler bei Discord-Daten-Sync: {e}')
                settings['discord_data_sync_trigger'] = False
                changed = True

            if changed:
                save_settings(settings)

        except Exception as e:
            logger.error(f'Settings-Watcher Fehler: {e}')

    @tasks.loop(minutes=5)
    async def cleanup_rate_limits(self):
        """Raeumt alte Rate-Limit-Eintraege auf."""
        now = time.time()
        to_remove = [key for key, ts in self.rate_limits.items() if now - ts > 60]
        for key in to_remove:
            del self.rate_limits[key]

    @settings_watcher.before_loop
    async def before_watcher(self):
        await self.wait_until_ready()

    @cleanup_rate_limits.before_loop
    async def before_cleanup(self):
        await self.wait_until_ready()

bot = MyBot()

if __name__ == "__main__":
    token = (TOKEN or "").strip()
    if not token or token.startswith("YOUR_") or token.lower().startswith("dummy"):
        raise RuntimeError("DISCORD_BOT_TOKEN fehlt oder ist ungueltig. Bitte als Umgebungsvariable setzen.")
    bot.run(TOKEN)
