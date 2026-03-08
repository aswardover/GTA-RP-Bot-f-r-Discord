# -*- coding: utf-8 -*-
# Ticket-System Cog (MEE6-style core features)

import io
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import discord
from discord.ext import commands, tasks
from discord import app_commands
from embeds import create_embed
from config import SETTINGS_FILE, COLOR_PRIMARY

STATE_FILE = "tickets_state.json"


def load_settings() -> Dict[str, Any]:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_settings(data: Dict[str, Any]):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_state() -> Dict[str, Any]:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(data: Dict[str, Any]):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_int(value) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def sanitize_channel_name(name: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in name)
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-")[:70] or "ticket"


class TicketOpenButton(discord.ui.Button):
    def __init__(self, cog: "Tickets", option_index: int, label: str, emoji: Optional[str]):
        super().__init__(
            style=discord.ButtonStyle.primary,
            label=label[:80],
            emoji=emoji,
            custom_id=f"ticket_open_{option_index}",
        )
        self.cog = cog
        self.option_index = option_index

    async def callback(self, interaction: discord.Interaction):
        await self.cog.create_ticket(interaction, self.option_index)


class TicketOpenSelect(discord.ui.Select):
    def __init__(self, cog: "Tickets", options_config: List[Dict[str, Any]]):
        options = []
        for idx, cfg in enumerate(options_config):
            label = str(cfg.get("name") or cfg.get("label") or f"Ticket {idx + 1}")[:100]
            description = str(cfg.get("description") or "")[:100]
            emoji = cfg.get("emoji")
            options.append(discord.SelectOption(label=label, description=description or None, emoji=emoji, value=str(idx)))
        super().__init__(
            placeholder="Waehle deine Ticket-Option",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_open_select",
        )
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        await self.cog.create_ticket(interaction, int(self.values[0]))


class TicketPanelView(discord.ui.View):
    def __init__(self, cog: "Tickets", options_config: List[Dict[str, Any]], mode: str):
        super().__init__(timeout=None)
        if mode == "dropdown":
            self.add_item(TicketOpenSelect(cog, options_config))
        else:
            for idx, cfg in enumerate(options_config[:5]):
                label = str(cfg.get("name") or cfg.get("label") or f"Ticket {idx + 1}")
                emoji = cfg.get("emoji")
                self.add_item(TicketOpenButton(cog, idx, label, emoji))


class TicketControlView(discord.ui.View):
    def __init__(self, cog: "Tickets"):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.secondary, emoji="🛠", custom_id="ticket_claim")
    async def claim(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self.cog.claim_ticket(interaction)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="ticket_close")
    async def close(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self.cog.close_ticket(interaction)


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_publish_flag.start()

    def cog_unload(self):
        self.check_publish_flag.cancel()

    def _manager_role_ids(self, settings: Dict[str, Any]) -> List[int]:
        raw = settings.get("tickets_manager_roles", [])
        ids = []
        for item in raw:
            parsed = parse_int(item)
            if parsed is not None:
                ids.append(parsed)
        return ids

    def _is_manager(self, user: discord.Member, settings: Dict[str, Any]) -> bool:
        if user.guild_permissions.administrator or user.guild_permissions.manage_channels:
            return True
        manager_ids = set(self._manager_role_ids(settings))
        if not manager_ids:
            return False
        return any(role.id in manager_ids for role in user.roles)

    def _options(self, settings: Dict[str, Any]) -> List[Dict[str, Any]]:
        raw = settings.get("tickets_categories", [])
        if not isinstance(raw, list):
            return [{"name": "Ticket oeffnen", "description": "Unser Team kann dir helfen!", "emoji": "📩"}]

        normalized: List[Dict[str, Any]] = []
        for item in raw:
            if isinstance(item, str):
                normalized.append({"name": item, "description": "", "emoji": "📩"})
            elif isinstance(item, dict):
                name = str(item.get("name") or item.get("label") or "Ticket oeffnen")
                normalized.append(
                    {
                        "name": name,
                        "description": str(item.get("description") or ""),
                        "emoji": item.get("emoji") or "📩",
                        "category_channel_id": item.get("category_channel_id"),
                        "auto_role_id": item.get("auto_role_id"),
                    }
                )
        if not normalized:
            normalized.append({"name": "Ticket oeffnen", "description": "Unser Team kann dir helfen!", "emoji": "📩"})
        return normalized[:25]

    async def create_ticket(self, interaction: discord.Interaction, option_index: int):
        guild = interaction.guild
        user = interaction.user
        if guild is None:
            await interaction.response.send_message("Dieser Button funktioniert nur auf dem Server.", ephemeral=True)
            return

        settings = load_settings()
        if not settings.get("tickets_enabled", False):
            await interaction.response.send_message("Tickets sind aktuell deaktiviert.", ephemeral=True)
            return

        options = self._options(settings)
        if option_index < 0 or option_index >= len(options):
            await interaction.response.send_message("Diese Ticket-Option ist nicht mehr verfuegbar.", ephemeral=True)
            return

        state = load_state()
        for channel_id, info in state.items():
            if str(info.get("creator_id")) == str(user.id):
                channel = guild.get_channel(parse_int(channel_id) or 0)
                if channel is not None:
                    await interaction.response.send_message(f"Du hast bereits ein offenes Ticket: {channel.mention}", ephemeral=True)
                    return

        option = options[option_index]
        open_category_id = parse_int(settings.get("tickets_open_category_id")) or parse_int(option.get("category_channel_id"))
        category = guild.get_channel(open_category_id) if open_category_id else None

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True, manage_messages=True),
        }
        for role_id in self._manager_role_ids(settings):
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True)

        channel_name = f"ticket-{sanitize_channel_name(user.display_name)}"
        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"ticket_owner:{user.id}",
        )

        auto_role_id = parse_int(option.get("auto_role_id"))
        if auto_role_id:
            role = guild.get_role(auto_role_id)
            if role:
                await user.add_roles(role)

        embed = create_embed(
            title=f"🎫 {option.get('name', 'Ticket')}",
            description=(
                f"Hallo {user.mention}, dein Ticket wurde erstellt.\n"
                f"{option.get('description') or 'Ein Teammitglied kuemmert sich gleich um dich.'}"
            ),
            color=COLOR_PRIMARY,
        )
        await ticket_channel.send(embed=embed, view=TicketControlView(self))

        state[str(ticket_channel.id)] = {
            "creator_id": user.id,
            "creator_tag": str(user),
            "option_name": option.get("name"),
            "claimed_by": None,
            "created_at": datetime.utcnow().isoformat(),
        }
        save_state(state)

        await interaction.response.send_message(f"✅ Ticket erstellt: {ticket_channel.mention}", ephemeral=True)

    async def claim_ticket(self, interaction: discord.Interaction):
        channel = interaction.channel
        settings = load_settings()
        if not isinstance(channel, discord.TextChannel) or not channel.name.startswith("ticket-"):
            await interaction.response.send_message("Nur in Ticket-Kanaelen nutzbar.", ephemeral=True)
            return
        if not self._is_manager(interaction.user, settings):
            await interaction.response.send_message("Keine Berechtigung (Ticket Manager).", ephemeral=True)
            return

        state = load_state()
        info = state.get(str(channel.id), {})
        info["claimed_by"] = interaction.user.id
        state[str(channel.id)] = info
        save_state(state)

        claimed_category_id = parse_int(settings.get("tickets_claimed_category_id"))
        if claimed_category_id:
            claimed_category = interaction.guild.get_channel(claimed_category_id)
            if isinstance(claimed_category, discord.CategoryChannel):
                await channel.edit(category=claimed_category)

        await interaction.response.send_message(f"🛠 Ticket wurde von {interaction.user.mention} uebernommen.")

    async def _build_transcript(self, channel: discord.TextChannel) -> bytes:
        lines = [f"Transcript for #{channel.name}", f"Generated: {datetime.utcnow().isoformat()} UTC", ""]
        messages = [m async for m in channel.history(limit=None, oldest_first=True)]
        for m in messages:
            created = m.created_at.strftime("%Y-%m-%d %H:%M:%S")
            content = m.content.replace("\n", " ") if m.content else ""
            lines.append(f"[{created}] {m.author}: {content}")
        return "\n".join(lines).encode("utf-8")

    async def close_ticket(self, interaction: discord.Interaction):
        channel = interaction.channel
        settings = load_settings()
        if not isinstance(channel, discord.TextChannel) or not channel.name.startswith("ticket-"):
            await interaction.response.send_message("Nur in Ticket-Kanaelen nutzbar.", ephemeral=True)
            return

        state = load_state()
        info = state.get(str(channel.id), {})
        creator_id = parse_int(info.get("creator_id"))
        is_creator = creator_id is not None and interaction.user.id == creator_id
        if not is_creator and not self._is_manager(interaction.user, settings):
            await interaction.response.send_message("Keine Berechtigung, dieses Ticket zu schliessen.", ephemeral=True)
            return

        await interaction.response.send_message("🔒 Ticket wird geschlossen...")

        transcript_bytes = await self._build_transcript(channel)
        transcript_file = discord.File(io.BytesIO(transcript_bytes), filename=f"transcript-{channel.id}.txt")

        transcript_channel_id = parse_int(settings.get("tickets_transcript_channel_id"))
        if transcript_channel_id:
            transcript_channel = interaction.guild.get_channel(transcript_channel_id)
            if transcript_channel:
                await transcript_channel.send(
                    content=f"📄 Transcript von {channel.mention} (geschlossen von {interaction.user.mention})",
                    file=transcript_file,
                )

        if settings.get("tickets_transcript_dm_enabled", False) and creator_id:
            creator = interaction.guild.get_member(creator_id)
            if creator:
                try:
                    await creator.send(
                        content=f"📄 Hier ist dein Ticket-Transcript von **{interaction.guild.name}**.",
                        file=discord.File(io.BytesIO(transcript_bytes), filename=f"transcript-{channel.id}.txt"),
                    )
                except Exception:
                    pass

        closed_category_id = parse_int(settings.get("tickets_closed_category_id"))
        delete_on_close = settings.get("tickets_delete_on_close", True)
        if not delete_on_close and closed_category_id:
            closed_category = interaction.guild.get_channel(closed_category_id)
            if isinstance(closed_category, discord.CategoryChannel):
                await channel.edit(category=closed_category, name=f"closed-{channel.name}"[:95])
                return

        state.pop(str(channel.id), None)
        save_state(state)
        await channel.delete(reason=f"Ticket geschlossen von {interaction.user}")

    async def publish_panel(self, guild: discord.Guild):
        settings = load_settings()
        if not settings.get("tickets_enabled", False):
            return

        panel_channel_id = parse_int(settings.get("tickets_panel_channel_id"))
        if panel_channel_id is None:
            return
        channel = guild.get_channel(panel_channel_id)
        if not isinstance(channel, discord.TextChannel):
            return

        options = self._options(settings)
        panel_mode = str(settings.get("tickets_panel_mode", "buttons")).lower()
        if panel_mode not in {"buttons", "dropdown"}:
            panel_mode = "buttons"

        title = settings.get("tickets_panel_title", "🎫 Ticket-System")
        description = settings.get("tickets_panel_description", "Waehle eine Option, um ein Ticket zu erstellen.")
        embed = create_embed(title=title, description=description, color=COLOR_PRIMARY)
        for opt in options[:10]:
            embed.add_field(
                name=f"{opt.get('emoji') or '📩'} {opt.get('name')}",
                value=opt.get("description") or "Ticket-Option",
                inline=False,
            )

        # Alte Panels aufraeumen
        try:
            async for msg in channel.history(limit=50):
                if msg.author == guild.me and msg.components:
                    await msg.delete()
        except Exception:
            pass

        await channel.send(embed=embed, view=TicketPanelView(self, options, panel_mode))

    @tasks.loop(seconds=5)
    async def check_publish_flag(self):
        settings = load_settings()
        if not settings.get("tickets_publish_trigger", False):
            return

        settings["tickets_publish_trigger"] = False
        save_settings(settings)

        if getattr(self.bot, "guilds", None):
            for guild in self.bot.guilds:
                await self.publish_panel(guild)

    @check_publish_flag.before_loop
    async def before_check_publish_flag(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="ticket-close", description="Schliesst das aktuelle Ticket")
    async def ticket_close(self, interaction: discord.Interaction):
        await self.close_ticket(interaction)


async def setup(bot):
    await bot.add_cog(Tickets(bot))
