# -*- coding: utf-8 -*-
"""Discord OAuth2 Helfer."""

import requests
from urllib.parse import urlencode

from config import DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, DASHBOARD_REDIRECT_URI

# Discord OAuth2 URLs
DISCORD_AUTH_URL = "https://discord.com/api/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_USER_URL = "https://discord.com/api/users/@me"


def oauth_is_configured():
    client_id = str(DISCORD_CLIENT_ID or "").strip()
    client_secret = str(DISCORD_CLIENT_SECRET or "").strip()
    if not client_id or client_id.startswith("YOUR_"):
        return False
    if not client_secret or client_secret.startswith("YOUR_"):
        return False
    if not client_id.isdigit():
        return False
    return True


def get_discord_auth_url():
    params = {
        "client_id": DISCORD_CLIENT_ID,
        "redirect_uri": DASHBOARD_REDIRECT_URI,
        "response_type": "code",
        "scope": "identify"
    }
    url = DISCORD_AUTH_URL + "?" + urlencode(params)
    return url


def get_bot_invite_url(guild_id=None, permissions="8", disable_guild_select=False):
    params = {
        "client_id": DISCORD_CLIENT_ID,
        "scope": "bot applications.commands",
        "permissions": str(permissions or "8"),
    }
    guild_id_str = str(guild_id or "").strip()
    if guild_id_str:
        params["guild_id"] = guild_id_str
        params["disable_guild_select"] = "true" if disable_guild_select else "false"
    return f"https://discord.com/oauth2/authorize?{urlencode(params)}"


def exchange_code_for_token(code):
    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DASHBOARD_REDIRECT_URI
    }
    response = requests.post(DISCORD_TOKEN_URL, data=data)
    return response.json()


def get_user_info(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(DISCORD_USER_URL, headers=headers)
    return response.json()
