# -*- coding: utf-8 -*-
"""Reine Hilfsfunktionen ohne Streamlit- oder Datei-Abhängigkeiten."""

from copy import deepcopy


# ── Normalisierungen ─────────────────────────────────────────────

def _normalize_server_key(value):
    key = str(value or "default").strip().lower()
    cleaned = "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in key)
    cleaned = "-".join([part for part in cleaned.split("-") if part])
    return cleaned or "default"


def _normalize_custom_command(raw):
    item = raw if isinstance(raw, dict) else {}
    return {
        "name": str(item.get("name", "")).strip(),
        "response": str(item.get("response", "")).strip(),
        "send_as_embed": bool(item.get("send_as_embed", True)),
        "target_channel_id": str(item.get("target_channel_id", "") or "").strip(),
        "allowed_roles": [str(x) for x in (item.get("allowed_roles", []) if isinstance(item.get("allowed_roles"), list) else []) if str(x).strip()],
    }


def _normalize_if_rule(raw):
    item = raw if isinstance(raw, dict) else {}
    event = str(item.get("event", "role_add"))
    if event not in ("role_add", "role_remove"):
        event = "role_add"
    return {
        "event": event,
        "role": str(item.get("role", "")).strip(),
        "action": "send_message",
        "channel": str(item.get("channel", "")).strip(),
        "message": str(item.get("message", "")).strip(),
        "send_as_embed": bool(item.get("send_as_embed", False)),
        "allowed_roles": [str(x) for x in (item.get("allowed_roles", []) if isinstance(item.get("allowed_roles"), list) else []) if str(x).strip()],
    }


def _normalize_reaction_panel(raw, idx=0):
    item = raw if isinstance(raw, dict) else {}
    base_items = item.get("items", []) if isinstance(item.get("items"), list) else []
    cleaned_items = []
    for sub in base_items:
        if not isinstance(sub, dict):
            continue
        emoji = str(sub.get("emoji", "")).strip()
        role_id = str(sub.get("role_id", "")).strip()
        if emoji and role_id:
            cleaned_items.append({"emoji": emoji, "role_id": role_id})
    return {
        "name": str(item.get("name", f"Reaktionsrollen Panel {idx + 1}")).strip() or f"Reaktionsrollen Panel {idx + 1}",
        "enabled": bool(item.get("enabled", False)),
        "channel_id": str(item.get("channel_id", "")).strip(),
        "title": str(item.get("title", "Wähle deine Rollen")).strip() or "Wähle deine Rollen",
        "description": str(item.get("description", "Reagiere mit Emojis um Rollen zu bekommen.")).strip() or "Reagiere mit Emojis um Rollen zu bekommen.",
        "color": str(item.get("color", "#8a2be2")).strip() or "#8a2be2",
        "send_as_embed": bool(item.get("send_as_embed", True)),
        "items": cleaned_items,
        "allowed_roles": [str(x) for x in (item.get("allowed_roles", []) if isinstance(item.get("allowed_roles"), list) else []) if str(x).strip()],
    }


# ── Mapping-Helfer ───────────────────────────────────────────────

def normalize_named_mapping(raw):
    """Normalisiert Discord-Daten auf Name->ID Mapping (dict), auch wenn Listen gespeichert wurden."""
    if isinstance(raw, dict):
        return {str(k): str(v) for k, v in raw.items()}
    if isinstance(raw, list):
        result = {}
        for item in raw:
            if isinstance(item, dict):
                name = item.get("name") or item.get("label") or item.get("title")
                value = item.get("id") or item.get("value")
                if name is not None and value is not None:
                    result[str(name)] = str(value)
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                result[str(item[0])] = str(item[1])
            elif isinstance(item, (str, int)):
                value = str(item)
                if value:
                    result[f"ID {value}"] = value
        return result
    return {}


def add_ids_from_settings(mapping, settings, keys, label_prefix):
    """Fuegt bekannte IDs aus settings hinzu, damit Dropdowns auch ohne discord_data nutzbar sind."""
    enriched = dict(mapping)
    existing_values = set(str(v) for v in enriched.values())
    for key in keys:
        value = settings.get(key)
        if value is None:
            continue
        value_str = str(value).strip()
        if not value_str:
            continue
        if value_str not in existing_values:
            enriched[f"{label_prefix}: {key} ({value_str})"] = value_str
            existing_values.add(value_str)
    return enriched


def extract_ticket_category_names(raw_categories, categories_mapping):
    """Extrahiert Category-Namen fuer Multiselect (kompatibel mit alter und neuer Struktur)."""
    if not isinstance(raw_categories, list):
        return []
    reverse_map = {str(v): k for k, v in categories_mapping.items()}
    names = []
    for item in raw_categories:
        if isinstance(item, str):
            if item in categories_mapping:
                names.append(item)
            elif item in reverse_map:
                names.append(reverse_map[item])
        elif isinstance(item, dict):
            category_id = item.get("category_channel_id")
            name = item.get("name")
            if category_id is not None and str(category_id) in reverse_map:
                names.append(reverse_map[str(category_id)])
            elif name and name in categories_mapping:
                names.append(name)
    return list(dict.fromkeys(names))


def add_ticket_categories_from_settings(categories_mapping, settings):
    """Ergaenzt Kategorien aus tickets_categories in die Auswahl (falls keine discord_data Kategorien vorliegen)."""
    enriched = dict(categories_mapping)
    existing_values = set(str(v) for v in enriched.values())
    raw_categories = settings.get("tickets_categories", [])
    if not isinstance(raw_categories, list):
        return enriched

    for item in raw_categories:
        if isinstance(item, dict):
            category_id = item.get("category_channel_id")
            name = item.get("name") or "Kategorie"
            if category_id is None:
                continue
            category_id_str = str(category_id)
            if category_id_str not in existing_values:
                enriched[f"{name} ({category_id_str})"] = category_id_str
                existing_values.add(category_id_str)
        elif isinstance(item, str):
            if item not in enriched:
                enriched[item] = item
    return enriched


# ── ID-Parsing / Lookup ─────────────────────────────────────────

def index_for_value(mapping, current_value):
    if not mapping:
        return 0
    values = list(mapping.values())
    for i, val in enumerate(values):
        if str(val) == str(current_value):
            return i
    return 0


def parse_id_list(raw_value):
    """Parst komma-separierte IDs in eindeutige String-Liste."""
    if not raw_value:
        return []
    ids = []
    seen = set()
    for part in str(raw_value).split(","):
        value = part.strip()
        if not value or value in seen:
            continue
        ids.append(value)
        seen.add(value)
    return ids


def names_for_ids(mapping, id_list):
    """Mappt IDs auf bekannte Namen fuer Default-Werte in Multiselects."""
    reverse_map = {str(v): k for k, v in mapping.items()}
    return [reverse_map[str(item)] for item in (id_list or []) if str(item) in reverse_map]


# ── Guild-Daten-Extraktion ──────────────────────────────────────

def _guild_stats_for_selected(discord_data, server_entry):
    guild_id = str((server_entry or {}).get("guild_id") or "").strip()
    raw_guilds = discord_data.get("guilds", []) if isinstance(discord_data, dict) else []
    if not isinstance(raw_guilds, list):
        return {"member_count": 0, "online_count": 0}

    if guild_id:
        for guild in raw_guilds:
            if isinstance(guild, dict) and str(guild.get("id") or guild.get("guild_id") or "").strip() == guild_id:
                return {
                    "member_count": int(guild.get("member_count") or 0),
                    "online_count": int(guild.get("online_count") or 0),
                }

    label = str((server_entry or {}).get("label") or "").strip().lower()
    if label:
        for guild in raw_guilds:
            if isinstance(guild, dict) and str(guild.get("name") or guild.get("guild_name") or "").strip().lower() == label:
                return {
                    "member_count": int(guild.get("member_count") or 0),
                    "online_count": int(guild.get("online_count") or 0),
                }
    return {"member_count": 0, "online_count": 0}


def _guild_members_for_selected(discord_data, server_entry):
    guild_id = str((server_entry or {}).get("guild_id") or "").strip()
    raw_guilds = discord_data.get("guilds", []) if isinstance(discord_data, dict) else []
    if not isinstance(raw_guilds, list):
        return []

    def _extract_members(guild):
        members = guild.get("members", []) if isinstance(guild, dict) else []
        return members if isinstance(members, list) else []

    if guild_id:
        for guild in raw_guilds:
            if isinstance(guild, dict) and str(guild.get("id") or guild.get("guild_id") or "").strip() == guild_id:
                return _extract_members(guild)

    label = str((server_entry or {}).get("label") or "").strip().lower()
    if label:
        for guild in raw_guilds:
            if isinstance(guild, dict) and str(guild.get("name") or guild.get("guild_name") or "").strip().lower() == label:
                return _extract_members(guild)
    return []
