# -*- coding: utf-8 -*-
import streamlit as st
import json
import os
import requests
import discord
from copy import deepcopy
from urllib.parse import urlencode
from config import SETTINGS_FILE, DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, DASHBOARD_REDIRECT_URI

# --- KONFIGURATION ---
DISCORD_DATA_FILE = "discord_data.json"
TICKETS_STATE_FILE = "tickets_state.json"
ADMIN_ID = "202768068617699328" # Deine Discord ID

# Discord OAuth2 URLs
DISCORD_AUTH_URL = "https://discord.com/api/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_USER_URL = "https://discord.com/api/users/@me"

# --- STYLING (angepasst an Logo) ---
st.set_page_config(
    page_title="GTA RP Bot Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
    <style>
    :root {
        --as-bg-0: #0b0f1c;
        --as-bg-1: #12192b;
        --as-panel: #161f33;
        --as-panel-soft: #1b2540;
        --as-text: #f5f8ff;
        --as-muted: #a8b3cf;
        --as-accent: #5f7cff;
        --as-accent-2: #7a4dff;
        --as-ok: #3bd39a;
    }
    .stApp {
        background: radial-gradient(1200px 500px at 85% -20%, rgba(95,124,255,0.35), transparent),
                    radial-gradient(900px 350px at 10% -10%, rgba(122,77,255,0.25), transparent),
                    linear-gradient(180deg, var(--as-bg-1) 0%, var(--as-bg-0) 80%);
        color: var(--as-text);
    }
    [data-testid="stHeader"] {
        background: transparent;
        border-bottom: 0;
    }
    [data-testid="stToolbar"] {
        display: none;
    }
    /* Keep the left navigation permanently visible and non-collapsible. */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #10192d 0%, #0e1628 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
        min-width: 17rem !important;
        max-width: 17rem !important;
    }
    [data-testid="stSidebar"][aria-expanded="false"] {
        margin-left: 0 !important;
        transform: none !important;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div {
        margin-left: 0 !important;
    }
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0;
    }
    [data-testid="stSidebar"] .stRadio label {
        border: 0 !important;
        background: transparent !important;
        border-radius: 0;
        padding: 0.46rem 0.2rem;
        margin: 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        transition: background-color 140ms ease, transform 140ms ease, box-shadow 140ms ease;
    }
    [data-testid="stSidebar"] .stRadio label p {
        font-size: 1.03rem;
        font-weight: 620;
        letter-spacing: 0.01em;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.03) !important;
        transform: translateX(2px);
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.06);
    }
    [data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background: rgba(95,124,255,0.12) !important;
        border-left: 3px solid rgba(95,124,255,0.95);
        padding-left: calc(0.2rem - 3px);
        box-shadow: inset 0 0 0 1px rgba(122,77,255,0.28), 0 0 14px rgba(95,124,255,0.20);
    }
    [data-testid="stSidebar"] .stRadio label:has(input:checked) p {
        color: #f3f6ff !important;
        text-shadow: 0 0 10px rgba(122,77,255,0.24);
    }
    [data-testid="stSidebar"] [role="radiogroup"] {
        border-top: 1px solid rgba(255,255,255,0.1);
    }
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        justify-content: flex-start;
        text-align: left;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.12);
        background: rgba(255,255,255,0.02);
        font-weight: 500;
        font-size: 1.05rem;
        padding: 0.5rem 0.7rem;
        min-height: 2.25rem;
        transition: transform 120ms ease, box-shadow 120ms ease, background-color 120ms ease;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        transform: translateX(2px);
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.08);
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"],
    [data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] {
        background: rgba(95,124,255,0.22) !important;
        border-color: rgba(95,124,255,0.55) !important;
        box-shadow: inset 2px 0 0 rgba(95,124,255,0.95), 0 0 12px rgba(95,124,255,0.18);
    }
    [data-testid="stSidebar"] .stSelectbox label {
        font-size: 0.86rem !important;
        color: var(--as-muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .sidebar-section-title {
        color: #9fb0d7;
        font-size: 0.73rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 700;
        margin: 0.65rem 0 0.35rem 0;
    }
    .sidebar-section-gap {
        height: 0.35rem;
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: var(--as-text);
    }
    .block-container {
        padding-top: 1rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, var(--as-accent-2), var(--as-accent));
        color: #ffffff;
        border-radius: 10px;
        border: 0;
        padding: 0.48rem 0.95rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }
    .stButton > button:hover {
        filter: brightness(1.08);
        transform: translateY(-1px);
    }
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div,
    .stNumberInput input {
        background: var(--as-panel-soft);
        color: var(--as-text);
        border-color: rgba(255,255,255,0.12);
        border-radius: 10px;
        min-height: 40px;
    }
    .stTextArea textarea {
        min-height: 110px;
    }
    .stCheckbox label,
    .stSelectbox label,
    .stTextInput label,
    .stTextArea label,
    .stNumberInput label,
    .stMultiSelect label {
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        color: #d8e2ff !important;
    }
    /* Keep Streamlit/BaseWeb dropdown popovers above custom layers and clickable. */
    div[data-baseweb="popover"],
    div[role="listbox"] {
        z-index: 3000 !important;
        pointer-events: auto !important;
    }
    .stSelectbox, .stMultiSelect {
        position: relative;
        z-index: 1;
    }
    div[data-testid="stMetricValue"] {
        color: #93a6ff;
    }
    .status-card {
        background: linear-gradient(135deg, rgba(95,124,255,0.18), rgba(122,77,255,0.16));
        border: 1px solid rgba(255,255,255,0.14);
        color: var(--as-text);
        padding: 16px;
        border-radius: 14px;
        margin-bottom: 14px;
    }
    .brand-wrap {
        border: 1px solid rgba(255,255,255,0.10);
        background: rgba(255,255,255,0.03);
        border-radius: 14px;
        padding: 12px 14px;
        margin-bottom: 12px;
    }
    .brand-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: var(--as-text);
        margin: 0;
    }
    .brand-sub {
        color: var(--as-muted);
        margin-top: 2px;
        font-size: 0.92rem;
    }
    .pill-ok {
        display: inline-block;
        background: rgba(59,211,154,0.18);
        color: #7df2c1;
        border: 1px solid rgba(59,211,154,0.28);
        border-radius: 999px;
        font-size: 0.78rem;
        padding: 0.12rem 0.55rem;
        margin-top: 0.25rem;
    }
    .section-title {
        margin-bottom: 0.1rem;
    }
    .section-sub {
        color: var(--as-muted);
        margin-top: 0;
        margin-bottom: 1rem;
    }
    .soft-divider {
        border: 0;
        border-top: 1px solid rgba(255,255,255,0.10);
        margin: 0.7rem 0 1rem 0;
    }
    .ticket-panel-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }
    .ticket-panel-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .ticket-panel-meta {
        color: var(--as-muted);
        font-size: 0.9rem;
        margin-bottom: 0.4rem;
    }
    .ticket-command-row {
        border-bottom: 1px solid rgba(255,255,255,0.08);
        padding: 0.42rem 0;
        color: #e6ecff;
    }
    .ticket-command-row:last-child {
        border-bottom: 0;
    }
    [data-testid="stExpander"] {
        border: 1px solid rgba(95,124,255,0.25);
        border-radius: 10px;
        background: rgba(255,255,255,0.02);
        margin-bottom: 0.55rem;
        overflow: hidden;
    }
    [data-testid="stExpander"] details {
        border: 0 !important;
    }
    [data-testid="stExpander"] details summary {
        background: rgba(255,255,255,0.02);
        border: 0 !important;
        box-shadow: none !important;
        outline: none !important;
        min-height: 44px;
    }
    [data-testid="stExpander"] details summary:focus,
    [data-testid="stExpander"] details summary:focus-visible {
        outline: none !important;
        box-shadow: inset 0 0 0 1px rgba(95,124,255,0.35) !important;
    }
    [data-testid="stExpander"] details[open] summary {
        border-bottom: 1px solid rgba(95,124,255,0.2) !important;
        background: rgba(95,124,255,0.08);
    }
    [data-testid="stExpander"] details > div {
        border-top: 0 !important;
        padding-top: 0.45rem;
    }
    [data-testid="stExpander"] details summary p {
        font-weight: 700;
        font-size: 0.95rem;
    }
    /* Improve readability across the dashboard with high-contrast text. */
    .stMarkdown,
    .stMarkdown p,
    .stMarkdown li,
    .stMarkdown span,
    .stCaption,
    .stAlert,
    .stRadio label,
    .stCheckbox label,
    .stSelectbox label,
    .stTextInput label,
    .stTextArea label,
    .stNumberInput label,
    h1, h2, h3, h4, h5, h6,
    p, span, label {
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

def render_brand_header():
    logo_col, txt_col = st.columns([1, 8])
    with logo_col:
        if os.path.exists("logo.jpg"):
            st.image("logo.jpg", width=72)
    with txt_col:
        st.markdown(
            '<div class="brand-wrap"><p class="brand-title">ASWARD Control Center</p><span class="pill-ok">Live</span></div>',
            unsafe_allow_html=True,
        )

def load_reaction_roles():
    if os.path.exists("reaction_roles.json"):
        with open("reaction_roles.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_reaction_roles(data):
    with open("reaction_roles.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def _safe_read_json(path, fallback):
    if not os.path.exists(path):
        return deepcopy(fallback)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return deepcopy(fallback)

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

def _normalize_server_key(value):
    key = str(value or "default").strip().lower()
    cleaned = "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in key)
    cleaned = "-".join([part for part in cleaned.split("-") if part])
    return cleaned or "default"

def _write_raw_settings(raw_settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(raw_settings, f, indent=4, ensure_ascii=False)
    _load_settings_cached.clear()

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

def request_discord_data_sync():
    """Setzt ein Trigger-Flag, das der laufende Bot verarbeitet und danach discord_data.json aktualisiert."""
    settings = load_settings()
    settings["discord_data_sync_trigger"] = True
    save_settings(settings)
    return True, "Sync angefordert. In wenigen Sekunden sind Channels/Kategorien aktualisiert."

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

def select_role_id(label, roles_mapping, current_value, key_prefix, allow_manual_input=True):
    """Returns a role ID string from dropdown options."""
    role_names = list(roles_mapping.keys())
    current_str = str(current_value).strip() if current_value is not None else ""
    selected_id = current_str or None

    if role_names:
        def_idx = index_for_value(roles_mapping, current_value)
        selected_name = st.selectbox(
            label,
            options=[""] + role_names,
            index=(def_idx + 1) if role_names else 0,
            key=f"{key_prefix}_name",
        )
        if selected_name:
            selected_id = str(roles_mapping.get(selected_name))
    else:
        message = "Keine Rollen-Daten verfuegbar. Bitte zuerst Discord-Daten synchronisieren."
        if allow_manual_input:
            message = "Keine Rollen-Daten verfuegbar. Nutze die Rollen-ID als Eingabe."
        st.info(message)

    if allow_manual_input:
        manual_id = st.text_input(
            f"{label} ID",
            value=selected_id or "",
            key=f"{key_prefix}_manual_id",
        ).strip()
        if manual_id:
            return manual_id
    return selected_id

def render_page_header(title, subtitle):
    st.markdown(f"<h2 class='section-title'>{title}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p class='section-sub'>{subtitle}</p>", unsafe_allow_html=True)

def embed_config_block(settings, key_prefix, title_default, desc_default, color_default, footer_default):
    title = st.text_input("Titel", value=settings.get(f"{key_prefix}_title", title_default), key=f"{key_prefix}_title_input")
    description = st.text_area("Beschreibung", value=settings.get(f"{key_prefix}_description", desc_default), key=f"{key_prefix}_desc_input")
    color = st.text_input("Farbe (Hex)", value=settings.get(f"{key_prefix}_color", color_default), key=f"{key_prefix}_color_input")
    footer = st.text_input("Footer", value=settings.get(f"{key_prefix}_footer", footer_default), key=f"{key_prefix}_footer_input")
    return title, description, color, footer

def select_channel_id(label, channels_mapping, current_value, key_prefix, allow_manual_input=True):
    """Returns a channel ID string from dropdown options."""
    channel_names = list(channels_mapping.keys())
    current_str = str(current_value).strip() if current_value is not None else ""
    selected_id = current_str or None

    if channel_names:
        def_idx = index_for_value(channels_mapping, current_value)
        selected_name = st.selectbox(
            label,
            options=[""] + channel_names,
            index=(def_idx + 1) if channel_names else 0,
            key=f"{key_prefix}_name",
        )
        if selected_name:
            selected_id = str(channels_mapping.get(selected_name))
    else:
        message = "Keine Kanaele verfuegbar. Bitte zuerst Discord-Daten synchronisieren."
        if allow_manual_input:
            message = "Keine Kanaele verfuegbar. Nutze unten die Channel-ID oder synchronisiere Discord-Daten."
        st.warning(message)

    if allow_manual_input:
        manual_id = st.text_input(
            f"{label} ID",
            value=selected_id or "",
            key=f"{key_prefix}_manual_id",
        ).strip()
        if manual_id:
            return manual_id
    return selected_id

def select_category_id(label, categories_mapping, current_value, key_prefix, allow_manual_input=True):
    """Returns a category ID string from dropdown options."""
    category_names = list(categories_mapping.keys())
    current_str = str(current_value).strip() if current_value is not None else ""
    selected_id = current_str or None

    if category_names:
        def_idx = index_for_value(categories_mapping, current_value)
        selected_name = st.selectbox(
            label,
            options=[""] + category_names,
            index=(def_idx + 1) if category_names else 0,
            key=f"{key_prefix}_name",
        )
        if selected_name:
            selected_id = str(categories_mapping.get(selected_name))
    else:
        message = "Keine Kategorien verfuegbar. Bitte zuerst Discord-Daten synchronisieren."
        if allow_manual_input:
            message = "Keine Kategorien verfuegbar. Nutze die Kategorie-ID als Eingabe."
        st.warning(message)

    if allow_manual_input:
        manual_id = st.text_input(
            f"{label} ID",
            value=selected_id or "",
            key=f"{key_prefix}_manual_id",
        ).strip()
        if manual_id:
            return manual_id
    return selected_id

# --- OAUTH2 HILFSFUNKTIONEN ---
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

# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "access_token" not in st.session_state:
    st.session_state.access_token = None

# --- LOGIN LOGIK ---
def login_form():
    render_page_header("Discord Login", "Melde dich mit deinem Discord Account an, um das Dashboard zu verwalten.")

    if not oauth_is_configured():
        st.error("Discord OAuth ist nicht korrekt konfiguriert (DISCORD_CLIENT_ID / DISCORD_CLIENT_SECRET).")
        st.code(
            "sudo systemctl edit gta-dashboard --full\n"
            "# Unter [Service] setzen:\n"
            "Environment=\"DISCORD_CLIENT_ID=<deine_client_id>\"\n"
            "Environment=\"DISCORD_CLIENT_SECRET=<dein_client_secret>\"\n"
            "Environment=\"DASHBOARD_REDIRECT_URI=https://asward-helper.store\"\n"
            "sudo systemctl daemon-reload\n"
            "sudo systemctl restart gta-dashboard",
            language="bash",
        )
        return
    
    auth_url = get_discord_auth_url()
    st.markdown(f'<a href="{auth_url}" target="_self">Mit Discord anmelden</a>', unsafe_allow_html=True)
    
    # Check for code in query params
    query_params = st.query_params
    code = query_params.get("code")
    if isinstance(code, list):
        code = code[0] if code else None
    if code:
        token_data = exchange_code_for_token(code)
        if "access_token" in token_data:
            st.session_state.access_token = token_data["access_token"]
            user_info = get_user_info(st.session_state.access_token)
            if "id" in user_info:
                st.session_state.user_id = user_info["id"]
                st.session_state.logged_in = True
                st.query_params.clear()  # Clear params
                st.rerun()
        else:
            st.error("Fehler beim Anmelden. Versuche es erneut.")

# --- HAUPTTEIL ---
if not st.session_state.logged_in:
    render_brand_header()
    login_form()
else:
    user_id = str(st.session_state.user_id)
    raw_settings = load_settings()
    raw_discord_data = load_discord_data()
    is_root_admin = user_id == ADMIN_ID

    all_server_entries = _build_server_entries(raw_discord_data, raw_settings)
    if is_root_admin:
        accessible_server_entries = all_server_entries
    else:
        accessible_server_entries = [
            entry for entry in all_server_entries
            if user_id in _allowed_ids_for_server(raw_settings, entry["key"])
        ]

    if not (is_root_admin or accessible_server_entries):
        render_brand_header()
        render_page_header("Zugriff verweigert", "Dieser Account hat aktuell keine Dashboard-Berechtigung.")
        st.error("Du kannst aktuell nicht auf diese Seite zugreifen")
        st.info(f"Eingeloggt als: {st.session_state.user_id}")
        if st.button("Abmelden"):
            st.session_state.logged_in = False
            st.session_state.access_token = None
            st.session_state.user_id = None
            st.rerun()
    else:
        # ADMIN DASHBOARD
        render_brand_header()
        discord_data = raw_discord_data
        st.sidebar.markdown("### ASWARD Modules")
        st.sidebar.caption("Steuere alle Bot-Systeme zentral")
        server_entries = accessible_server_entries if accessible_server_entries else all_server_entries
        display_labels = []
        display_to_key = {}
        display_to_entry = {}
        seen_labels = set()
        for entry in server_entries:
            label = entry["label"]
            key = entry["key"]
            if label in seen_labels:
                label = f"{label} [{key[:6]}]"
            seen_labels.add(label)
            display_labels.append(label)
            display_to_key[label] = key
            display_to_entry[label] = entry

        add_server_option = "Server Hinzufuegen"
        server_dropdown_options = [add_server_option] + display_labels

        if "sidebar_server_choice" not in st.session_state or st.session_state.sidebar_server_choice not in server_dropdown_options:
            st.session_state.sidebar_server_choice = display_labels[0]

        selected_dropdown_option = st.sidebar.selectbox(
            "Server auswaehlen",
            server_dropdown_options,
            index=server_dropdown_options.index(st.session_state.sidebar_server_choice),
            key="sidebar_server_choice",
        )

        if selected_dropdown_option == add_server_option:
            chosen_server_label = st.session_state.get("active_server_label", display_labels[0])
            selected_server_key = st.session_state.get("active_server_key", display_to_key.get(chosen_server_label, display_to_key[display_labels[0]]))
            selected_server_entry = display_to_entry.get(chosen_server_label, {"label": chosen_server_label, "key": selected_server_key, "guild_id": ""})

            st.sidebar.markdown("<hr class='soft-divider' />", unsafe_allow_html=True)
            st.sidebar.markdown("#### Server Hinzufuegen")
            if is_root_admin:
                new_server_name = st.sidebar.text_input("Servername", key="new_server_name")
                new_server_id = st.sidebar.text_input("Server-ID (optional)", key="new_server_id")
                invite_permissions = st.sidebar.text_input(
                    "Invite-Berechtigungen (Integer)",
                    value=str(raw_settings.get("bot_invite_permissions", "8")),
                    key="new_server_permissions",
                )
                disable_guild_select = st.sidebar.checkbox("Server im Invite fixieren", value=False, key="new_server_disable_select")
                invite_link = get_bot_invite_url(
                    guild_id=new_server_id.strip() if new_server_id.strip() else None,
                    permissions=invite_permissions,
                    disable_guild_select=disable_guild_select,
                )
                st.sidebar.markdown(f"[Bot auf Server einladen]({invite_link})")
                st.sidebar.code(invite_link)

                if st.sidebar.button("Server speichern", key="save_new_server_btn"):
                    if not new_server_name.strip():
                        st.sidebar.error("Bitte gib einen Servernamen an.")
                    else:
                        created_key = _register_dashboard_server(new_server_name.strip(), new_server_id.strip())
                        if created_key:
                            st.session_state.active_server_key = created_key
                            st.session_state.active_server_label = new_server_name.strip()
                            st.session_state.sidebar_server_choice = new_server_name.strip()
                            st.sidebar.success("Server angelegt. Du kannst ihn jetzt konfigurieren.")
                            st.rerun()
            else:
                st.sidebar.info("Nur die Owner-ID kann neue Serverprofile anlegen.")
        else:
            chosen_server_label = selected_dropdown_option
            selected_server_key = display_to_key[chosen_server_label]
            selected_server_entry = display_to_entry.get(chosen_server_label, {"label": chosen_server_label, "key": selected_server_key, "guild_id": ""})

        st.session_state.active_server_key = selected_server_key
        st.session_state.active_server_label = chosen_server_label
        st.session_state.active_server_entry = selected_server_entry

        settings = _effective_settings_for_server(raw_settings, selected_server_key)
        settings["dashboard_server_name"] = chosen_server_label

        with st.sidebar.expander("Anleitung", expanded=False):
            st.markdown("1. Waehle links oben den Server im Dropdown aus.")
            st.markdown("2. Fuer neue Server zuerst Server Hinzufuegen nutzen und Bot ueber den Link einladen.")
            st.markdown("3. Danach den Server wieder im Dropdown auswaehlen und Module konfigurieren.")
            st.markdown("4. Jede Konfiguration wird im eigenen Server-Profil gespeichert und nicht uebernommen.")
            st.markdown("5. Dashboard-Zugriffe pro Server verwaltest du in Einstellungen.")

        st.sidebar.markdown("<hr class='soft-divider' />", unsafe_allow_html=True)

        if st.sidebar.button("Discord-Daten synchronisieren"):
            ok, msg = request_discord_data_sync()
            if ok:
                st.sidebar.success(msg)
            else:
                st.sidebar.error(msg)
        channels_map = normalize_named_mapping(discord_data.get("channels", {}))
        channels_map = add_ids_from_settings(
            channels_map,
            settings,
            [
                "ticket_channel_id",
                "tickets_panel_channel_id",
                "tickets_transcript_channel_id",
                "stempeluhr_panel_channel_id",
                "announce_channel_id",
                "automod_log_channel",
                "moderation_log_channel",
                "logging_channel_id",
            ],
            "Channel",
        )
        roles_map = normalize_named_mapping(discord_data.get("roles", {}))
        categories_map = normalize_named_mapping(discord_data.get("categories", {}))
        categories_map = add_ids_from_settings(
            categories_map,
            settings,
            [
                "ticket_category_id",
                "tickets_open_category_id",
                "tickets_claimed_category_id",
                "tickets_closed_category_id",
            ],
            "Kategorie",
        )
        categories_map = add_ticket_categories_from_settings(categories_map, settings)
        
        # Navigation in Bereiche gegliedert.
        page_map = {
            "Overview": "Übersicht",
            "Tickets": "Tickets",
            "Stempeluhr": "Stempeluhr",
            "Server Tools": "Server Tools",
            "Auto Mod": "Automod",
            "If Rules": "Wenn-Funktionen",
            "Giveaway": "Giveaway",
            "Announcements": "Ankündigungen",
            "Reaction Roles": "Reaction Roles",
            "Polls": "Umfragen",
            "Moderation": "Moderation",
            "Logging": "Logging",
            "Embed Hub": "Embed Hub",
            "Settings": "Einstellungen",
        }
        nav_sections = [
            ("Grundlegende Informationen", ["Overview", "Tickets", "Stempeluhr"]),
            ("Server-Verwaltung", ["Server Tools", "Auto Mod", "Moderation", "Logging"]),
            ("Engagement", ["Announcements", "Reaction Roles", "Polls", "Giveaway", "If Rules", "Embed Hub"]),
            ("System", ["Settings"]),
        ]
        nav_icon_map = {
            "Overview": "◉",
            "Tickets": "✦",
            "Stempeluhr": "◷",
            "Server Tools": "🛠",
            "Auto Mod": "🛡",
            "If Rules": "↯",
            "Giveaway": "🎁",
            "Announcements": "📣",
            "Reaction Roles": "◎",
            "Polls": "🗳",
            "Moderation": "⚖",
            "Logging": "⎘",
            "Embed Hub": "◈",
            "Settings": "⚙",
        }

        nav_options = list(page_map.keys())
        if "active_page" not in st.session_state or st.session_state.active_page not in nav_options:
            st.session_state.active_page = nav_options[0]

        st.sidebar.markdown("### Schnellnavigation")
        for section_title, section_items in nav_sections:
            st.sidebar.markdown(f"<div class='sidebar-section-title'>{section_title}</div>", unsafe_allow_html=True)
            for nav_key in section_items:
                nav_label = f"{nav_icon_map.get(nav_key, '•')}  {nav_key}"
                is_active = st.session_state.active_page == nav_key
                if st.sidebar.button(nav_label, key=f"nav_btn_{nav_key}", use_container_width=True, type="primary" if is_active else "secondary"):
                    st.session_state.active_page = nav_key
            st.sidebar.markdown("<div class='sidebar-section-gap'></div>", unsafe_allow_html=True)

        page = page_map[st.session_state.active_page]
        st.sidebar.markdown("<hr class='soft-divider' />", unsafe_allow_html=True)

        if st.sidebar.button("Abmelden"):
            st.session_state.logged_in = False
            st.rerun()
        
        if page == "Übersicht":
            render_page_header("Bot Übersicht", "Schneller Ueberblick ueber Status und Kernmetriken.")
            guild_stats = _guild_stats_for_selected(discord_data, selected_server_entry)
            live_tickets = _live_ticket_count_for_selected(selected_server_entry)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mitglieder", str(guild_stats.get("member_count", 0)))
            with col2:
                st.metric("Online", str(guild_stats.get("online_count", 0)))
            with col3:
                st.metric("Tickets", str(live_tickets))
            
            st.markdown("### Letzte Aktivitäten")
            st.markdown('<div class="status-card">Bot erfolgreich gestartet. Alle Systeme laufen nominal.</div>', unsafe_allow_html=True)

        elif page == "Tickets":
            render_page_header("Ticketsystem", "Uebersicht und pro Panel ein strukturierter Editor.")

            if "tickets_editor_open" not in st.session_state:
                st.session_state.tickets_editor_open = False

            ticket_panels = settings.get("ticket_panels") if isinstance(settings.get("ticket_panels"), list) else []
            if not ticket_panels:
                ticket_panels = [
                    {
                        "name": settings.get("tickets_panel_name", "Neues Ticket-Panel"),
                        "enabled": settings.get("tickets_enabled", False),
                        "panel_channel_id": settings.get("tickets_panel_channel_id"),
                        "manager_roles": settings.get("tickets_manager_roles", []),
                        "panel_title": settings.get("tickets_panel_title", "🎫 Ticket-System"),
                        "panel_description": settings.get("tickets_panel_description", "Waehle eine Option, um ein Ticket zu erstellen."),
                        "panel_mode": settings.get("tickets_panel_mode", "buttons"),
                        "options": settings.get("tickets_categories", []),
                        "open_category_id": settings.get("tickets_open_category_id"),
                        "claimed_category_id": settings.get("tickets_claimed_category_id"),
                        "closed_category_id": settings.get("tickets_closed_category_id"),
                        "transcript_channel_id": settings.get("tickets_transcript_channel_id"),
                        "transcript_dm_enabled": settings.get("tickets_transcript_dm_enabled", False),
                        "delete_on_close": settings.get("tickets_delete_on_close", True),
                        "opened_message": settings.get("tickets_opened_message", "Dein Ticket wurde erstellt. Bitte gib alle zusaetzlichen Informationen an."),
                    }
                ]

            if not st.session_state.tickets_editor_open:
                top_col, toggle_col = st.columns([10, 2])
                with top_col:
                    st.markdown("### Deine Ticket-Panels")
                with toggle_col:
                    active_toggle = st.checkbox("Aktiv", value=bool(ticket_panels and ticket_panels[0].get("enabled", False)), key="tickets_active_toggle")
                    ticket_panels[0]["enabled"] = active_toggle

                stat_left, stat_right = st.columns([7, 3])
                with stat_left:
                    st.caption("Die Befehle koennen nur von Ticketmanagern in einem Ticketkanal ausgefuehrt werden.")
                with stat_right:
                    st.markdown("<div style='text-align:right;'>1 / 10</div>", unsafe_allow_html=True)

                list_col, action_col = st.columns([8, 2])
                with action_col:
                    if st.button("+ Ein Panel erstellen"):
                        st.session_state.tickets_editor_snapshot = deepcopy(ticket_panels[0])
                        st.session_state.tickets_confirm_leave = False
                        st.session_state.tickets_editor_open = True
                        st.rerun()
                    delete_from_overview = st.button("Panel loeschen", type="secondary")

                if delete_from_overview:
                    settings["ticket_panels"] = []
                    settings["tickets_enabled"] = False
                    settings["ticket_channel_id"] = ""
                    settings["tickets_panel_channel_id"] = ""
                    settings["tickets_panel_mode"] = "buttons"
                    settings["tickets_panel_name"] = "Neues Ticket-Panel"
                    settings["tickets_panel_title"] = "🎫 Ticket-System"
                    settings["tickets_panel_description"] = "Waehle eine Option, um ein Ticket zu erstellen."
                    settings["tickets_categories"] = []
                    settings["tickets_manager_roles"] = []
                    settings["tickets_open_category_id"] = ""
                    settings["tickets_claimed_category_id"] = ""
                    settings["tickets_closed_category_id"] = ""
                    settings["tickets_transcript_channel_id"] = ""
                    settings["tickets_transcript_dm_enabled"] = False
                    settings["tickets_delete_on_close"] = True
                    settings["tickets_opened_message"] = "Dein Ticket wurde erstellt. Bitte gib alle zusaetzlichen Informationen an."
                    settings["tickets_publish_trigger"] = False
                    save_settings(settings)
                    st.success("Ticket-Panel wurde geloescht.")
                    st.rerun()

                with list_col:
                    panel = ticket_panels[0]
                    channel_id_preview = panel.get("panel_channel_id") or "-"
                    status_text = "Veroeffentlicht" if panel.get("enabled", False) else "Entwurf"
                    st.markdown(
                        f"<div class='ticket-panel-card'><div class='ticket-panel-head'><span>{panel.get('name', 'Neues Ticket-Panel')}</span>"
                        f"<span class='pill-ok'>{status_text}</span></div><div class='ticket-panel-meta'>Kanal-ID: {channel_id_preview}</div>"
                        f"<div class='ticket-panel-meta'>Modus: {panel.get('panel_mode', 'buttons')}</div></div>",
                        unsafe_allow_html=True,
                    )

                st.subheader("Befehle")
                st.markdown("<div class='ticket-command-row'>/ticket-claim - Beanspruche ein Ticket</div>", unsafe_allow_html=True)
                st.markdown("<div class='ticket-command-row'>/ticket-close - Schliesse ein Ticket</div>", unsafe_allow_html=True)
                st.markdown("<div class='ticket-command-row'>/ticket-delete - optional ueber Kanal-Loeschung bei Close</div>", unsafe_allow_html=True)

                settings["ticket_panels"] = ticket_panels
                settings["tickets_enabled"] = ticket_panels[0].get("enabled", False)
                save_settings(settings)

            else:
                panel = ticket_panels[0]
                if "tickets_editor_snapshot" not in st.session_state:
                    st.session_state.tickets_editor_snapshot = deepcopy(panel)
                if "tickets_confirm_leave" not in st.session_state:
                    st.session_state.tickets_confirm_leave = False

                back_col, title_col, action_col = st.columns([1, 7, 4])
                with back_col:
                    back_btn = st.button("<")
                with title_col:
                    panel_name = st.text_input("Panelname", value=panel.get("name", "Neues Ticket-Panel"))
                with action_col:
                    discard_btn = st.button("Verwerfen")
                    save_btn = st.button("Speichern")
                    publish_btn = st.button("Veroeffentlichen")

                st.session_state.tickets_confirm_delete = st.checkbox(
                    "Panel wirklich loeschen",
                    value=st.session_state.get("tickets_confirm_delete", False),
                    key="tickets_confirm_delete_checkbox",
                )
                delete_btn = st.button("Panel jetzt loeschen", type="secondary")

                with st.expander("Allgemein", expanded=True):
                    panel_channel_id = select_channel_id(
                        "Kanal veroeffentlichen",
                        channels_map,
                        panel.get("panel_channel_id"),
                        "tickets_panel_editor_channel",
                        allow_manual_input=False,
                    )
                    manager_defaults = names_for_ids(roles_map, panel.get("manager_roles", []))
                    manager_role_names = st.multiselect(
                        "Ticket Manager-Rollen",
                        options=list(roles_map.keys()),
                        default=manager_defaults,
                    )

                with st.expander("Panel", expanded=True):
                    panel_title = st.text_input("Titel des Ticket-Panels", value=panel.get("panel_title", "🎫 Ticket-System"))
                    panel_description = st.text_area("Beschreibung", value=panel.get("panel_description", "Waehle eine Option, um ein Ticket zu erstellen."))

                with st.expander("Ticketarten", expanded=True):
                    panel_mode = st.radio(
                        "Ansicht",
                        ["buttons", "dropdown"],
                        index=0 if panel.get("panel_mode", "buttons") == "buttons" else 1,
                        horizontal=True,
                    )
                    existing_options = panel.get("options", []) if isinstance(panel.get("options", []), list) else []
                    option_count_default = len(existing_options) if existing_options else 1
                    option_count = int(st.number_input("Anzahl Buttons/Optionen", min_value=1, max_value=5, value=max(1, min(5, option_count_default))))
                    built_options = []
                    for idx in range(option_count):
                        base = existing_options[idx] if idx < len(existing_options) and isinstance(existing_options[idx], dict) else {}
                        st.markdown(f"**Option {idx + 1}**")
                        opt_emoji = st.text_input("Emoji", value=str(base.get("emoji", "📩")), key=f"ticket_editor_emoji_{idx}")
                        opt_name = st.text_input("Buttonname", value=str(base.get("name", f"Ticket oeffnen {idx + 1}")), key=f"ticket_editor_name_{idx}")
                        opt_desc = st.text_input("Beschreibung", value=str(base.get("description", "Unser Team kann dir helfen!")), key=f"ticket_editor_desc_{idx}")
                        opt_cat_open = select_category_id("Kategorie fuer erstellte Tickets", categories_map, base.get("category_channel_id"), f"ticket_editor_open_cat_{idx}", allow_manual_input=False)
                        opt_cat_claimed = select_category_id("Kategorie fuer beanspruchte Tickets", categories_map, panel.get("claimed_category_id"), f"ticket_editor_claim_cat_{idx}", allow_manual_input=False)
                        opt_cat_closed = select_category_id("Kategorie fuer geschlossene Tickets", categories_map, panel.get("closed_category_id"), f"ticket_editor_close_cat_{idx}", allow_manual_input=False)
                        built_options.append(
                            {
                                "emoji": opt_emoji,
                                "name": opt_name,
                                "description": opt_desc,
                                "category_channel_id": int(opt_cat_open) if (opt_cat_open and str(opt_cat_open).isdigit()) else opt_cat_open,
                                "auto_role_id": None,
                            }
                        )

                with st.expander("Nachricht zur Ticketeroeffnung", expanded=True):
                    opened_message = st.text_area(
                        "Nachrichtstext",
                        value=panel.get("opened_message", "Dein Ticket wurde erstellt. Bitte gib alle zusaetzlichen Informationen an."),
                    )

                with st.expander("Ticket-Transkripte", expanded=True):
                    transcript_channel_id = select_channel_id(
                        "Transkript-Kanal",
                        channels_map,
                        panel.get("transcript_channel_id"),
                        "tickets_editor_transcript_channel",
                        allow_manual_input=False,
                    )
                    transcript_dm_enabled = st.checkbox(
                        "Sende den Link zum Transcript privat an das Mitglied",
                        value=panel.get("transcript_dm_enabled", False),
                    )

                # Values from visual selectors
                open_category_id = int(opt_cat_open) if (opt_cat_open and str(opt_cat_open).isdigit()) else opt_cat_open
                claimed_category_id = int(opt_cat_claimed) if (opt_cat_claimed and str(opt_cat_claimed).isdigit()) else opt_cat_claimed
                closed_category_id = int(opt_cat_closed) if (opt_cat_closed and str(opt_cat_closed).isdigit()) else opt_cat_closed
                manager_role_ids = [str(roles_map[name]) for name in manager_role_names]

                draft_panel = {
                    "name": panel_name,
                    "enabled": bool(panel.get("enabled", False)),
                    "panel_channel_id": panel_channel_id,
                    "manager_roles": manager_role_ids,
                    "panel_title": panel_title,
                    "panel_description": panel_description,
                    "panel_mode": panel_mode,
                    "options": built_options,
                    "open_category_id": open_category_id,
                    "claimed_category_id": claimed_category_id,
                    "closed_category_id": closed_category_id,
                    "transcript_channel_id": transcript_channel_id,
                    "transcript_dm_enabled": transcript_dm_enabled,
                    "delete_on_close": True,
                    "opened_message": opened_message,
                }
                has_unsaved_changes = draft_panel != st.session_state.tickets_editor_snapshot
                if has_unsaved_changes:
                    st.warning("Es gibt ungespeicherte Aenderungen.")
                    st.session_state.tickets_confirm_leave = st.checkbox(
                        "Ungespeicherte Aenderungen beim Verlassen verwerfen",
                        value=st.session_state.tickets_confirm_leave,
                        key="tickets_confirm_leave_checkbox",
                    )
                else:
                    st.session_state.tickets_confirm_leave = False

                if back_btn or discard_btn:
                    if has_unsaved_changes and not st.session_state.tickets_confirm_leave:
                        st.error("Bitte bestaetige zuerst das Verwerfen ungespeicherter Aenderungen.")
                        st.stop()
                    st.session_state.pop("tickets_editor_snapshot", None)
                    st.session_state.tickets_confirm_leave = False
                    st.session_state.tickets_editor_open = False
                    st.rerun()

                if delete_btn:
                    if not st.session_state.tickets_confirm_delete:
                        st.error("Bitte bestaetige zuerst 'Panel wirklich loeschen'.")
                        st.stop()
                    settings["ticket_panels"] = []
                    settings["tickets_enabled"] = False
                    settings["ticket_channel_id"] = ""
                    settings["tickets_panel_channel_id"] = ""
                    settings["tickets_panel_mode"] = "buttons"
                    settings["tickets_panel_name"] = "Neues Ticket-Panel"
                    settings["tickets_panel_title"] = "🎫 Ticket-System"
                    settings["tickets_panel_description"] = "Waehle eine Option, um ein Ticket zu erstellen."
                    settings["tickets_categories"] = []
                    settings["tickets_manager_roles"] = []
                    settings["tickets_open_category_id"] = ""
                    settings["tickets_claimed_category_id"] = ""
                    settings["tickets_closed_category_id"] = ""
                    settings["tickets_transcript_channel_id"] = ""
                    settings["tickets_transcript_dm_enabled"] = False
                    settings["tickets_delete_on_close"] = True
                    settings["tickets_opened_message"] = "Dein Ticket wurde erstellt. Bitte gib alle zusaetzlichen Informationen an."
                    settings["tickets_publish_trigger"] = False
                    save_settings(settings)
                    st.session_state.pop("tickets_editor_snapshot", None)
                    st.session_state.tickets_confirm_leave = False
                    st.session_state.tickets_confirm_delete = False
                    st.session_state.tickets_editor_open = False
                    st.success("Ticket-Panel wurde geloescht.")
                    st.rerun()

                if save_btn or publish_btn:
                    panel.update(draft_panel)
                    ticket_panels[0] = panel
                    settings["ticket_panels"] = ticket_panels

                    # Keep backend compatibility for current ticket cog.
                    settings["tickets_enabled"] = panel.get("enabled", False)
                    settings["ticket_channel_id"] = panel_channel_id
                    settings["tickets_panel_channel_id"] = panel_channel_id
                    settings["tickets_panel_mode"] = panel_mode
                    settings["tickets_panel_name"] = panel_name
                    settings["tickets_panel_title"] = panel_title
                    settings["tickets_panel_description"] = panel_description
                    settings["tickets_categories"] = built_options
                    settings["tickets_manager_roles"] = manager_role_ids
                    settings["tickets_open_category_id"] = open_category_id
                    settings["tickets_claimed_category_id"] = claimed_category_id
                    settings["tickets_closed_category_id"] = closed_category_id
                    settings["tickets_transcript_channel_id"] = transcript_channel_id
                    settings["tickets_transcript_dm_enabled"] = transcript_dm_enabled
                    settings["tickets_delete_on_close"] = True
                    settings["tickets_opened_message"] = opened_message

                    if publish_btn:
                        settings["tickets_enabled"] = True
                        settings["tickets_publish_trigger"] = True
                        panel["enabled"] = True

                    save_settings(settings)
                    st.session_state.tickets_editor_snapshot = deepcopy(panel)
                    st.session_state.tickets_confirm_leave = False
                    st.success("Ticket-Panel gespeichert." if save_btn else "Ticket-Panel gespeichert und wird veroeffentlicht.")

        elif page == "Stempeluhr":
            render_page_header("Stempeluhr System", "Berechtigungen und Panel-Channel für die Zeit-Erfassung.")
            stempeluhr_enabled = st.checkbox("Stempeluhr aktivieren", value=settings.get("stempeluhr_enabled", False))
            
            role_names = list(roles_map.keys())
            
            st.subheader("Berechtigungen")
            
            # Multi-Select für Rollen
            default_ein_names = names_for_ids(roles_map, settings.get("stempel_ein_roles", []))
            default_aus_names = names_for_ids(roles_map, settings.get("stempel_aus_roles", []))
            selected_ein_roles = st.multiselect("Wer darf /stempel_ein nutzen?", options=role_names, default=default_ein_names)
            selected_aus_roles = st.multiselect("Wer darf /stempel_aus nutzen?", options=role_names, default=default_aus_names)

            manual_ein_ids = parse_id_list(
                st.text_input(
                    "Rollen-IDs fuer /stempel_ein (Fallback, komma-separiert)",
                    value=", ".join([str(x) for x in settings.get("stempel_ein_roles", [])]),
                    key="stempel_ein_roles_manual",
                )
            )
            manual_aus_ids = parse_id_list(
                st.text_input(
                    "Rollen-IDs fuer /stempel_aus (Fallback, komma-separiert)",
                    value=", ".join([str(x) for x in settings.get("stempel_aus_roles", [])]),
                    key="stempel_aus_roles_manual",
                )
            )

            current_panel_channel = settings.get("stempeluhr_panel_channel_id", "")
            panel_channel_id = select_channel_id("Stempeluhr Panel Channel", channels_map, current_panel_channel, "stempeluhr_panel")
            
            if st.button("Stempel-Berechtigungen speichern"):
                settings["stempeluhr_enabled"] = stempeluhr_enabled
                resolved_ein = [str(roles_map[r]) for r in selected_ein_roles]
                resolved_aus = [str(roles_map[r]) for r in selected_aus_roles]
                final_ein = manual_ein_ids or resolved_ein
                final_aus = manual_aus_ids or resolved_aus
                settings["stempel_ein_roles"] = final_ein
                settings["stempel_aus_roles"] = final_aus
                # Backward/forward compatibility with cog keys.
                settings["stempeluhr_allowed_roles"] = list(dict.fromkeys(final_ein + final_aus))
                settings["stempeluhr_admin_roles"] = list(dict.fromkeys(final_aus))
                settings["stempeluhr_panel_channel_id"] = panel_channel_id
                save_settings(settings)
                st.success("Stempel-Berechtigungen wurden aktualisiert!")

            if st.button("Stempeluhr Panel veröffentlichen"):
                settings["stempeluhr_enabled"] = stempeluhr_enabled
                settings["stempeluhr_panel_channel_id"] = panel_channel_id or settings.get("stempeluhr_panel_channel_id")
                settings["stempeluhr_publish_trigger"] = True
                save_settings(settings)
                st.success("Stempeluhr Panel wird veröffentlicht.")

        elif page == "Automod":
            render_page_header("Automod", "Schütze den Server mit Spam-, Caps- und Wortfiltern.")
            
            automod_enabled = st.checkbox("Automod aktivieren", value=settings.get("automod_enabled", False))
            banned_words = st.text_area("Verbotene Wörter (kommasepariert)", value=", ".join(settings.get("automod_banned_words", [])))
            spam_threshold = st.number_input("Spam-Schwellenwert", value=settings.get("automod_spam_threshold", 5), min_value=1)
            spam_timeframe = st.number_input("Spam-Zeitfenster (Sekunden)", value=settings.get("automod_spam_timeframe", 10), min_value=1)
            caps_threshold = st.slider("Caps-Schwellenwert", 0.0, 1.0, value=settings.get("automod_caps_threshold", 0.7))
            action = st.selectbox("Aktion bei Verstoß", ["delete", "warn", "mute", "ban"], index=["delete", "warn", "mute", "ban"].index(settings.get("automod_action", "delete")))
            
            caps_enabled = st.checkbox("Caps-Lock Filter aktivieren", value=settings.get("automod_caps_enabled", True))
            block_links = st.checkbox("Links blockieren", value=settings.get("automod_block_links", False))
            block_invites = st.checkbox("Discord-Einladungslinks blockieren", value=settings.get("automod_block_invites", False))

            log_channel_id = select_channel_id("Log-Channel", channels_map, settings.get("automod_log_channel"), "automod_log")
            
            mute_role_id = select_role_id("Mute-Rolle", roles_map, settings.get("automod_mute_role"), "automod_mute_role")
            
            if st.button("Automod speichern"):
                settings["automod_enabled"] = automod_enabled
                settings["automod_banned_words"] = [w.strip() for w in banned_words.split(",") if w.strip()]
                settings["automod_spam_threshold"] = spam_threshold
                settings["automod_spam_timeframe"] = spam_timeframe
                settings["automod_caps_enabled"] = caps_enabled
                settings["automod_caps_threshold"] = caps_threshold
                settings["automod_block_links"] = block_links
                settings["automod_block_invites"] = block_invites
                settings["automod_action"] = action
                settings["automod_log_channel"] = log_channel_id
                settings["automod_mute_role"] = mute_role_id
                save_settings(settings)
                st.success("Automod-Einstellungen gespeichert!")

        elif page == "Server Tools":
            render_page_header("Server Tools", "Moderationstools fuer den RP-Alltag: Slowmode, Lock/Unlock, Timeout.")
            tools_enabled = st.checkbox("Server Tools aktivieren", value=settings.get("server_tools_enabled", True))
            st.info("Neue Befehle: /slowmode, /lock, /unlock, /timeout, /untimeout")
            if st.button("Server Tools speichern"):
                settings["server_tools_enabled"] = tools_enabled
                save_settings(settings)
                st.success("Server Tools gespeichert.")

        elif page == "Wenn-Funktionen":
            render_page_header("Wenn-Funktionen", "Eventbasierte Regeln fuer Rollen-Events und Auto-Aktionen.")
            
            custom_rules = settings.get("custom_rules", [])
            
            st.subheader("Neue Regel hinzufügen")
            event = st.selectbox("Event", ["role_add", "role_remove"])
            custom_enabled = st.checkbox("Wenn-Funktionen aktivieren", value=settings.get("custom_rules_enabled", False))
            role_names = list(roles_map.keys())
            selected_role = st.selectbox("Rolle", options=role_names) if role_names else ""
            if not role_names:
                st.info("Keine Rollen geladen. Trage die Rollen-ID manuell ein.")
            manual_rule_role_id = st.text_input("Rollen-ID (Fallback)", key="ifrules_role_manual")
            action = st.selectbox("Aktion", ["send_message"])
            selected_channel_id = select_channel_id("Channel", channels_map, None, "ifrules_channel")
            message = st.text_area("Nachricht", placeholder="Verwende {user} und {server}")
            
            if st.button("Regel hinzufügen"):
                settings["custom_rules_enabled"] = custom_enabled
                role_id_value = manual_rule_role_id.strip() or (str(roles_map[selected_role]) if selected_role else "")
                if not role_id_value:
                    st.error("Bitte waehle eine Rolle oder trage eine Rollen-ID ein.")
                    st.stop()
                if not selected_channel_id:
                    st.error("Bitte waehle einen Channel oder trage eine Channel-ID ein.")
                    st.stop()
                new_rule = {
                    "event": event,
                    "role": role_id_value,
                    "action": action,
                    "channel": str(selected_channel_id),
                    "message": message
                }
                custom_rules.append(new_rule)
                settings["custom_rules"] = custom_rules
                save_settings(settings)
                st.success("Regel hinzugefügt!")
                st.rerun()
            
            st.subheader("Vorhandene Regeln")
            for i, rule in enumerate(custom_rules):
                st.write(f"**Regel {i+1}:** {rule['event']} für Rolle {rule['role']} -> {rule['action']} in Channel {rule['channel']}")
                if st.button(f"Regel {i+1} löschen", key=f"delete_{i}"):
                    custom_rules.pop(i)
                    settings["custom_rules"] = custom_rules
                    save_settings(settings)
                    st.success("Regel gelöscht!")
                    st.rerun()

        elif page == "Giveaway":
            render_page_header("Giveaway", "Passe das Giveaway-Embed im gewohnten Control-Center Stil an.")
            giveaway_enabled = st.checkbox("Giveaway aktivieren", value=settings.get("giveaway_enabled", False))
            
            giveaway_embed_title = st.text_input("Embed Titel", value=settings.get("giveaway_embed_title", "🎉 Giveaway!"))
            giveaway_embed_description = st.text_area("Embed Beschreibung", value=settings.get("giveaway_embed_description", "Gegenstand: {item}\nEndet in: {time}"))
            giveaway_embed_color = st.text_input("Embed Farbe (Hex)", value=settings.get("giveaway_embed_color", "#ff4500"))
            giveaway_embed_footer = st.text_input("Embed Footer", value=settings.get("giveaway_embed_footer", "Klicke auf Teilnehmen!"))
            
            if st.button("Giveaway Embed speichern"):
                settings["giveaway_enabled"] = giveaway_enabled
                settings["giveaway_embed_title"] = giveaway_embed_title
                settings["giveaway_embed_description"] = giveaway_embed_description
                settings["giveaway_embed_color"] = giveaway_embed_color
                settings["giveaway_embed_footer"] = giveaway_embed_footer
                save_settings(settings)
                st.success("Giveaway Embed gespeichert!")

        elif page == "Ankündigungen":
            render_page_header("Ankuendigungen", "Steuere Channel, Embed-Layout und Publishing fuer Ankuendigungen.")
            announce_enabled = st.checkbox("Ankündigungen aktivieren", value=settings.get("announce_enabled", True))
            current_announce_channel = settings.get("announce_channel_id", "")
            announce_channel_id = select_channel_id("Ankündigungs-Channel", channels_map, current_announce_channel, "announce_channel")
            
            announce_embed_enabled = st.checkbox("Als Embed senden", value=settings.get("announce_embed_enabled", False))
            if announce_embed_enabled:
                announce_embed_title = st.text_input("Embed Titel", value=settings.get("announce_embed_title", "📢 Ankündigung"))
                announce_embed_description = st.text_area("Embed Beschreibung", value=settings.get("announce_embed_description", "{text}"))
                announce_embed_color = st.text_input("Embed Farbe (Hex)", value=settings.get("announce_embed_color", "#38bdf8"))
                announce_embed_footer = st.text_input("Embed Footer", value=settings.get("announce_embed_footer", "Gesendet von {user}"))
                
                if st.button("Ankündigung Embed speichern"):
                    settings["announce_enabled"] = announce_enabled
                    settings["announce_channel_id"] = announce_channel_id or settings.get("announce_channel_id")
                    settings["announce_embed_title"] = announce_embed_title
                    settings["announce_embed_description"] = announce_embed_description
                    settings["announce_embed_color"] = announce_embed_color
                    settings["announce_embed_footer"] = announce_embed_footer
                    save_settings(settings)
                    st.success("Ankündigung Embed gespeichert!")
            else:
                if st.button("Einstellung speichern"):
                    settings["announce_enabled"] = announce_enabled
                    settings["announce_channel_id"] = announce_channel_id or settings.get("announce_channel_id")
                    settings["announce_embed_enabled"] = announce_embed_enabled
                    save_settings(settings)
                    st.success("Gespeichert!")

            if st.button("Ankündigung veröffentlichen"):
                settings["announce_enabled"] = announce_enabled
                settings["announce_channel_id"] = announce_channel_id or settings.get("announce_channel_id")
                settings["announce_publish_trigger"] = True
                save_settings(settings)
                st.success("Ankündigung wird veröffentlicht.")

        elif page == "Reaction Roles":
            render_page_header("Reaction Roles", "Baue selbsterklaerende Rollen-Panels mit Emoji-Zuordnung.")
            reaction_roles_enabled = st.checkbox("Reaction Roles aktivieren", value=settings.get("reaction_roles_enabled", False))
            rr_data = load_reaction_roles()
            
            st.subheader("Neue Reaction Role Nachricht")
            rr_channel_id = select_channel_id("Channel", channels_map, None, "reaction_roles_channel")
            title = st.text_input("Embed Titel", "Wähle deine Rollen")
            description = st.text_area("Embed Beschreibung", "Reagiere mit Emojis um Rollen zu bekommen.")
            color = st.text_input("Embed Farbe (Hex)", "#8a2be2")
            
            st.subheader("Rollen zuweisen")
            emoji1 = st.text_input("Emoji 1", "🔴")
            role1 = select_role_id("Rolle 1", roles_map, None, "reaction_role_1")
            emoji2 = st.text_input("Emoji 2", "🔵")
            role2 = select_role_id("Rolle 2", roles_map, None, "reaction_role_2")
            # Mehr können hinzugefügt werden
            
            async def _send_reaction_role(ch_id: int, embed: discord.Embed, emoji_role_map: dict):
                # Runs in the bot event loop.
                bot = st.session_state.get("bot")
                if bot is None:
                    return
                chan = bot.get_channel(ch_id)
                if chan is None:
                    return
                msg = await chan.send(embed=embed)
                for emoji in emoji_role_map.keys():
                    await msg.add_reaction(emoji)
                rr_data[str(msg.id)] = emoji_role_map
                save_reaction_roles(rr_data)
                from database import add_reaction_role
                await add_reaction_role(str(msg.id), json.dumps(emoji_role_map))

            if st.button("Reaction Role Nachricht senden"):
                if rr_channel_id and title:
                    emoji_role_map = {}
                    if emoji1 and role1:
                        emoji_role_map[emoji1] = str(role1)
                    if emoji2 and role2:
                        emoji_role_map[emoji2] = str(role2)

                    bot = st.session_state.get("bot")
                    if bot is None:
                        st.error("Bot-Session nicht verfügbar. Nutze den Befehl im Discord oder verbinde den Bot mit dem Dashboard.")
                    else:
                        settings["reaction_roles_enabled"] = reaction_roles_enabled
                        save_settings(settings)
                        ch = int(rr_channel_id)
                        embed = discord.Embed(title=title, description=description, color=int(color.lstrip("#"), 16))
                        bot.loop.create_task(_send_reaction_role(ch, embed, emoji_role_map))
                        st.success("Reaction Role Nachricht wird gesendet!")
                else:
                    st.error("Channel und Titel erforderlich!")

        elif page == "Umfragen":
            render_page_header("Umfragen", "Definiere Titel, Farbe und Footer fuer Poll-Embeds.")
            polls_enabled = st.checkbox("Umfragen aktivieren", value=settings.get("polls_enabled", False))
            
            poll_embed_title = st.text_input("Embed Titel", value=settings.get("poll_embed_title", "📊 Umfrage"))
            poll_embed_color = st.text_input("Embed Farbe (Hex)", value=settings.get("poll_embed_color", "#8a2be2"))
            poll_embed_footer = st.text_input("Embed Footer", value=settings.get("poll_embed_footer", "Stimme ab!"))
            
            if st.button("Umfrage Embed speichern"):
                settings["polls_enabled"] = polls_enabled
                settings["poll_embed_title"] = poll_embed_title
                settings["poll_embed_color"] = poll_embed_color
                settings["poll_embed_footer"] = poll_embed_footer
                save_settings(settings)
                st.success("Umfrage Embed gespeichert!")

        elif page == "Moderation":
            render_page_header("Moderation", "Sanktions-, Warn- und Log-Templates zentral verwalten.")
            
            st.subheader("Sanktionen")
            moderation_enabled = st.checkbox("Moderation aktivieren", value=settings.get("management_enabled", True))
            sanktion_role_id = select_role_id("Sanktions-Rolle", roles_map, settings.get("sanktion_role_id"), "moderation_sanktion_role")
            sanktion_embed_title = st.text_input("Sanktion Embed Titel", value=settings.get("sanktion_embed_title", "🚫 Sanktion"))
            sanktion_embed_description = st.text_area("Sanktion Embed Beschreibung", value=settings.get("sanktion_embed_description", "User: {user}\nBetrag: {betrag}\nGrund: {grund}\nDauer: {dauer} Tage"))
            sanktion_embed_color = st.text_input("Sanktion Embed Farbe (Hex)", value=settings.get("sanktion_embed_color", "#ff0000"))
            sanktion_embed_footer = st.text_input("Sanktion Embed Footer", value=settings.get("sanktion_embed_footer", "Sanktion erteilt"))
            
            st.subheader("Warnungen")
            warn_embed_title = st.text_input("Warn Embed Titel", value=settings.get("warn_embed_title", "⚠️ Warnung"))
            warn_embed_description = st.text_area("Warn Embed Beschreibung", value=settings.get("warn_embed_description", "User: {user}\nGrund: {grund}\nDauer: {dauer} Tage"))
            warn_embed_color = st.text_input("Warn Embed Farbe (Hex)", value=settings.get("warn_embed_color", "#ffa500"))
            warn_embed_footer = st.text_input("Warn Embed Footer", value=settings.get("warn_embed_footer", "Warnung erteilt"))
            
            st.subheader("Logs")
            moderation_log_channel_id = select_channel_id("Moderation Log Channel", channels_map, settings.get("moderation_log_channel"), "moderation_log")
            
            if st.button("Moderation speichern"):
                settings["management_enabled"] = moderation_enabled
                settings["sanktion_role_id"] = sanktion_role_id
                settings["sanktion_embed_title"] = sanktion_embed_title
                settings["sanktion_embed_description"] = sanktion_embed_description
                settings["sanktion_embed_color"] = sanktion_embed_color
                settings["sanktion_embed_footer"] = sanktion_embed_footer
                settings["warn_embed_title"] = warn_embed_title
                settings["warn_embed_description"] = warn_embed_description
                settings["warn_embed_color"] = warn_embed_color
                settings["warn_embed_footer"] = warn_embed_footer
                settings["moderation_log_channel"] = moderation_log_channel_id
                save_settings(settings)
                st.success("Moderation gespeichert!")

        elif page == "Logging":
            render_page_header("Logging", "Aktiviere Logging und ordne den Ziel-Channel zu.")
            logging_enabled = st.checkbox("Logging aktivieren", value=settings.get("logging_enabled", True))
            logging_channel_id = select_channel_id("Logging Channel", channels_map, settings.get("logging_channel_id"), "logging_channel")
            
            if st.button("Logging speichern"):
                settings["logging_enabled"] = logging_enabled
                settings["logging_channel_id"] = logging_channel_id
                save_settings(settings)
                st.success("Logging gespeichert!")

        elif page == "Einstellungen":
            render_page_header("Allgemeine Einstellungen", "Globale Basiswerte fuer Prefix und Kern-Module.")
            active_server_label = st.session_state.get("active_server_label", settings.get("dashboard_server_name", "ASWARD Server"))
            active_server_key = st.session_state.get("active_server_key", "default")
            st.info(f"Aktiver Server-Kontext: {active_server_label}")

            st.subheader("Basis-Einstellungen")
            automod_enabled = st.checkbox("Automod global aktivieren", value=settings.get("automod_enabled", False))
            st.subheader("Sonstige Einstellungen")
            bot_prefix = st.text_input("Bot Prefix", value=settings.get("prefix", "!"))
            
            if st.button("Speichern"):
                settings["automod_enabled"] = automod_enabled
                settings["prefix"] = bot_prefix
                save_settings(settings)
                st.success("Einstellungen gespeichert!")
                st.rerun()  # Seite neu laden, um Navigation zu aktualisieren

            st.markdown("<hr class='soft-divider' />", unsafe_allow_html=True)
            st.subheader("Dashboard-Zugriff pro Server")
            current_allowed_ids = sorted(list(_allowed_ids_for_server(raw_settings, active_server_key)))
            if is_root_admin:
                allowed_input = st.text_input(
                    "Discord User IDs mit Dashboard-Zugriff (komma-separiert)",
                    value=", ".join(current_allowed_ids),
                    key="dashboard_allowed_ids_input",
                )
                st.caption("Nur deine Owner-ID kann diese Liste bearbeiten.")
                if st.button("Dashboard-Benutzer speichern"):
                    _set_allowed_ids_for_server(active_server_key, parse_id_list(allowed_input))
                    st.success("Zugriffsrechte fuer den ausgewaehlten Server gespeichert.")
                    st.rerun()
            else:
                st.write("Freigegebene IDs:")
                st.code("\n".join(current_allowed_ids) if current_allowed_ids else "Keine weiteren Benutzer freigegeben.")
                st.info("Nur die Owner-ID kann Dashboard-Benutzer je Server hinzufuegen oder entfernen.")

        elif page == "Embed Hub":
            render_page_header("Embed Hub", "Zentrale Konfiguration fuer alle wichtigen Embed-Vorlagen.")

            with st.expander("Ankuendigungs-Embed", expanded=True):
                title, desc, color, footer = embed_config_block(
                    settings,
                    "announce_embed",
                    "📢 Ankündigung",
                    "{text}",
                    "#38bdf8",
                    "Gesendet von {user}",
                )
                settings["announce_embed_title"] = title
                settings["announce_embed_description"] = desc
                settings["announce_embed_color"] = color
                settings["announce_embed_footer"] = footer

            with st.expander("Giveaway-Embed"):
                title, desc, color, footer = embed_config_block(
                    settings,
                    "giveaway_embed",
                    "🎉 Giveaway!",
                    "Gegenstand: {item}\nEndet in: {time}",
                    "#ff4500",
                    "Klicke auf Teilnehmen!",
                )
                settings["giveaway_embed_title"] = title
                settings["giveaway_embed_description"] = desc
                settings["giveaway_embed_color"] = color
                settings["giveaway_embed_footer"] = footer

            with st.expander("Umfrage-Embed"):
                title, desc, color, footer = embed_config_block(
                    settings,
                    "poll_embed",
                    "📊 Umfrage",
                    "{question}",
                    "#8a2be2",
                    "Stimme ab!",
                )
                settings["poll_embed_title"] = title
                settings["poll_embed_description"] = desc
                settings["poll_embed_color"] = color
                settings["poll_embed_footer"] = footer

            with st.expander("Moderation: Sanktion"):
                title, desc, color, footer = embed_config_block(
                    settings,
                    "sanktion_embed",
                    "🚫 Sanktion",
                    "User: {user}\nBetrag: {betrag}\nGrund: {grund}\nDauer: {dauer} Tage",
                    "#ff0000",
                    "Sanktion erteilt",
                )
                settings["sanktion_embed_title"] = title
                settings["sanktion_embed_description"] = desc
                settings["sanktion_embed_color"] = color
                settings["sanktion_embed_footer"] = footer

            with st.expander("Moderation: Warnung"):
                title, desc, color, footer = embed_config_block(
                    settings,
                    "warn_embed",
                    "⚠️ Warnung",
                    "User: {user}\nGrund: {grund}\nDauer: {dauer} Tage",
                    "#ffa500",
                    "Warnung erteilt",
                )
                settings["warn_embed_title"] = title
                settings["warn_embed_description"] = desc
                settings["warn_embed_color"] = color
                settings["warn_embed_footer"] = footer

            if st.button("Alle Embed-Vorlagen speichern"):
                save_settings(settings)
                st.success("Embed Hub gespeichert.")
