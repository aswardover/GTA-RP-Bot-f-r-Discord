# -*- coding: utf-8 -*-
import os

# BOT CREDENTIALS
# Prefer environment variable in production.
TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
GUILD_ID = 678706941014573059

# DISCORD OAUTH2 FOR DASHBOARD
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "YOUR_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "YOUR_CLIENT_SECRET")
DASHBOARD_REDIRECT_URI = os.getenv("DASHBOARD_REDIRECT_URI", "https://asward-helper.store")  # Für Streamlit

# DATEIPFADE
SETTINGS_FILE = 'settings.json'
LOGO_FILE = 'logo.jpg'

# FARBEN FÜR EMBEDS
COLOR_PRIMARY = 0x38bdf8
COLOR_SUCCESS = 0x22c55e
COLOR_ERROR = 0xef4444
COLOR_WARNING = 0xf59e0b
# Backward compatibility for modules using COLOR_INFO.
COLOR_INFO = COLOR_PRIMARY
