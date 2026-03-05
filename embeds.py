# -*- coding: utf-8 -*-
import discord
import config
from datetime import datetime
import json
import os

SETTINGS_FILE = "settings.json"


def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _get_color_from_hex(hex_str, fallback: int) -> int:
    if not hex_str:
        return fallback
    try:
        return int(hex_str.replace("#", ""), 16)
    except Exception:
        return fallback


def create_embed(
    title: str = None,
    description: str = None,
    color: int = None,
    thumbnail: str = None,
    image: str = None,
    fields: list = None,
    footer: str = None
) -> discord.Embed:
    settings = load_settings()

    if color is None:
        hex_default = settings.get("embed_default_color")
        color = _get_color_from_hex(hex_default, config.COLOR_PRIMARY)

    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now()
    )

    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if image:
        embed.set_image(url=image)
    if fields:
        for field in fields:
            embed.add_field(
                name=field.get("name", ""),
                value=field.get("value", ""),
                inline=field.get("inline", False)
            )

    footer_text = footer
    if not footer_text:
        footer_text = settings.get("embed_default_footer") or settings.get("embed_footer")
    use_footer = settings.get("embed_use_footer", True)
    if footer_text and use_footer:
        embed.set_footer(text=footer_text)

    return embed


def success_embed(title: str, description: str) -> discord.Embed:
    return create_embed(title=f"✅ {title}", description=description, color=config.COLOR_SUCCESS)


def error_embed(title: str, description: str) -> discord.Embed:
    return create_embed(title=f"❌ {title}", description=description, color=config.COLOR_ERROR)


def warning_embed(title: str, description: str) -> discord.Embed:
    return create_embed(title=f"⚠️ {title}", description=description, color=config.COLOR_WARNING)


def info_embed(title: str, description: str) -> discord.Embed:
    return create_embed(title=f"ℹ️ {title}", description=description, color=config.COLOR_INFO)
