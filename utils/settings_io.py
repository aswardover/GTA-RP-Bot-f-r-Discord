# -*- coding: utf-8 -*-
"""Settings / Discord-Daten laden, speichern, Server-Verwaltung."""

import os
import json
import time
import datetime
import streamlit as st
from copy import deepcopy

from config import SETTINGS_FILE
from utils.helpers import _normalize_server_key

# ── Konstanten ───────────────────────────────────────────────────
DISCORD_DATA_FILE = "discord_data.json"
TICKETS_STATE_FILE = "tickets_state.json"
AUTO_SYNC_STALE_AFTER_SECONDS = 60
AUTO_SYNC_COOLDOWN_SECONDS = 45


# ── Low-Level I/O ────────────────────────────────────────────────

def _safe_read_json(path, fallback):
    if not os.path.exists(path):
        return deepcopy(fallback)
    for i in range(3):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError, IOError):
            if i < 2:
                time.sleep(0.1)
                continue
            return deepcopy(fallback)
    return deepcopy(fallback)


# ── Cached Loaders ───────────────────────────────────────────────

@st.cache_data(ttl=3)
def _load_settings_cached(version_token):
    return _safe_read_json(SETTINGS_FILE, {})


@st.cache_data(ttl=10)
def _load_discord_data_cached(version_token):
    return _safe_read_json(DISCORD_DATA_FILE, {"channels": {}, "roles": {}, "categories": {}, "guilds": []})


def _settings_version_token():
    try:
        return int(os.path.getmtime(SETTINGS_FILE))
    except OSError:
        return 0


def _discord_version_token():
    try:
        return int(os.path.getmtime(DISCORD_DATA_FILE))
    except OSError:
        return 0


def _write_raw_settings(raw_settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(raw_settings, f, indent=4, ensure_ascii=False)
    _load_settings_cached.clear()


# ── Public Load / Save ───────────────────────────────────────────

def load_settings():
    return _load_settings_cached(_settings_version_token())


def save_settings(settings):
    active_server_key = st.session_state.get("active_server_key")
    payload = deepcopy(settings) if isinstance(settings, dict) else {}

    if active_server_key:
        raw_settings = _safe_read_json(SETTINGS_FILE, {})
        profiles = raw_settings.get("server_profiles", {})
        if not isinstance(profiles, dict):
            profiles = {}

        profile_data = deepcopy(payload)
        profile_data.pop("server_profiles", None)
        profiles[active_server_key] = profile_data

        merged = deepcopy(raw_settings)
        merged.update(profile_data)
        merged["server_profiles"] = profiles
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(merged, f, indent=4, ensure_ascii=False)
    else:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=4, ensure_ascii=False)

    _load_settings_cached.clear()


def load_discord_data():
    return _load_discord_data_cached(_discord_version_token())


def save_discord_data(data):
    with open(DISCORD_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    _load_discord_data_cached.clear()


def load_reaction_roles():
    if os.path.exists("reaction_roles.json"):
        with open("reaction_roles.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_reaction_roles(data):
    with open("reaction_roles.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ── Sync-Helfer ──────────────────────────────────────────────────

def request_discord_data_sync():
    """Setzt ein Trigger-Flag, das der laufende Bot verarbeitet und danach discord_data.json aktualisiert."""
    settings = load_settings()
    settings["discord_data_sync_trigger"] = True
    save_settings(settings)
    return True, "Sync angefordert. In wenigen Sekunden sind Channels/Kategorien aktualisiert."


def _discord_data_age_seconds(discord_data):
    if not isinstance(discord_data, dict):
        return None
    meta = discord_data.get("meta", {})
    if not isinstance(meta, dict):
        return None
    exported_at = str(meta.get("exported_at") or "").strip()
    if not exported_at:
        return None
    try:
        ts = datetime.datetime.fromisoformat(exported_at.replace("Z", "+00:00"))
    except Exception:
        return None
    now = datetime.datetime.now(datetime.timezone.utc)
    return max(0.0, (now - ts).total_seconds())


def _auto_sync_discord_data_if_needed(
    discord_data,
    stale_after_seconds=AUTO_SYNC_STALE_AFTER_SECONDS,
    cooldown_seconds=AUTO_SYNC_COOLDOWN_SECONDS,
):
    age_seconds = _discord_data_age_seconds(discord_data)
    is_stale = age_seconds is None or age_seconds >= float(stale_after_seconds)

    now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
    last_request_ts = float(st.session_state.get("dashboard_last_auto_sync_request_ts", 0.0) or 0.0)
    in_cooldown = (now_ts - last_request_ts) < float(cooldown_seconds)

    requested = False
    if is_stale and not in_cooldown:
        ok, _ = request_discord_data_sync()
        if ok:
            st.session_state.dashboard_last_auto_sync_request_ts = now_ts
            requested = True

    return {
        "requested": requested,
        "age_seconds": age_seconds,
        "is_stale": is_stale,
    }


# ── Server-Verwaltung ────────────────────────────────────────────

def _register_dashboard_server(server_name, guild_id=None):
    label = str(server_name or "").strip()
    if not label:
        return None
    guild_id_str = str(guild_id or "").strip()
    server_key = _normalize_server_key(guild_id_str or label)

    raw_settings = _safe_read_json(SETTINGS_FILE, {})
    servers = raw_settings.get("dashboard_servers", [])
    if not isinstance(servers, list):
        servers = []

    updated = False
    for item in servers:
        if isinstance(item, dict) and _normalize_server_key(item.get("key") or item.get("guild_id") or item.get("label")) == server_key:
            item["label"] = label
            item["guild_id"] = guild_id_str
            item["key"] = server_key
            updated = True
            break

    if not updated:
        servers.append({"label": label, "guild_id": guild_id_str, "key": server_key})

    raw_settings["dashboard_servers"] = servers
    profiles = raw_settings.get("server_profiles", {})
    if not isinstance(profiles, dict):
        profiles = {}
    if server_key not in profiles:
        profiles[server_key] = {}
    raw_settings["server_profiles"] = profiles
    _write_raw_settings(raw_settings)
    return server_key


def _build_server_entries(discord_data, settings):
    entries = []
    raw_guilds = discord_data.get("guilds", []) if isinstance(discord_data, dict) else []
    if isinstance(raw_guilds, dict):
        for name, gid in raw_guilds.items():
            label = str(name).strip() or f"Server {gid}"
            gid_str = str(gid).strip()
            entries.append({"label": label, "key": _normalize_server_key(gid_str or label), "guild_id": gid_str})
    elif isinstance(raw_guilds, list):
        for item in raw_guilds:
            if isinstance(item, dict):
                label = str(item.get("name") or item.get("guild_name") or item.get("label") or "").strip()
                gid = str(item.get("id") or item.get("guild_id") or "").strip()
                if label or gid:
                    entries.append({"label": label or f"Server {gid}", "key": _normalize_server_key(gid or label), "guild_id": gid})
            elif isinstance(item, str) and item.strip():
                label = item.strip()
                entries.append({"label": label, "key": _normalize_server_key(label), "guild_id": ""})

    manual_servers = settings.get("dashboard_servers", []) if isinstance(settings, dict) else []
    if isinstance(manual_servers, list):
        for item in manual_servers:
            if isinstance(item, dict):
                label = str(item.get("label") or "").strip()
                gid = str(item.get("guild_id") or "").strip()
                key = str(item.get("key") or "").strip()
                if label or gid or key:
                    entries.append(
                        {
                            "label": label or f"Server {gid}" if gid else "Neuer Server",
                            "key": _normalize_server_key(key or gid or label),
                            "guild_id": gid,
                        }
                    )

    if not entries:
        fallback_name = str(settings.get("dashboard_server_name", "ASWARD Server")).strip() or "ASWARD Server"
        entries = [{"label": fallback_name, "key": "default", "guild_id": ""}]

    unique = {}
    for entry in entries:
        unique[entry["key"]] = entry
    return list(unique.values())


def _effective_settings_for_server(raw_settings, server_key):
    effective = deepcopy(raw_settings) if isinstance(raw_settings, dict) else {}
    profiles = raw_settings.get("server_profiles", {}) if isinstance(raw_settings, dict) else {}
    profile = profiles.get(server_key, {}) if isinstance(profiles, dict) else {}
    if isinstance(profile, dict):
        effective.update(deepcopy(profile))
    return effective


def _allowed_ids_for_server(raw_settings, server_key):
    profiles = raw_settings.get("server_profiles", {}) if isinstance(raw_settings, dict) else {}
    profile = profiles.get(server_key, {}) if isinstance(profiles, dict) else {}
    allowed = profile.get("dashboard_allowed_users", []) if isinstance(profile, dict) else []
    return {str(x).strip() for x in allowed if str(x).strip()}


def _set_allowed_ids_for_server(server_key, allowed_ids):
    raw_settings = _safe_read_json(SETTINGS_FILE, {})
    profiles = raw_settings.get("server_profiles", {})
    if not isinstance(profiles, dict):
        profiles = {}
    profile = profiles.get(server_key, {})
    if not isinstance(profile, dict):
        profile = {}
    profile["dashboard_allowed_users"] = [str(x).strip() for x in (allowed_ids or []) if str(x).strip()]
    profiles[server_key] = profile
    raw_settings["server_profiles"] = profiles
    _write_raw_settings(raw_settings)


def _live_ticket_count_for_selected(server_entry):
    state = _safe_read_json(TICKETS_STATE_FILE, {})
    if not isinstance(state, dict):
        return 0
    guild_id = str((server_entry or {}).get("guild_id") or "").strip()
    if not guild_id:
        return len(state)
    return sum(
        1
        for info in state.values()
        if isinstance(info, dict) and str(info.get("guild_id") or "").strip() == guild_id
    )
