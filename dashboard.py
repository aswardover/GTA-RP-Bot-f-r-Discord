# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import json
import os
import datetime
import requests
import discord
import html
from copy import deepcopy
from urllib.parse import urlencode
from config import SETTINGS_FILE, DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, DASHBOARD_REDIRECT_URI

# --- KONFIGURATION ---
DISCORD_DATA_FILE = "discord_data.json"
TICKETS_STATE_FILE = "tickets_state.json"
AUDIT_LOG_FILE = "dashboard_audit.json"
BOT_RUNTIME_FILE = "bot_runtime.json"
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
    .pill-err {
        display: inline-block;
        background: rgba(239,68,68,0.18);
        color: #fca5a5;
        border: 1px solid rgba(239,68,68,0.32);
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
    runtime = _safe_read_json(BOT_RUNTIME_FILE, {})
    online = bool(runtime.get("online", False)) if isinstance(runtime, dict) else False
    brand_color = "#7ddc4d" if online else "#ef4444"
    status_text = "Online" if online else "Offline"
    status_class = "pill-ok" if online else "pill-err"
    logo_col, txt_col = st.columns([1, 8])
    with logo_col:
        if os.path.exists("logo.jpg"):
            st.image("logo.jpg", width=72)
    with txt_col:
        st.markdown(
            f'<div class="brand-wrap"><p class="brand-title" style="color:{brand_color};">ASWARD Control Center</p><span class="{status_class}">{status_text}</span></div>',
            unsafe_allow_html=True,
        )

def _bot_runtime_status():
    runtime = _safe_read_json(BOT_RUNTIME_FILE, {})
    if not isinstance(runtime, dict):
        return {"online": False, "last_seen": ""}
    last_seen = str(runtime.get("last_seen") or "").strip()
    online_flag = bool(runtime.get("online", False))
    if not last_seen:
        return {"online": online_flag, "last_seen": ""}
    try:
        dt = datetime.datetime.fromisoformat(last_seen.replace("Z", "+00:00"))
        age = (datetime.datetime.now(datetime.timezone.utc) - dt).total_seconds()
        return {"online": online_flag and age <= 20, "last_seen": last_seen}
    except Exception:
        return {"online": online_flag, "last_seen": last_seen}

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

def _render_member_copy_list(members):
    if not members:
        st.info("Keine Mitgliederdaten verfügbar. Bot muss online sein und Daten exportieren.")
        return

    rows = []
    for item in members:
        if not isinstance(item, dict):
            continue
        user_id = str(item.get("id") or "").strip()
        if not user_id:
            continue
        display_name = str(item.get("display_name") or item.get("name") or user_id)
        is_online = bool(item.get("online", False))
        status_dot = "#22c55e" if is_online else "#64748b"
        safe_name = html.escape(display_name)
        safe_id = html.escape(user_id)
        rows.append(
            f'<button class="member-copy-btn" data-user-id="{safe_id}"><span class="dot" style="background:{status_dot};"></span><span class="name">{safe_name}</span><span class="uid">{safe_id}</span></button>'
        )

    if not rows:
        st.info("Keine Mitglieder gefunden.")
        return

    body = "".join(rows)
    list_height = min(520, max(160, 54 + len(rows) * 36))
    components.html(
        f"""
        <div class="member-copy-wrap">
            <div class="member-copy-head">Mitgliederliste (klicken = ID kopieren)</div>
            <div class="member-copy-list" style="max-height:{list_height}px;">{body}</div>
            <div id="copy-toast" class="copy-toast">NutzerID kopiert</div>
        </div>
        <style>
            .member-copy-wrap {{
                border: 1px solid rgba(255,255,255,0.14);
                border-radius: 12px;
                background: rgba(255,255,255,0.03);
                padding: 10px;
                color: #fff;
                font-family: Segoe UI, sans-serif;
            }}
            .member-copy-head {{
                font-size: 0.9rem;
                color: #c8d2f4;
                margin-bottom: 8px;
            }}
            .member-copy-list {{
                overflow: auto;
                display: grid;
                gap: 6px;
            }}
            .member-copy-btn {{
                width: 100%;
                border: 1px solid rgba(255,255,255,0.12);
                background: rgba(16,25,45,0.7);
                color: #fff;
                border-radius: 8px;
                padding: 8px 10px;
                display: flex;
                align-items: center;
                gap: 8px;
                cursor: pointer;
                text-align: left;
            }}
            .member-copy-btn:hover {{
                background: rgba(95,124,255,0.18);
                border-color: rgba(95,124,255,0.5);
            }}
            .member-copy-btn .dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                flex: 0 0 auto;
            }}
            .member-copy-btn .name {{
                flex: 1;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            .member-copy-btn .uid {{
                font-size: 0.78rem;
                color: #9fb0d7;
            }}
            .copy-toast {{
                margin-top: 8px;
                padding: 6px 8px;
                border-radius: 8px;
                background: rgba(34,197,94,0.15);
                color: #86efac;
                border: 1px solid rgba(34,197,94,0.3);
                display: none;
                font-size: 0.82rem;
            }}
        </style>
        <script>
            (function() {{
                const root = document.currentScript.parentElement;
                const toast = root.querySelector('#copy-toast');
                root.querySelectorAll('.member-copy-btn').forEach((btn) => {{
                    btn.addEventListener('click', async () => {{
                        const userId = btn.getAttribute('data-user-id') || '';
                        if (!userId) return;
                        try {{
                            await navigator.clipboard.writeText(userId);
                            toast.textContent = 'NutzerID kopiert';
                            toast.style.display = 'block';
                            setTimeout(() => {{ toast.style.display = 'none'; }}, 1200);
                        }} catch (e) {{
                            toast.textContent = 'Kopieren fehlgeschlagen';
                            toast.style.display = 'block';
                            setTimeout(() => {{ toast.style.display = 'none'; }}, 1500);
                        }}
                    }});
                }});
            }})();
        </script>
        """,
        height=min(620, list_height + 110),
    )

def _enable_overview_autorefresh(interval_ms=8000):
    components.html(
        f"""
        <script>
            setTimeout(function() {{
                window.parent.location.reload();
            }}, {int(interval_ms)});
        </script>
        """,
        height=0,
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

def _append_audit_entry(module, action, details=None, status="ok"):
    entries = _safe_read_json(AUDIT_LOG_FILE, [])
    if not isinstance(entries, list):
        entries = []

    actor_id = str(st.session_state.get("user_id") or "unknown")
    server_key = str(st.session_state.get("active_server_key") or "default")
    server_label = str(st.session_state.get("active_server_label") or "-")
    entry = {
        "ts": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "module": str(module),
        "action": str(action),
        "status": str(status),
        "server_key": server_key,
        "server_label": server_label,
        "actor_id": actor_id,
        "details": str(details or ""),
    }
    entries.insert(0, entry)
    entries = entries[:500]
    with open(AUDIT_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

def _read_audit_entries(server_key=None, limit=100):
    entries = _safe_read_json(AUDIT_LOG_FILE, [])
    if not isinstance(entries, list):
        return []
    if server_key:
        entries = [e for e in entries if isinstance(e, dict) and str(e.get("server_key")) == str(server_key)]
    return entries[:max(1, int(limit))]

def _push_undo_snapshot(settings, snapshot_key, payload):
    undo_root = settings.get("dashboard_undo", {}) if isinstance(settings.get("dashboard_undo"), dict) else {}
    stack = undo_root.get(snapshot_key, []) if isinstance(undo_root.get(snapshot_key), list) else []
    stack.append(deepcopy(payload))
    undo_root[snapshot_key] = stack[-5:]
    settings["dashboard_undo"] = undo_root

def _pop_undo_snapshot(settings, snapshot_key):
    undo_root = settings.get("dashboard_undo", {}) if isinstance(settings.get("dashboard_undo"), dict) else {}
    stack = undo_root.get(snapshot_key, []) if isinstance(undo_root.get(snapshot_key), list) else []
    if not stack:
        return None
    payload = stack.pop()
    undo_root[snapshot_key] = stack
    settings["dashboard_undo"] = undo_root
    return payload

def _preview_text(template_text, channel_hint="#channel"):
    text = str(template_text or "")
    return (
        text.replace("{user}", "@User")
        .replace("{server}", str(st.session_state.get("active_server_label") or "Server"))
        .replace("{channel}", channel_hint)
    )

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

PLACEHOLDER_REGISTRY = {
    "announce": ["{text}", "{user}"],
    "giveaway": ["{item}", "{time}"],
    "poll": ["{question}"],
    "sanktion": ["{user}", "{betrag}", "{grund}", "{dauer}"],
    "warn": ["{user}", "{grund}", "{dauer}"],
    "reaction_roles": [],
}

def _render_placeholder_registry(context_key):
    placeholders = PLACEHOLDER_REGISTRY.get(context_key, [])
    if not placeholders:
        st.caption("Verfügbare Platzhalter: Keine")
        return
    st.caption("Verfügbare Platzhalter: " + ", ".join(placeholders))

def _render_embed_preview(title, description, footer):
    st.caption("Live-Vorschau")
    safe_title = title or "(kein Titel)"
    safe_description = description or "(keine Beschreibung)"
    safe_footer = footer or "(kein Footer)"
    st.markdown(
        f"<div class='ticket-panel-card'><div class='ticket-panel-head'><span>{safe_title}</span><span class='pill-ok'>Embed</span></div>"
        f"<div class='ticket-panel-meta'>{safe_description}</div><div class='ticket-panel-meta'>Footer: {safe_footer}</div></div>",
        unsafe_allow_html=True,
    )

def render_embed_designer(settings, key_prefix, title_default, desc_default, color_default, footer_default, context_key):
    st.subheader("Embed-Baukasten")
    title = st.text_input("Embed Titel", value=settings.get(f"{key_prefix}_title", title_default), key=f"{key_prefix}_title_input")
    description = st.text_area("Embed Beschreibung", value=settings.get(f"{key_prefix}_description", desc_default), key=f"{key_prefix}_desc_input")
    color = st.text_input("Embed Farbe (Hex)", value=settings.get(f"{key_prefix}_color", color_default), key=f"{key_prefix}_color_input")
    footer = st.text_input("Embed Footer", value=settings.get(f"{key_prefix}_footer", footer_default), key=f"{key_prefix}_footer_input")
    _render_placeholder_registry(context_key)
    _render_embed_preview(title, _preview_text(description, "#preview"), _preview_text(footer, "#preview"))
    return title, description, color, footer

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
        runtime_status = _bot_runtime_status()
        sidebar_brand_color = "#7ddc4d" if runtime_status.get("online") else "#ef4444"
        st.sidebar.markdown(f"<h3 style='margin:0;color:{sidebar_brand_color};'>Asward-Helper</h3>", unsafe_allow_html=True)
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

        add_server_option = "Server Hinzufügen"
        server_dropdown_options = [add_server_option] + display_labels

        if "sidebar_server_choice" not in st.session_state or st.session_state.sidebar_server_choice not in server_dropdown_options:
            st.session_state.sidebar_server_choice = display_labels[0]

        selected_dropdown_option = st.sidebar.selectbox(
            "Server auswählen",
            server_dropdown_options,
            key="sidebar_server_choice",
        )

        if selected_dropdown_option == add_server_option:
            chosen_server_label = st.session_state.get("active_server_label", display_labels[0])
            selected_server_key = st.session_state.get("active_server_key", display_to_key.get(chosen_server_label, display_to_key[display_labels[0]]))
            selected_server_entry = display_to_entry.get(chosen_server_label, {"label": chosen_server_label, "key": selected_server_key, "guild_id": ""})

            st.sidebar.markdown("<hr class='soft-divider' />", unsafe_allow_html=True)
            st.sidebar.markdown("#### Server Hinzufügen")
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
            st.markdown("1. Wähle links oben den Server im Dropdown aus.")
            st.markdown("2. Für neue Server zuerst Server Hinzufügen nutzen und Bot über den Link einladen.")
            st.markdown("3. Danach den Server wieder im Dropdown auswählen und Module konfigurieren.")
            st.markdown("4. Jede Konfiguration wird im eigenen Server-Profil gespeichert und nicht übernommen.")
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
            "Ankündigungen": "Ankündigungen",
            "Reaction Roles": "Reaction Roles",
            "Custom Commands": "Custom Commands",
            "Umfragen": "Umfragen",
            "Warns/Sanktionen": "Warns/Sanktionen",
            "Logging": "Logging",
            "Embed Hub": "Embed Hub",
            "Settings": "Einstellungen",
            "Audit-Logs": "Audit-Logs",
        }
        nav_sections = [
            ("Grundlegende Informationen", ["Overview", "Tickets", "Stempeluhr"]),
            ("Server-Verwaltung", ["Server Tools", "Auto Mod", "Warns/Sanktionen", "Logging"]),
            ("Community", ["Ankündigungen", "Reaction Roles", "Custom Commands", "Umfragen", "Giveaway", "If Rules", "Embed Hub"]),
            ("System", ["Settings", "Audit-Logs"]),
        ]
        nav_icon_map = {
            "Overview": "◉",
            "Tickets": "✦",
            "Stempeluhr": "◷",
            "Server Tools": "🛠",
            "Auto Mod": "🛡",
            "If Rules": "↯",
            "Giveaway": "🎁",
            "Ankündigungen": "📣",
            "Reaction Roles": "◎",
            "Custom Commands": "⌘",
            "Umfragen": "🗳",
            "Warns/Sanktionen": "⚖",
            "Logging": "⎘",
            "Embed Hub": "◈",
            "Settings": "⚙",
            "Audit-Logs": "🧾",
        }
        nav_display_map = {
            "Overview": "Übersicht",
            "Tickets": "Tickets",
            "Stempeluhr": "Stempeluhr",
            "Server Tools": "Server-Tools",
            "Auto Mod": "Auto-Moderation",
            "If Rules": "Wenn-Regeln",
            "Giveaway": "Gewinnspiel",
            "Ankündigungen": "Ankündigungen",
            "Reaction Roles": "Reaktionsrollen",
            "Custom Commands": "Eigene Befehle",
            "Umfragen": "Umfragen",
            "Warns/Sanktionen": "Warns/Sanktionen",
            "Logging": "Protokolle",
            "Embed Hub": "Embed-Vorlagen",
            "Settings": "Einstellungen",
            "Audit-Logs": "Audit-Logs",
        }

        nav_options = list(page_map.keys())
        if st.session_state.get("active_page") == "Announcements":
            st.session_state.active_page = "Ankündigungen"
        if st.session_state.get("active_page") == "Polls":
            st.session_state.active_page = "Umfragen"
        if st.session_state.get("active_page") == "Moderation":
            st.session_state.active_page = "Warns/Sanktionen"
        if "active_page" not in st.session_state or st.session_state.active_page not in nav_options:
            st.session_state.active_page = nav_options[0]

        st.sidebar.markdown("### Schnellnavigation")
        for section_title, section_items in nav_sections:
            st.sidebar.markdown(f"<div class='sidebar-section-title'>{section_title}</div>", unsafe_allow_html=True)
            for nav_key in section_items:
                nav_label = f"{nav_icon_map.get(nav_key, '•')}  {nav_display_map.get(nav_key, nav_key)}"
                is_active = st.session_state.active_page == nav_key
                if st.sidebar.button(nav_label, key=f"nav_btn_{nav_key}", use_container_width=True, type="primary" if is_active else "secondary"):
                    st.session_state.active_page = nav_key
                    st.rerun()
            st.sidebar.markdown("<div class='sidebar-section-gap'></div>", unsafe_allow_html=True)

        page = page_map[st.session_state.active_page]
        st.sidebar.markdown("<hr class='soft-divider' />", unsafe_allow_html=True)
        st.caption(f"Aktiver Server: {chosen_server_label}")

        if st.sidebar.button("Abmelden"):
            st.session_state.logged_in = False
            st.rerun()
        
        if page == "Übersicht":
            render_page_header("Bot Übersicht", "Schneller Überblick über Status und Kernmetriken.")
            _enable_overview_autorefresh(8000)
            refreshed_data = load_discord_data()
            runtime = _bot_runtime_status()
            guild_stats = _guild_stats_for_selected(discord_data, selected_server_entry)
            if isinstance(refreshed_data, dict):
                guild_stats = _guild_stats_for_selected(refreshed_data, selected_server_entry)
            live_tickets = _live_ticket_count_for_selected(selected_server_entry)
            members = _guild_members_for_selected(refreshed_data if isinstance(refreshed_data, dict) else discord_data, selected_server_entry)

            if guild_stats.get("member_count", 0) <= 0 and members:
                guild_stats["member_count"] = len(members)
            if guild_stats.get("online_count", 0) <= 0 and members:
                guild_stats["online_count"] = len([m for m in members if isinstance(m, dict) and bool(m.get("online", False))])

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mitglieder", str(guild_stats.get("member_count", 0)))
            with col2:
                st.metric("Online", str(guild_stats.get("online_count", 0)))
            with col3:
                st.metric("Tickets", str(live_tickets))
            
            st.markdown("### Letzte Aktivitäten")
            state_text = "Bot online" if runtime.get("online") else "Bot offline"
            state_color = "#86efac" if runtime.get("online") else "#fca5a5"
            last_seen = runtime.get("last_seen") or "unbekannt"
            st.markdown(
                f'<div class="status-card"><b style="color:{state_color};">{state_text}</b><br/>Live-Refresh: alle 8 Sekunden<br/>Letztes Heartbeat: {last_seen}</div>',
                unsafe_allow_html=True,
            )
            _render_member_copy_list(members)

        elif page == "Tickets":
            render_page_header("Ticketsystem", "Übersicht und pro Panel ein strukturierter Editor.")

            if "tickets_editor_open" not in st.session_state:
                st.session_state.tickets_editor_open = False
            if "tickets_selected_index" not in st.session_state:
                st.session_state.tickets_selected_index = 0

            ticket_panels = settings.get("ticket_panels") if isinstance(settings.get("ticket_panels"), list) else []
            if "ticket_panels" not in settings:
                ticket_panels = [
                    {
                        "name": settings.get("tickets_panel_name", "Neues Ticket-Panel"),
                        "enabled": settings.get("tickets_enabled", False),
                        "panel_channel_id": settings.get("tickets_panel_channel_id"),
                        "manager_roles": settings.get("tickets_manager_roles", []),
                        "panel_title": settings.get("tickets_panel_title", "🎫 Ticket-System"),
                        "panel_description": settings.get("tickets_panel_description", "Wähle eine Option, um ein Ticket zu erstellen."),
                        "panel_mode": settings.get("tickets_panel_mode", "buttons"),
                        "options": settings.get("tickets_categories", []),
                        "open_category_id": settings.get("tickets_open_category_id"),
                        "claimed_category_id": settings.get("tickets_claimed_category_id"),
                        "closed_category_id": settings.get("tickets_closed_category_id"),
                        "transcript_channel_id": settings.get("tickets_transcript_channel_id"),
                        "transcript_dm_enabled": settings.get("tickets_transcript_dm_enabled", False),
                        "delete_on_close": settings.get("tickets_delete_on_close", True),
                        "opened_message": settings.get("tickets_opened_message", "Dein Ticket wurde erstellt. Bitte gib alle zusätzlichen Informationen an."),
                    }
                ]

            if not st.session_state.tickets_editor_open:
                top_col, stat_toggle_col = st.columns([10, 2])
                with top_col:
                    st.markdown("### Deine Ticket-Panels")
                with stat_toggle_col:
                    active_count = len([p for p in ticket_panels if p.get("enabled", False)])
                    st.markdown(f"<div style='text-align:right;'>Aktiv: {active_count}</div>", unsafe_allow_html=True)

                stat_left, stat_right = st.columns([7, 3])
                with stat_left:
                    st.caption("Die Befehle können nur von Ticketmanagern in einem Ticketkanal ausgeführt werden.")
                with stat_right:
                    st.markdown(f"<div style='text-align:right;'>{len(ticket_panels)} / 10</div>", unsafe_allow_html=True)

                list_col, action_col = st.columns([8, 2])
                with action_col:
                    if st.button("+ Ein Panel erstellen"):
                        ticket_panels.append(
                            {
                                "name": f"Neues Ticket-Panel {len(ticket_panels) + 1}",
                                "enabled": False,
                                "panel_channel_id": "",
                                "manager_roles": [],
                                "panel_title": "🎫 Ticket-System",
                                "panel_description": "Wähle eine Option, um ein Ticket zu erstellen.",
                                "panel_mode": "buttons",
                                "options": [],
                                "open_category_id": "",
                                "claimed_category_id": "",
                                "closed_category_id": "",
                                "transcript_channel_id": "",
                                "transcript_dm_enabled": False,
                                "delete_on_close": True,
                                "opened_message": "Dein Ticket wurde erstellt. Bitte gib alle zusätzlichen Informationen an.",
                            }
                        )
                        st.session_state.tickets_selected_index = len(ticket_panels) - 1
                        st.session_state.tickets_editor_snapshot = deepcopy(ticket_panels[st.session_state.tickets_selected_index])
                        st.session_state.tickets_confirm_leave = False
                        st.session_state.tickets_editor_open = True
                        st.rerun()
                    delete_from_overview = st.button("Markierte löschen", type="secondary")

                if delete_from_overview:
                    remaining_panels = []
                    for idx, panel_item in enumerate(ticket_panels):
                        if not st.session_state.get(f"ticket_delete_mark_{idx}", False):
                            remaining_panels.append(panel_item)

                    ticket_panels = remaining_panels
                    settings["ticket_panels"] = ticket_panels
                    if not ticket_panels:
                        settings["tickets_enabled"] = False
                        settings["ticket_channel_id"] = ""
                        settings["tickets_panel_channel_id"] = ""
                        settings["tickets_panel_mode"] = "buttons"
                        settings["tickets_panel_name"] = "Neues Ticket-Panel"
                        settings["tickets_panel_title"] = "🎫 Ticket-System"
                        settings["tickets_panel_description"] = "Wähle eine Option, um ein Ticket zu erstellen."
                        settings["tickets_categories"] = []
                        settings["tickets_manager_roles"] = []
                        settings["tickets_open_category_id"] = ""
                        settings["tickets_claimed_category_id"] = ""
                        settings["tickets_closed_category_id"] = ""
                        settings["tickets_transcript_channel_id"] = ""
                        settings["tickets_transcript_dm_enabled"] = False
                        settings["tickets_delete_on_close"] = True
                        settings["tickets_opened_message"] = "Dein Ticket wurde erstellt. Bitte gib alle zusätzlichen Informationen an."
                        settings["tickets_publish_trigger"] = False
                        st.session_state.tickets_selected_index = 0
                    else:
                        st.session_state.tickets_selected_index = min(st.session_state.tickets_selected_index, len(ticket_panels) - 1)
                    save_settings(settings)
                    st.success("Markierte Ticket-Panels wurden gelöscht.")
                    st.rerun()

                with list_col:
                    for idx, panel in enumerate(ticket_panels):
                        row_card_col, row_action_col = st.columns([8, 2])
                        with row_card_col:
                            channel_id_preview = panel.get("panel_channel_id") or "-"
                            status_text = "Veröffentlicht" if panel.get("enabled", False) else "Entwurf"
                            st.markdown(
                                f"<div class='ticket-panel-card'><div class='ticket-panel-head'><span>{panel.get('name', f'Ticket-Panel {idx + 1}')}</span>"
                                f"<span class='pill-ok'>{status_text}</span></div><div class='ticket-panel-meta'>Kanal-ID: {channel_id_preview}</div>"
                                f"<div class='ticket-panel-meta'>Modus: {panel.get('panel_mode', 'buttons')}</div></div>",
                                unsafe_allow_html=True,
                            )
                        with row_action_col:
                            if st.button(f"Bearbeiten", key=f"ticket_edit_btn_{idx}", use_container_width=True):
                                st.session_state.tickets_selected_index = idx
                                st.session_state.tickets_editor_snapshot = deepcopy(ticket_panels[idx])
                                st.session_state.tickets_confirm_leave = False
                                st.session_state.tickets_editor_open = True
                                st.rerun()
                            st.checkbox("Löschen", key=f"ticket_delete_mark_{idx}")

                st.subheader("Befehle")
                st.markdown("<div class='ticket-command-row'>/ticket-claim - Beanspruche ein Ticket</div>", unsafe_allow_html=True)
                st.markdown("<div class='ticket-command-row'>/ticket-close - Schliesse ein Ticket</div>", unsafe_allow_html=True)
                st.markdown("<div class='ticket-command-row'>/ticket-delete - optional über Kanal-Löschung bei Close</div>", unsafe_allow_html=True)

            else:
                if not ticket_panels:
                    st.session_state.tickets_editor_open = False
                    st.rerun()
                selected_idx = min(st.session_state.get("tickets_selected_index", 0), len(ticket_panels) - 1)
                panel = ticket_panels[selected_idx]
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
                    publish_btn = st.button("Veröffentlichen")

                st.session_state.tickets_confirm_delete = st.checkbox(
                    "Panel wirklich löschen",
                    value=st.session_state.get("tickets_confirm_delete", False),
                    key="tickets_confirm_delete_checkbox",
                )
                delete_btn = st.button("Panel jetzt löschen", type="secondary")

                with st.expander("Allgemein", expanded=True):
                    panel_channel_id = select_channel_id(
                        "Kanal veröffentlichen",
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
                    panel_description = st.text_area("Beschreibung", value=panel.get("panel_description", "Wähle eine Option, um ein Ticket zu erstellen."))

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
                        opt_name = st.text_input("Buttonname", value=str(base.get("name", f"Ticket öffnen {idx + 1}")), key=f"ticket_editor_name_{idx}")
                        opt_desc = st.text_input("Beschreibung", value=str(base.get("description", "Unser Team kann dir helfen!")), key=f"ticket_editor_desc_{idx}")
                        opt_cat_open = select_category_id("Kategorie für erstellte Tickets", categories_map, base.get("category_channel_id"), f"ticket_editor_open_cat_{idx}", allow_manual_input=False)
                        opt_cat_claimed = select_category_id("Kategorie für beanspruchte Tickets", categories_map, panel.get("claimed_category_id"), f"ticket_editor_claim_cat_{idx}", allow_manual_input=False)
                        opt_cat_closed = select_category_id("Kategorie für geschlossene Tickets", categories_map, panel.get("closed_category_id"), f"ticket_editor_close_cat_{idx}", allow_manual_input=False)
                        built_options.append(
                            {
                                "emoji": opt_emoji,
                                "name": opt_name,
                                "description": opt_desc,
                                "category_channel_id": int(opt_cat_open) if (opt_cat_open and str(opt_cat_open).isdigit()) else opt_cat_open,
                                "auto_role_id": None,
                            }
                        )

                with st.expander("Nachricht zur Ticketeröffnung", expanded=True):
                    opened_message = st.text_area(
                        "Nachrichtstext",
                        value=panel.get("opened_message", "Dein Ticket wurde erstellt. Bitte gib alle zusätzlichen Informationen an."),
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
                    st.warning("Es gibt ungespeicherte Änderungen.")
                    st.session_state.tickets_confirm_leave = st.checkbox(
                        "Ungespeicherte Änderungen beim Verlassen verwerfen",
                        value=st.session_state.tickets_confirm_leave,
                        key="tickets_confirm_leave_checkbox",
                    )
                else:
                    st.session_state.tickets_confirm_leave = False

                if back_btn or discard_btn:
                    if has_unsaved_changes and not st.session_state.tickets_confirm_leave:
                        st.error("Bitte bestätige zuerst das Verwerfen ungespeicherter Änderungen.")
                        st.stop()
                    st.session_state.pop("tickets_editor_snapshot", None)
                    st.session_state.tickets_confirm_leave = False
                    st.session_state.tickets_editor_open = False
                    st.rerun()

                if delete_btn:
                    if not st.session_state.tickets_confirm_delete:
                        st.error("Bitte bestätige zuerst 'Panel wirklich löschen'.")
                        st.stop()
                    settings["ticket_panels"] = []
                    settings["tickets_enabled"] = False
                    settings["ticket_channel_id"] = ""
                    settings["tickets_panel_channel_id"] = ""
                    settings["tickets_panel_mode"] = "buttons"
                    settings["tickets_panel_name"] = "Neues Ticket-Panel"
                    settings["tickets_panel_title"] = "🎫 Ticket-System"
                    settings["tickets_panel_description"] = "Wähle eine Option, um ein Ticket zu erstellen."
                    settings["tickets_categories"] = []
                    settings["tickets_manager_roles"] = []
                    settings["tickets_open_category_id"] = ""
                    settings["tickets_claimed_category_id"] = ""
                    settings["tickets_closed_category_id"] = ""
                    settings["tickets_transcript_channel_id"] = ""
                    settings["tickets_transcript_dm_enabled"] = False
                    settings["tickets_delete_on_close"] = True
                    settings["tickets_opened_message"] = "Dein Ticket wurde erstellt. Bitte gib alle zusätzlichen Informationen an."
                    settings["tickets_publish_trigger"] = False
                    save_settings(settings)
                    st.session_state.pop("tickets_editor_snapshot", None)
                    st.session_state.tickets_confirm_leave = False
                    st.session_state.tickets_confirm_delete = False
                    st.session_state.tickets_editor_open = False
                    st.success("Ticket-Panel wurde gelöscht.")
                    st.rerun()

                if save_btn or publish_btn:
                    panel.update(draft_panel)
                    ticket_panels[selected_idx] = panel
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
                    st.success("Ticket-Panel gespeichert." if save_btn else "Ticket-Panel gespeichert und wird veröffentlicht.")

        elif page == "Stempeluhr":
            render_page_header("Stempeluhr System", "Übersicht und strukturierter Editor für Rollen und Panel-Verwaltung.")

            if "stempeluhr_editor_open" not in st.session_state:
                st.session_state.stempeluhr_editor_open = False
            if "stempeluhr_selected_index" not in st.session_state:
                st.session_state.stempeluhr_selected_index = 0

            stempel_panels = settings.get("stempeluhr_panels") if isinstance(settings.get("stempeluhr_panels"), list) else []
            if "stempeluhr_panels" not in settings:
                stempel_panels = [
                    {
                        "name": settings.get("stempeluhr_panel_name", "Stempeluhr Panel"),
                        "enabled": settings.get("stempeluhr_enabled", False),
                        "panel_channel_id": settings.get("stempeluhr_panel_channel_id", ""),
                        "ein_roles": settings.get("stempel_ein_roles", []),
                        "aus_roles": settings.get("stempel_aus_roles", []),
                    }
                ]

            if not st.session_state.stempeluhr_editor_open:
                top_col, stat_toggle_col = st.columns([10, 2])
                with top_col:
                    st.markdown("### Deine Stempeluhr-Panels")
                with stat_toggle_col:
                    active_count = len([p for p in stempel_panels if p.get("enabled", False)])
                    st.markdown(f"<div style='text-align:right;'>Aktiv: {active_count}</div>", unsafe_allow_html=True)

                stat_left, stat_right = st.columns([7, 3])
                with stat_left:
                    st.caption("Nur berechtigte Rollen können Ein-/Ausstempeln verwenden.")
                with stat_right:
                    st.markdown(f"<div style='text-align:right;'>{len(stempel_panels)} / 5</div>", unsafe_allow_html=True)

                list_col, action_col = st.columns([8, 2])
                with action_col:
                    if st.button("+ Ein Panel erstellen", key="stempeluhr_new_panel"):
                        stempel_panels.append(
                            {
                                "name": f"Stempeluhr Panel {len(stempel_panels) + 1}",
                                "enabled": False,
                                "panel_channel_id": "",
                                "ein_roles": [],
                                "aus_roles": [],
                            }
                        )
                        st.session_state.stempeluhr_selected_index = len(stempel_panels) - 1
                        st.session_state.stempeluhr_editor_snapshot = deepcopy(stempel_panels[st.session_state.stempeluhr_selected_index])
                        st.session_state.stempeluhr_confirm_leave = False
                        st.session_state.stempeluhr_editor_open = True
                        st.rerun()
                    delete_stempel_from_overview = st.button("Markierte löschen", key="stempeluhr_delete_marked", type="secondary")

                if delete_stempel_from_overview:
                    remaining_stempel = []
                    for idx, panel_item in enumerate(stempel_panels):
                        if not st.session_state.get(f"stempeluhr_delete_mark_{idx}", False):
                            remaining_stempel.append(panel_item)
                    stempel_panels = remaining_stempel
                    settings["stempeluhr_panels"] = stempel_panels
                    if not stempel_panels:
                        settings["stempeluhr_enabled"] = False
                        settings["stempel_ein_roles"] = []
                        settings["stempel_aus_roles"] = []
                        settings["stempeluhr_allowed_roles"] = []
                        settings["stempeluhr_admin_roles"] = []
                        settings["stempeluhr_panel_channel_id"] = ""
                        settings["stempeluhr_panel_name"] = "Stempeluhr Panel"
                        st.session_state.stempeluhr_selected_index = 0
                    else:
                        st.session_state.stempeluhr_selected_index = min(st.session_state.stempeluhr_selected_index, len(stempel_panels) - 1)
                    save_settings(settings)
                    st.success("Markierte Stempeluhr-Panels wurden gelöscht.")
                    st.rerun()

                with list_col:
                    for idx, panel in enumerate(stempel_panels):
                        row_card_col, row_action_col = st.columns([8, 2])
                        with row_card_col:
                            channel_id_preview = panel.get("panel_channel_id") or "-"
                            status_text = "Veröffentlicht" if panel.get("enabled", False) else "Entwurf"
                            ein_count = len(panel.get("ein_roles", []) or [])
                            aus_count = len(panel.get("aus_roles", []) or [])
                            st.markdown(
                                f"<div class='ticket-panel-card'><div class='ticket-panel-head'><span>{panel.get('name', f'Stempeluhr Panel {idx + 1}')}</span>"
                                f"<span class='pill-ok'>{status_text}</span></div><div class='ticket-panel-meta'>Kanal-ID: {channel_id_preview}</div>"
                                f"<div class='ticket-panel-meta'>/stempel_ein Rollen: {ein_count} | /stempel_aus Rollen: {aus_count}</div></div>",
                                unsafe_allow_html=True,
                            )
                        with row_action_col:
                            if st.button("Bearbeiten", key=f"stempeluhr_edit_btn_{idx}", use_container_width=True):
                                st.session_state.stempeluhr_selected_index = idx
                                st.session_state.stempeluhr_editor_snapshot = deepcopy(stempel_panels[idx])
                                st.session_state.stempeluhr_confirm_leave = False
                                st.session_state.stempeluhr_editor_open = True
                                st.rerun()
                            st.checkbox("Löschen", key=f"stempeluhr_delete_mark_{idx}")

                st.subheader("Befehle")
                st.markdown("<div class='ticket-command-row'>/stempel_ein - Schicht starten</div>", unsafe_allow_html=True)
                st.markdown("<div class='ticket-command-row'>/stempel_aus - Schicht beenden</div>", unsafe_allow_html=True)

            else:
                if not stempel_panels:
                    st.session_state.stempeluhr_editor_open = False
                    st.rerun()
                stempel_idx = min(st.session_state.get("stempeluhr_selected_index", 0), len(stempel_panels) - 1)
                panel = stempel_panels[stempel_idx]
                if "stempeluhr_editor_snapshot" not in st.session_state:
                    st.session_state.stempeluhr_editor_snapshot = deepcopy(panel)
                if "stempeluhr_confirm_leave" not in st.session_state:
                    st.session_state.stempeluhr_confirm_leave = False

                back_col, title_col, action_col = st.columns([1, 7, 4])
                with back_col:
                    back_btn = st.button("<", key="stempeluhr_back")
                with title_col:
                    panel_name = st.text_input("Panelname", value=panel.get("name", "Stempeluhr Panel"), key="stempeluhr_panel_name_input")
                with action_col:
                    discard_btn = st.button("Verwerfen", key="stempeluhr_discard")
                    save_btn = st.button("Speichern", key="stempeluhr_save")
                    publish_btn = st.button("Veröffentlichen", key="stempeluhr_publish")

                with st.expander("Allgemein", expanded=True):
                    stempeluhr_enabled = st.checkbox("Stempeluhr aktivieren", value=panel.get("enabled", False), key="stempeluhr_editor_enabled")
                    panel_channel_id = select_channel_id(
                        "Stempeluhr Panel Channel",
                        channels_map,
                        panel.get("panel_channel_id", ""),
                        "stempeluhr_editor_panel_channel",
                    )

                with st.expander("Berechtigungen", expanded=True):
                    role_names = list(roles_map.keys())
                    default_ein_names = names_for_ids(roles_map, panel.get("ein_roles", []))
                    default_aus_names = names_for_ids(roles_map, panel.get("aus_roles", []))
                    selected_ein_roles = st.multiselect(
                        "Wer darf /stempel_ein nutzen?",
                        options=role_names,
                        default=default_ein_names,
                        key="stempeluhr_editor_ein_roles",
                    )
                    selected_aus_roles = st.multiselect(
                        "Wer darf /stempel_aus nutzen?",
                        options=role_names,
                        default=default_aus_names,
                        key="stempeluhr_editor_aus_roles",
                    )
                    manual_ein_ids = parse_id_list(
                        st.text_input(
                            "Rollen-IDs für /stempel_ein (Fallback, komma-separiert)",
                            value=", ".join([str(x) for x in panel.get("ein_roles", [])]),
                            key="stempeluhr_editor_ein_roles_manual",
                        )
                    )
                    manual_aus_ids = parse_id_list(
                        st.text_input(
                            "Rollen-IDs für /stempel_aus (Fallback, komma-separiert)",
                            value=", ".join([str(x) for x in panel.get("aus_roles", [])]),
                            key="stempeluhr_editor_aus_roles_manual",
                        )
                    )

                resolved_ein = [str(roles_map[r]) for r in selected_ein_roles]
                resolved_aus = [str(roles_map[r]) for r in selected_aus_roles]
                final_ein = manual_ein_ids or resolved_ein
                final_aus = manual_aus_ids or resolved_aus

                draft_panel = {
                    "name": panel_name,
                    "enabled": bool(stempeluhr_enabled),
                    "panel_channel_id": panel_channel_id,
                    "ein_roles": final_ein,
                    "aus_roles": final_aus,
                }

                has_unsaved_changes = draft_panel != st.session_state.stempeluhr_editor_snapshot
                if has_unsaved_changes:
                    st.warning("Es gibt ungespeicherte Änderungen.")
                    st.session_state.stempeluhr_confirm_leave = st.checkbox(
                        "Ungespeicherte Änderungen beim Verlassen verwerfen",
                        value=st.session_state.stempeluhr_confirm_leave,
                        key="stempeluhr_confirm_leave_checkbox",
                    )
                else:
                    st.session_state.stempeluhr_confirm_leave = False

                if back_btn or discard_btn:
                    if has_unsaved_changes and not st.session_state.stempeluhr_confirm_leave:
                        st.error("Bitte bestätige zuerst das Verwerfen ungespeicherter Änderungen.")
                        st.stop()
                    st.session_state.pop("stempeluhr_editor_snapshot", None)
                    st.session_state.stempeluhr_confirm_leave = False
                    st.session_state.stempeluhr_editor_open = False
                    st.rerun()

                if save_btn or publish_btn:
                    panel.update(draft_panel)
                    stempel_panels[stempel_idx] = panel
                    settings["stempeluhr_panels"] = stempel_panels

                    settings["stempeluhr_enabled"] = panel.get("enabled", False)
                    settings["stempel_ein_roles"] = final_ein
                    settings["stempel_aus_roles"] = final_aus
                    settings["stempeluhr_allowed_roles"] = list(dict.fromkeys(final_ein + final_aus))
                    settings["stempeluhr_admin_roles"] = list(dict.fromkeys(final_aus))
                    settings["stempeluhr_panel_channel_id"] = panel_channel_id
                    settings["stempeluhr_panel_name"] = panel_name

                    if publish_btn:
                        settings["stempeluhr_publish_trigger"] = True

                    save_settings(settings)
                    st.session_state.stempeluhr_editor_snapshot = deepcopy(panel)
                    st.session_state.stempeluhr_confirm_leave = False
                    st.success("Stempeluhr gespeichert." if save_btn else "Stempeluhr gespeichert und Panel wird veröffentlicht.")

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
            render_page_header("Server Tools", "Moderationstools für den RP-Alltag: Slowmode, Lock/Unlock, Timeout.")
            legacy_default = settings.get("server_tools_enabled", True)
            slowmode_enabled = st.checkbox("/slowmode aktivieren", value=settings.get("server_tools_slowmode_enabled", legacy_default))
            lock_enabled = st.checkbox("/lock aktivieren", value=settings.get("server_tools_lock_enabled", legacy_default))
            unlock_enabled = st.checkbox("/unlock aktivieren", value=settings.get("server_tools_unlock_enabled", legacy_default))
            timeout_enabled = st.checkbox("/timeout aktivieren", value=settings.get("server_tools_timeout_enabled", legacy_default))
            untimeout_enabled = st.checkbox("/untimeout aktivieren", value=settings.get("server_tools_untimeout_enabled", legacy_default))
            server_tools_send_as_embed = st.checkbox("Antworten als Embed senden", value=settings.get("server_tools_send_as_embed", True))
            if st.button("Server Tools speichern"):
                settings["server_tools_slowmode_enabled"] = slowmode_enabled
                settings["server_tools_lock_enabled"] = lock_enabled
                settings["server_tools_unlock_enabled"] = unlock_enabled
                settings["server_tools_timeout_enabled"] = timeout_enabled
                settings["server_tools_untimeout_enabled"] = untimeout_enabled
                settings["server_tools_send_as_embed"] = server_tools_send_as_embed
                settings["server_tools_enabled"] = any([
                    slowmode_enabled,
                    lock_enabled,
                    unlock_enabled,
                    timeout_enabled,
                    untimeout_enabled,
                ])
                save_settings(settings)
                _append_audit_entry("Server Tools", "Einstellungen gespeichert", f"Aktive Tools: {sum([slowmode_enabled, lock_enabled, unlock_enabled, timeout_enabled, untimeout_enabled])}")
                st.success("Server Tools gespeichert.")

        elif page == "Wenn-Funktionen":
            render_page_header("Wenn-Funktionen", "Eventbasierte Regeln für Rollen-Events und Auto-Aktionen.")
            custom_rules = settings.get("custom_rules", []) if isinstance(settings.get("custom_rules"), list) else []
            custom_rules = [_normalize_if_rule(r) for r in custom_rules]
            settings["custom_rules"] = custom_rules
            custom_enabled = st.checkbox("Wenn-Funktionen aktivieren", value=settings.get("custom_rules_enabled", False))
            ifrules_scope_role_names = st.multiselect(
                "Regeln nur für Mitglieder mit diesen Rollen (optional)",
                options=list(roles_map.keys()),
                default=names_for_ids(roles_map, settings.get("if_rules_scope_roles", [])),
                key="ifrules_scope_roles",
            )
            ifrules_scope_roles = [str(roles_map[name]) for name in ifrules_scope_role_names if name in roles_map]

            if "ifrules_editor_open" not in st.session_state:
                st.session_state.ifrules_editor_open = False
            if "ifrules_selected_index" not in st.session_state:
                st.session_state.ifrules_selected_index = 0

            if not st.session_state.ifrules_editor_open:
                st.subheader("Regel-Übersicht")
                list_col, action_col = st.columns([8, 2])
                with action_col:
                    if st.button("+ Regel erstellen", key="ifrules_new"):
                        _push_undo_snapshot(settings, "if_rules", settings.get("custom_rules", []))
                        custom_rules.append(
                            {
                                "event": "role_add",
                                "role": "",
                                "action": "send_message",
                                "channel": "",
                                "message": "Hallo {user}",
                                "send_as_embed": False,
                                "allowed_roles": [],
                            }
                        )
                        settings["custom_rules"] = custom_rules
                        settings["custom_rules_enabled"] = custom_enabled
                        settings["if_rules_scope_roles"] = ifrules_scope_roles
                        save_settings(settings)
                        _append_audit_entry("Wenn-Funktionen", "Regel erstellt", f"Regeln: {len(custom_rules)}")
                        st.session_state.ifrules_selected_index = len(custom_rules) - 1
                        st.session_state.ifrules_editor_open = True
                        st.rerun()
                    delete_marked = st.button("Markierte löschen", key="ifrules_delete_marked", type="secondary")
                    if st.button("Status speichern", key="ifrules_save_status"):
                        settings["custom_rules_enabled"] = custom_enabled
                        settings["if_rules_scope_roles"] = ifrules_scope_roles
                        save_settings(settings)
                        _append_audit_entry("Wenn-Funktionen", "Status gespeichert", f"Aktiv: {custom_enabled}")
                        st.success("Wenn-Funktionen gespeichert.")
                    if st.button("Letzte Änderung rückgängig", key="ifrules_undo", type="secondary"):
                        restored = _pop_undo_snapshot(settings, "if_rules")
                        if restored is None:
                            st.warning("Keine rückgängig machbare Änderung vorhanden.")
                        else:
                            settings["custom_rules"] = [_normalize_if_rule(r) for r in restored]
                            save_settings(settings)
                            _append_audit_entry("Wenn-Funktionen", "Rückgängig", "Letzte Änderung wiederhergestellt")
                            st.success("Letzte Änderung wurde rückgängig gemacht.")
                            st.rerun()

                if delete_marked:
                    keep_rules = [
                        rule for i, rule in enumerate(custom_rules)
                        if not st.session_state.get(f"ifrules_delete_mark_{i}", False)
                    ]
                    if len(keep_rules) == len(custom_rules):
                        st.warning("Keine Regel zum Löschen markiert.")
                    else:
                        _push_undo_snapshot(settings, "if_rules", custom_rules)
                        custom_rules = keep_rules
                        settings["custom_rules"] = custom_rules
                        settings["custom_rules_enabled"] = custom_enabled
                        settings["if_rules_scope_roles"] = ifrules_scope_roles
                        save_settings(settings)
                        _append_audit_entry("Wenn-Funktionen", "Regeln gelöscht", f"Verbleibend: {len(custom_rules)}")
                        st.success("Markierte Regeln wurden gelöscht.")
                        st.rerun()

                with list_col:
                    if not custom_rules:
                        st.info("Noch keine Regeln vorhanden.")
                    for idx, rule in enumerate(custom_rules):
                        row_card_col, row_action_col = st.columns([8, 2])
                        with row_card_col:
                            st.markdown(
                                f"<div class='ticket-panel-card'><div class='ticket-panel-head'><span>Regel {idx + 1}</span>"
                                f"<span class='pill-ok'>{rule.get('event', 'role_add')}</span></div>"
                                f"<div class='ticket-panel-meta'>Rolle-ID: {rule.get('role', '-') or '-'}</div>"
                                f"<div class='ticket-panel-meta'>Kanal-ID: {rule.get('channel', '-') or '-'}</div></div>",
                                unsafe_allow_html=True,
                            )
                        with row_action_col:
                            if st.button("Bearbeiten", key=f"ifrules_edit_{idx}", use_container_width=True):
                                st.session_state.ifrules_selected_index = idx
                                st.session_state.ifrules_editor_open = True
                                st.rerun()
                            st.checkbox("Löschen", key=f"ifrules_delete_mark_{idx}")
            else:
                if not custom_rules:
                    st.session_state.ifrules_editor_open = False
                    st.rerun()

                selected_idx = min(st.session_state.get("ifrules_selected_index", 0), len(custom_rules) - 1)
                rule = custom_rules[selected_idx]

                back_col, title_col, action_col = st.columns([1, 7, 4])
                with back_col:
                    back_btn = st.button("<", key="ifrules_back")
                with title_col:
                    st.markdown(f"### Regel {selected_idx + 1} bearbeiten")
                with action_col:
                    discard_btn = st.button("Verwerfen", key="ifrules_discard")
                    save_btn = st.button("Speichern", key="ifrules_save")

                event = st.selectbox(
                    "Event",
                    ["role_add", "role_remove"],
                    index=0 if rule.get("event", "role_add") == "role_add" else 1,
                    key="ifrules_event",
                )
                role_id_value = select_role_id(
                    "Rolle",
                    roles_map,
                    rule.get("role", ""),
                    "ifrules_role",
                )
                selected_channel_id = select_channel_id(
                    "Kanal",
                    channels_map,
                    rule.get("channel", ""),
                    "ifrules_channel",
                )
                message = st.text_area(
                    "Nachricht",
                    value=rule.get("message", ""),
                    key="ifrules_message",
                    placeholder="Verwende {user} und {server}",
                )
                send_as_embed = st.checkbox("Als Embed senden", value=bool(rule.get("send_as_embed", False)), key="ifrules_send_as_embed")
                allowed_role_names = st.multiselect(
                    "Nur ausführen, wenn Mitglied eine dieser Rollen hat (optional)",
                    options=list(roles_map.keys()),
                    default=names_for_ids(roles_map, rule.get("allowed_roles", [])),
                    key="ifrules_allowed_roles",
                )
                allowed_role_ids = [str(roles_map[name]) for name in allowed_role_names if name in roles_map]
                st.caption("Vorschau")
                st.code(_preview_text(message, "#ziel-kanal"), language="text")

                if back_btn or discard_btn:
                    st.session_state.ifrules_editor_open = False
                    st.rerun()

                if save_btn:
                    if not role_id_value:
                        st.error("Bitte wähle eine Rolle oder trage eine Rollen-ID ein.")
                    elif not selected_channel_id:
                        st.error("Bitte wähle einen Kanal oder trage eine Kanal-ID ein.")
                    elif not message.strip():
                        st.error("Bitte eine Nachricht eintragen.")
                    else:
                        _push_undo_snapshot(settings, "if_rules", custom_rules)
                        custom_rules[selected_idx] = {
                            "event": event,
                            "role": str(role_id_value),
                            "action": "send_message",
                            "channel": str(selected_channel_id),
                            "message": message,
                            "send_as_embed": bool(send_as_embed),
                            "allowed_roles": allowed_role_ids,
                        }
                        settings["custom_rules"] = custom_rules
                        settings["custom_rules_enabled"] = custom_enabled
                        settings["if_rules_scope_roles"] = ifrules_scope_roles
                        save_settings(settings)
                        _append_audit_entry("Wenn-Funktionen", "Regel gespeichert", f"Regel {selected_idx + 1}")
                        st.success("Regel gespeichert.")
                        st.session_state.ifrules_editor_open = False
                        st.rerun()

        elif page == "Giveaway":
            render_page_header("Gewinnspiel", "Passe das Gewinnspiel-Embed im gewohnten Stil an.")
            giveaway_enabled = st.checkbox("Gewinnspiel aktivieren", value=settings.get("giveaway_enabled", False))
            giveaway_send_as_embed = st.checkbox("Nachrichten als Embed senden", value=settings.get("giveaway_send_as_embed", True))
            giveaway_embed_title, giveaway_embed_description, giveaway_embed_color, giveaway_embed_footer = render_embed_designer(
                settings,
                "giveaway_embed",
                "🎉 Giveaway!",
                "Gegenstand: {item}\nEndet in: {time}",
                "#ff4500",
                "Klicke auf Teilnehmen!",
                "giveaway",
            )
            
            if st.button("Gewinnspiel-Embed speichern"):
                settings["giveaway_enabled"] = giveaway_enabled
                settings["giveaway_embed_title"] = giveaway_embed_title
                settings["giveaway_embed_description"] = giveaway_embed_description
                settings["giveaway_embed_color"] = giveaway_embed_color
                settings["giveaway_embed_footer"] = giveaway_embed_footer
                settings["giveaway_send_as_embed"] = giveaway_send_as_embed
                save_settings(settings)
                st.success("Gewinnspiel-Embed gespeichert!")

        elif page == "Ankündigungen":
            render_page_header("Ankündigungen", "Steuere Channel, Embed-Layout und Publishing für Ankündigungen.")
            announce_enabled = st.checkbox("Ankündigungen aktivieren", value=settings.get("announce_enabled", True))
            current_announce_channel = settings.get("announce_channel_id", "")
            announce_channel_id = select_channel_id("Ankündigungs-Channel", channels_map, current_announce_channel, "announce_channel")
            
            announce_embed_enabled = st.checkbox("Als Embed senden", value=settings.get("announce_embed_enabled", False))
            if announce_embed_enabled:
                announce_embed_title, announce_embed_description, announce_embed_color, announce_embed_footer = render_embed_designer(
                    settings,
                    "announce_embed",
                    "📢 Ankündigung",
                    "{text}",
                    "#38bdf8",
                    "Gesendet von {user}",
                    "announce",
                )
                
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
            render_page_header("Reaktionsrollen", "Lege Rollen-Panels mit Emoji-Zuordnung einfach fest.")
            reaction_roles_enabled = st.checkbox("Reaktionsrollen aktivieren", value=settings.get("reaction_roles_enabled", False))
            rr_data = load_reaction_roles()

            rr_panels = settings.get("reaction_role_panels", []) if isinstance(settings.get("reaction_role_panels"), list) else []
            rr_panels = [_normalize_reaction_panel(panel, idx) for idx, panel in enumerate(rr_panels)]
            settings["reaction_role_panels"] = rr_panels
            rr_scope_role_names = st.multiselect(
                "Reaktionsrollen nur für Mitglieder mit diesen Rollen (optional)",
                options=list(roles_map.keys()),
                default=names_for_ids(roles_map, settings.get("reaction_roles_allowed_roles", [])),
                key="rr_scope_roles",
            )
            rr_scope_roles = [str(roles_map[name]) for name in rr_scope_role_names if name in roles_map]
            if "reaction_roles_editor_open" not in st.session_state:
                st.session_state.reaction_roles_editor_open = False
            if "reaction_roles_selected_index" not in st.session_state:
                st.session_state.reaction_roles_selected_index = 0
            
            async def _send_reaction_role(ch_id: int, embed: discord.Embed, emoji_role_map: dict, allowed_roles: list[str], send_as_embed: bool, fallback_text: str):
                # Runs in the bot event loop.
                bot = st.session_state.get("bot")
                if bot is None:
                    return
                chan = bot.get_channel(ch_id)
                if chan is None:
                    _append_audit_entry("Reaktionsrollen", "Publish fehlgeschlagen", f"Kanal {ch_id} nicht gefunden", status="failed")
                    return
                if send_as_embed:
                    msg = await chan.send(embed=embed)
                else:
                    plain_text = _preview_text(fallback_text or "Reagiere und erhalte deine Rollen.", "#rollen")
                    msg = await chan.send(content=plain_text)
                for emoji in emoji_role_map.keys():
                    await msg.add_reaction(emoji)
                rr_data[str(msg.id)] = emoji_role_map
                save_reaction_roles(rr_data)
                raw_settings_local = _safe_read_json(SETTINGS_FILE, {})
                meta = raw_settings_local.get("reaction_role_message_meta", {}) if isinstance(raw_settings_local.get("reaction_role_message_meta"), dict) else {}
                meta[str(msg.id)] = {"allowed_roles": [str(x) for x in (allowed_roles or []) if str(x).strip()]}
                raw_settings_local["reaction_role_message_meta"] = meta
                _write_raw_settings(raw_settings_local)
                from database import add_reaction_role
                await add_reaction_role(str(msg.id), json.dumps(emoji_role_map))
                _append_audit_entry("Reaktionsrollen", "Publish erfolgreich", f"Nachricht {msg.id} gesendet", status="sent")

            if not st.session_state.reaction_roles_editor_open:
                st.subheader("Panel-Übersicht")
                list_col, action_col = st.columns([8, 2])
                with action_col:
                    if st.button("+ Panel erstellen", key="rr_new"):
                        _push_undo_snapshot(settings, "reaction_roles", rr_panels)
                        rr_panels.append(
                            {
                                "name": f"Reaktionsrollen Panel {len(rr_panels) + 1}",
                                "enabled": False,
                                "channel_id": "",
                                "title": "Wähle deine Rollen",
                                "description": "Reagiere mit Emojis um Rollen zu bekommen.",
                                "color": "#8a2be2",
                                "send_as_embed": True,
                                "items": [],
                            }
                        )
                        settings["reaction_role_panels"] = rr_panels
                        settings["reaction_roles_enabled"] = reaction_roles_enabled
                        settings["reaction_roles_allowed_roles"] = rr_scope_roles
                        save_settings(settings)
                        _append_audit_entry("Reaktionsrollen", "Panel erstellt", f"Panels: {len(rr_panels)}")
                        st.session_state.reaction_roles_selected_index = len(rr_panels) - 1
                        st.session_state.reaction_roles_editor_open = True
                        st.rerun()
                    delete_marked = st.button("Markierte löschen", key="rr_delete_marked", type="secondary")
                    if st.button("Status speichern", key="rr_save_status"):
                        settings["reaction_roles_enabled"] = reaction_roles_enabled
                        settings["reaction_roles_allowed_roles"] = rr_scope_roles
                        save_settings(settings)
                        _append_audit_entry("Reaktionsrollen", "Status gespeichert", f"Aktiv: {reaction_roles_enabled}")
                        st.success("Reaktionsrollen gespeichert.")
                    if st.button("Letzte Änderung rückgängig", key="rr_undo", type="secondary"):
                        restored = _pop_undo_snapshot(settings, "reaction_roles")
                        if restored is None:
                            st.warning("Keine rückgängig machbare Änderung vorhanden.")
                        else:
                            settings["reaction_role_panels"] = [_normalize_reaction_panel(p, i) for i, p in enumerate(restored)]
                            save_settings(settings)
                            _append_audit_entry("Reaktionsrollen", "Rückgängig", "Letzte Änderung wiederhergestellt")
                            st.success("Letzte Änderung wurde rückgängig gemacht.")
                            st.rerun()

                if delete_marked:
                    keep_panels = [
                        panel for i, panel in enumerate(rr_panels)
                        if not st.session_state.get(f"rr_delete_mark_{i}", False)
                    ]
                    if len(keep_panels) == len(rr_panels):
                        st.warning("Kein Panel zum Löschen markiert.")
                    else:
                        _push_undo_snapshot(settings, "reaction_roles", rr_panels)
                        rr_panels = keep_panels
                        settings["reaction_role_panels"] = rr_panels
                        settings["reaction_roles_enabled"] = reaction_roles_enabled
                        settings["reaction_roles_allowed_roles"] = rr_scope_roles
                        save_settings(settings)
                        _append_audit_entry("Reaktionsrollen", "Panels gelöscht", f"Verbleibend: {len(rr_panels)}")
                        st.success("Markierte Reaktionsrollen-Panels wurden gelöscht.")
                        st.rerun()

                with list_col:
                    if not rr_panels:
                        st.info("Noch keine Reaktionsrollen-Panels vorhanden.")
                    for idx, panel in enumerate(rr_panels):
                        row_card_col, row_action_col = st.columns([8, 2])
                        with row_card_col:
                            status_text = "Veröffentlicht" if panel.get("enabled", False) else "Entwurf"
                            st.markdown(
                                f"<div class='ticket-panel-card'><div class='ticket-panel-head'><span>{panel.get('name', f'Panel {idx + 1}')}</span>"
                                f"<span class='pill-ok'>{status_text}</span></div>"
                                f"<div class='ticket-panel-meta'>Kanal-ID: {panel.get('channel_id', '-') or '-'}</div>"
                                f"<div class='ticket-panel-meta'>Rollen-Zuordnungen: {len(panel.get('items', []) or [])}</div></div>",
                                unsafe_allow_html=True,
                            )
                        with row_action_col:
                            if st.button("Bearbeiten", key=f"rr_edit_{idx}", use_container_width=True):
                                st.session_state.reaction_roles_selected_index = idx
                                st.session_state.reaction_roles_editor_open = True
                                st.rerun()
                            st.checkbox("Löschen", key=f"rr_delete_mark_{idx}")
            else:
                if not rr_panels:
                    st.session_state.reaction_roles_editor_open = False
                    st.rerun()

                selected_idx = min(st.session_state.get("reaction_roles_selected_index", 0), len(rr_panels) - 1)
                panel = rr_panels[selected_idx]
                items = panel.get("items", []) if isinstance(panel.get("items"), list) else []
                item1 = items[0] if len(items) > 0 and isinstance(items[0], dict) else {}
                item2 = items[1] if len(items) > 1 and isinstance(items[1], dict) else {}

                back_col, title_col, action_col = st.columns([1, 7, 4])
                with back_col:
                    back_btn = st.button("<", key="rr_back")
                with title_col:
                    panel_name = st.text_input("Panelname", value=panel.get("name", f"Reaktionsrollen Panel {selected_idx + 1}"), key="rr_panel_name")
                with action_col:
                    discard_btn = st.button("Verwerfen", key="rr_discard")
                    save_btn = st.button("Speichern", key="rr_save")
                    publish_btn = st.button("Veröffentlichen", key="rr_publish")

                rr_enabled = st.checkbox("Panel aktivieren", value=panel.get("enabled", False), key="rr_enabled")
                rr_channel_id = select_channel_id("Kanal", channels_map, panel.get("channel_id", ""), "rr_channel")
                title = st.text_input("Embed Titel", value=panel.get("title", "Wähle deine Rollen"), key="rr_title")
                description = st.text_area("Embed Beschreibung", value=panel.get("description", "Reagiere mit Emojis um Rollen zu bekommen."), key="rr_description")
                color = st.text_input("Embed Farbe (Hex)", value=panel.get("color", "#8a2be2"), key="rr_color")
                rr_send_as_embed = st.checkbox("Panel als Embed senden", value=bool(panel.get("send_as_embed", True)), key="rr_send_as_embed")

                st.subheader("Rollen zuweisen")
                emoji1 = st.text_input("Emoji 1", value=str(item1.get("emoji", "🔴")), key="rr_emoji1")
                role1 = select_role_id("Rolle 1", roles_map, item1.get("role_id"), "rr_role1")
                emoji2 = st.text_input("Emoji 2", value=str(item2.get("emoji", "🔵")), key="rr_emoji2")
                role2 = select_role_id("Rolle 2", roles_map, item2.get("role_id"), "rr_role2")
                panel_allowed_names = st.multiselect(
                    "Nur für Mitglieder mit diesen Rollen (optional)",
                    options=list(roles_map.keys()),
                    default=names_for_ids(roles_map, panel.get("allowed_roles", [])),
                    key="rr_panel_allowed_roles",
                )
                panel_allowed_roles = [str(roles_map[name]) for name in panel_allowed_names if name in roles_map]
                st.caption("Vorschau")
                st.code(f"Titel: {title}\nBeschreibung: {_preview_text(description, '#reaktion-kanal')}", language="text")

                if back_btn or discard_btn:
                    st.session_state.reaction_roles_editor_open = False
                    st.rerun()

                if save_btn or publish_btn:
                    items_built = []
                    if emoji1 and role1:
                        items_built.append({"emoji": emoji1, "role_id": str(role1)})
                    if emoji2 and role2:
                        items_built.append({"emoji": emoji2, "role_id": str(role2)})

                    panel.update(
                        {
                            "name": panel_name,
                            "enabled": rr_enabled,
                            "channel_id": rr_channel_id,
                            "title": title,
                            "description": description,
                            "color": color,
                            "send_as_embed": bool(rr_send_as_embed),
                            "items": items_built,
                            "allowed_roles": panel_allowed_roles,
                        }
                    )
                    rr_panels[selected_idx] = panel
                    settings["reaction_role_panels"] = rr_panels
                    settings["reaction_roles_enabled"] = reaction_roles_enabled
                    settings["reaction_roles_allowed_roles"] = rr_scope_roles

                    if publish_btn:
                        if not rr_channel_id or not title:
                            st.error("Kanal und Titel sind erforderlich.")
                        elif not items_built:
                            st.error("Mindestens eine Emoji-Rollen-Zuordnung ist erforderlich.")
                        else:
                            bot = st.session_state.get("bot")
                            if bot is None:
                                st.error("Bot-Session nicht verfügbar. Nutze den Befehl im Discord oder verbinde den Bot mit dem Dashboard.")
                            else:
                                try:
                                    parsed_color = int(str(color).strip().lstrip("#"), 16)
                                except ValueError:
                                    st.error("Ungültige Hex-Farbe. Beispiel: #8a2be2")
                                    save_settings(settings)
                                else:
                                    emoji_role_map = {item["emoji"]: item["role_id"] for item in items_built}
                                    embed = discord.Embed(title=title, description=description, color=parsed_color)
                                    effective_allowed = list(dict.fromkeys(rr_scope_roles + panel_allowed_roles))
                                    _append_audit_entry("Reaktionsrollen", "Publish gestartet", f"Panel {panel_name}", status="queued")
                                    bot.loop.create_task(_send_reaction_role(int(rr_channel_id), embed, emoji_role_map, effective_allowed, bool(rr_send_as_embed), description))
                                    panel["enabled"] = True
                                    rr_panels[selected_idx] = panel
                                    settings["reaction_role_panels"] = rr_panels
                                    save_settings(settings)
                                    st.success("Reaktionsrollen-Nachricht wird gesendet!")
                    else:
                        _push_undo_snapshot(settings, "reaction_roles", rr_panels)
                        save_settings(settings)
                        _append_audit_entry("Reaktionsrollen", "Panel gespeichert", panel_name)
                        st.success("Reaktionsrollen-Panel gespeichert.")

        elif page == "Umfragen":
            render_page_header("Umfragen", "Definiere Titel, Farbe und Footer für Poll-Embeds.")
            polls_enabled = st.checkbox("Umfragen aktivieren", value=settings.get("polls_enabled", False))
            poll_send_as_embed = st.checkbox("Nachrichten als Embed senden", value=settings.get("poll_send_as_embed", True))
            poll_embed_title, poll_embed_description, poll_embed_color, poll_embed_footer = render_embed_designer(
                settings,
                "poll_embed",
                "📊 Umfrage",
                "{question}",
                "#8a2be2",
                "Stimme ab!",
                "poll",
            )
            
            if st.button("Umfrage Embed speichern"):
                settings["polls_enabled"] = polls_enabled
                settings["poll_embed_title"] = poll_embed_title
                settings["poll_embed_description"] = poll_embed_description
                settings["poll_embed_color"] = poll_embed_color
                settings["poll_embed_footer"] = poll_embed_footer
                settings["poll_send_as_embed"] = poll_send_as_embed
                save_settings(settings)
                st.success("Umfrage Embed gespeichert!")

        elif page == "Warns/Sanktionen":
            render_page_header("Warns/Sanktionen", "Sanktions-, Warn- und Log-Templates zentral verwalten.")
            
            st.subheader("Sanktionen")
            moderation_enabled = st.checkbox("Moderation aktivieren", value=settings.get("management_enabled", True))
            sanktion_role_id = select_role_id("Sanktions-Rolle", roles_map, settings.get("sanktion_role_id"), "moderation_sanktion_role")
            sanktion_embed_title, sanktion_embed_description, sanktion_embed_color, sanktion_embed_footer = render_embed_designer(
                settings,
                "sanktion_embed",
                "🚫 Sanktion",
                "User: {user}\nBetrag: {betrag}\nGrund: {grund}\nDauer: {dauer} Tage",
                "#ff0000",
                "Sanktion erteilt",
                "sanktion",
            )
            sanktion_send_as_embed = st.checkbox("Sanktions-Nachricht als Embed senden", value=settings.get("sanktion_send_as_embed", True))
            
            st.subheader("Warnungen")
            warn_embed_title, warn_embed_description, warn_embed_color, warn_embed_footer = render_embed_designer(
                settings,
                "warn_embed",
                "⚠️ Warnung",
                "User: {user}\nGrund: {grund}\nDauer: {dauer} Tage",
                "#ffa500",
                "Warnung erteilt",
                "warn",
            )
            warn_send_as_embed = st.checkbox("Warn-Nachricht als Embed senden", value=settings.get("warn_send_as_embed", True))
            
            st.subheader("Logs")
            moderation_log_channel_id = select_channel_id("Moderations-Log-Kanal", channels_map, settings.get("moderation_log_channel"), "moderation_log")
            
            if st.button("Warns/Sanktionen speichern"):
                settings["management_enabled"] = moderation_enabled
                settings["sanktion_role_id"] = sanktion_role_id
                settings["sanktion_embed_title"] = sanktion_embed_title
                settings["sanktion_embed_description"] = sanktion_embed_description
                settings["sanktion_embed_color"] = sanktion_embed_color
                settings["sanktion_embed_footer"] = sanktion_embed_footer
                settings["sanktion_send_as_embed"] = sanktion_send_as_embed
                settings["warn_embed_title"] = warn_embed_title
                settings["warn_embed_description"] = warn_embed_description
                settings["warn_embed_color"] = warn_embed_color
                settings["warn_embed_footer"] = warn_embed_footer
                settings["warn_send_as_embed"] = warn_send_as_embed
                settings["moderation_log_channel"] = moderation_log_channel_id
                save_settings(settings)
                st.success("Warns/Sanktionen gespeichert!")

        elif page == "Logging":
            render_page_header("Protokolle", "Aktiviere Logs und wähle den Ziel-Kanal.")
            logging_enabled = st.checkbox("Protokolle aktivieren", value=settings.get("logging_enabled", True))
            logging_channel_id = select_channel_id("Log-Kanal", channels_map, settings.get("logging_channel_id"), "logging_channel")
            
            if st.button("Protokolle speichern"):
                settings["logging_enabled"] = logging_enabled
                settings["logging_channel_id"] = logging_channel_id
                save_settings(settings)
                st.success("Protokolle gespeichert!")

        elif page == "Einstellungen":
            render_page_header("Allgemeine Einstellungen", "Globale Basiswerte für Kern-Module.")
            active_server_label = st.session_state.get("active_server_label", settings.get("dashboard_server_name", "ASWARD Server"))
            active_server_key = st.session_state.get("active_server_key", "default")
            st.info(f"Aktiver Server-Kontext: {active_server_label}")

            st.subheader("Basis-Einstellungen")
            automod_enabled = st.checkbox("Automod global aktivieren", value=settings.get("automod_enabled", False))
            
            if st.button("Speichern"):
                settings["automod_enabled"] = automod_enabled
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
                    st.success("Zugriffsrechte für den ausgewählten Server gespeichert.")
                    st.rerun()
            else:
                st.write("Freigegebene IDs:")
                st.code("\n".join(current_allowed_ids) if current_allowed_ids else "Keine weiteren Benutzer freigegeben.")
                st.info("Nur die Owner-ID kann Dashboard-Benutzer je Server hinzufügen oder entfernen.")

        elif page == "Audit-Logs":
            render_page_header("Audit-Logs", "Status, Änderungen und Aktionen pro Server nachvollziehen.")
            current_server_key = st.session_state.get("active_server_key", "default")
            only_current_server = st.checkbox("Nur aktuellen Server anzeigen", value=True)
            max_rows = st.slider("Einträge", min_value=20, max_value=300, value=120, step=20)
            entries = _read_audit_entries(current_server_key if only_current_server else None, max_rows)

            status_col1, status_col2, status_col3 = st.columns(3)
            queued = len([e for e in entries if str(e.get("status")) == "queued"])
            sent = len([e for e in entries if str(e.get("status")) == "sent"])
            failed = len([e for e in entries if str(e.get("status")) == "failed"])
            with status_col1:
                st.metric("Queued", str(queued))
            with status_col2:
                st.metric("Sent", str(sent))
            with status_col3:
                st.metric("Failed", str(failed))

            if not entries:
                st.info("Noch keine Audit-Einträge vorhanden.")
            else:
                for idx, item in enumerate(entries):
                    st.markdown(
                        f"<div class='ticket-panel-card'><div class='ticket-panel-head'><span>{item.get('module', '-')}</span>"
                        f"<span class='pill-ok'>{item.get('status', 'ok')}</span></div>"
                        f"<div class='ticket-panel-meta'>{item.get('ts', '-')} | Aktion: {item.get('action', '-')}</div>"
                        f"<div class='ticket-panel-meta'>Server: {item.get('server_label', '-')} | Actor: {item.get('actor_id', '-')}</div>"
                        f"<div class='ticket-panel-meta'>Details: {item.get('details', '-') or '-'}</div></div>",
                        unsafe_allow_html=True,
                    )
                if st.button("Audit-Logs leeren", type="secondary"):
                    with open(AUDIT_LOG_FILE, 'w', encoding='utf-8') as f:
                        json.dump([], f, indent=2, ensure_ascii=False)
                    st.success("Audit-Logs wurden geleert.")
                    st.rerun()

        elif page == "Custom Commands":
            render_page_header("Eigene Befehle", "Lege Trigger fest und definiere, wie der Bot antwortet, inkl. optionalem Ziel-Kanal.")

            custom_enabled = st.checkbox("Eigene Befehle aktivieren", value=settings.get("commands_enabled", True))
            custom_prefix = st.text_input(
                "Prefix für eigene Befehle",
                value=str(settings.get("custom_commands_prefix", settings.get("prefix", "!")) or "!").strip() or "!",
                help="Beispiel: Prefix '/' + Name 'meto' reagiert auf '/meto'.",
            )
            commands_list = settings.get("custom_commands", []) if isinstance(settings.get("custom_commands"), list) else []
            commands_list = [_normalize_custom_command(cmd) for cmd in commands_list]
            settings["custom_commands"] = commands_list
            custom_manager_role_names = st.multiselect(
                "Nur Mitglieder mit diesen Rollen dürfen eigene Befehle ausführen (optional)",
                options=list(roles_map.keys()),
                default=names_for_ids(roles_map, settings.get("custom_commands_manager_roles", [])),
                key="custom_manager_roles",
            )
            custom_manager_roles = [str(roles_map[name]) for name in custom_manager_role_names if name in roles_map]

            if "custom_editor_open" not in st.session_state:
                st.session_state.custom_editor_open = False
            if "custom_selected_index" not in st.session_state:
                st.session_state.custom_selected_index = 0

            if not st.session_state.custom_editor_open:
                st.subheader("Befehls-Übersicht")
                list_col, action_col = st.columns([8, 2])
                with action_col:
                    if st.button("+ Befehl erstellen", key="custom_new"):
                        _push_undo_snapshot(settings, "custom_commands", commands_list)
                        commands_list.append(
                            {
                                "name": f"cmd_{len(commands_list) + 1}",
                                "response": "Hallo {user}",
                                "send_as_embed": True,
                                "target_channel_id": "",
                                "allowed_roles": [],
                            }
                        )
                        settings["custom_commands"] = commands_list
                        settings["custom_commands_prefix"] = custom_prefix
                        settings["commands_enabled"] = custom_enabled
                        settings["custom_commands_manager_roles"] = custom_manager_roles
                        save_settings(settings)
                        _append_audit_entry("Eigene Befehle", "Befehl erstellt", f"Befehle: {len(commands_list)}")
                        st.session_state.custom_selected_index = len(commands_list) - 1
                        st.session_state.custom_editor_open = True
                        st.rerun()
                    delete_marked = st.button("Markierte löschen", key="custom_delete_marked", type="secondary")
                    if st.button("Prefix & Status speichern", key="custom_save_status", use_container_width=True):
                        settings["custom_commands_prefix"] = custom_prefix
                        settings["commands_enabled"] = custom_enabled
                        settings["custom_commands_manager_roles"] = custom_manager_roles
                        save_settings(settings)
                        _append_audit_entry("Eigene Befehle", "Status gespeichert", f"Aktiv: {custom_enabled}")
                        st.success("Eigene Befehle gespeichert.")
                    if st.button("Letzte Änderung rückgängig", key="custom_undo", type="secondary"):
                        restored = _pop_undo_snapshot(settings, "custom_commands")
                        if restored is None:
                            st.warning("Keine rückgängig machbare Änderung vorhanden.")
                        else:
                            settings["custom_commands"] = [_normalize_custom_command(c) for c in restored]
                            save_settings(settings)
                            _append_audit_entry("Eigene Befehle", "Rückgängig", "Letzte Änderung wiederhergestellt")
                            st.success("Letzte Änderung wurde rückgängig gemacht.")
                            st.rerun()

                if delete_marked:
                    filtered = [
                        cmd for i, cmd in enumerate(commands_list)
                        if not st.session_state.get(f"custom_cmd_delete_{i}", False)
                    ]
                    if len(filtered) == len(commands_list):
                        st.warning("Kein Befehl zum Löschen markiert.")
                    else:
                        _push_undo_snapshot(settings, "custom_commands", commands_list)
                        settings["custom_commands"] = filtered
                        settings["custom_commands_prefix"] = custom_prefix
                        settings["commands_enabled"] = custom_enabled
                        settings["custom_commands_manager_roles"] = custom_manager_roles
                        save_settings(settings)
                        _append_audit_entry("Eigene Befehle", "Befehle gelöscht", f"Verbleibend: {len(filtered)}")
                        st.success("Markierte Befehle wurden gelöscht.")
                        st.rerun()

                with list_col:
                    if not commands_list:
                        st.info("Noch keine eigenen Befehle vorhanden.")
                    for idx, cmd in enumerate(commands_list):
                        name = str(cmd.get("name", "")).strip() or f"command_{idx + 1}"
                        response = str(cmd.get("response", "")).strip()
                        send_as_embed = bool(cmd.get("send_as_embed", True))
                        target_channel_id = str(cmd.get("target_channel_id", "") or "").strip()
                        target_channel_hint = f"Ziel-Kanal ID: {target_channel_id}" if target_channel_id else "Ziel-Kanal: aktueller Kanal"
                        row_card_col, row_action_col = st.columns([8, 2])
                        with row_card_col:
                            st.markdown(
                                f"<div class='ticket-panel-card'><div class='ticket-panel-head'><span>{custom_prefix}{name}</span>"
                                f"<span class='pill-ok'>{'Embed' if send_as_embed else 'Text'}</span></div>"
                                f"<div class='ticket-panel-meta'>{target_channel_hint}</div>"
                                f"<div class='ticket-panel-meta'>Antwort: {response[:140] if response else '-'}</div></div>",
                                unsafe_allow_html=True,
                            )
                        with row_action_col:
                            if st.button("Bearbeiten", key=f"custom_edit_{idx}", use_container_width=True):
                                st.session_state.custom_selected_index = idx
                                st.session_state.custom_editor_open = True
                                st.rerun()
                            st.checkbox("Löschen", key=f"custom_cmd_delete_{idx}")
            else:
                if not commands_list:
                    st.session_state.custom_editor_open = False
                    st.rerun()

                selected_idx = min(st.session_state.get("custom_selected_index", 0), len(commands_list) - 1)
                cmd = commands_list[selected_idx]

                back_col, title_col, action_col = st.columns([1, 7, 4])
                with back_col:
                    back_btn = st.button("<", key="custom_back")
                with title_col:
                    st.markdown(f"### Befehl {selected_idx + 1} bearbeiten")
                with action_col:
                    discard_btn = st.button("Verwerfen", key="custom_discard")
                    save_btn = st.button("Speichern", key="custom_save")

                new_name = st.text_input("Name (ohne Prefix)", value=str(cmd.get("name", "")).strip(), key="custom_name")
                new_response = st.text_area("Antwort", value=str(cmd.get("response", "")), key="custom_response")
                new_target_channel_id = select_channel_id(
                    "Ziel-Kanal (optional)",
                    channels_map,
                    cmd.get("target_channel_id", ""),
                    "custom_target",
                )
                new_embed = st.checkbox("Als Embed senden", value=bool(cmd.get("send_as_embed", True)), key="custom_embed")
                allowed_role_names = st.multiselect(
                    "Nur diese Rollen dürfen diesen Befehl ausführen (optional)",
                    options=list(roles_map.keys()),
                    default=names_for_ids(roles_map, cmd.get("allowed_roles", [])),
                    key="custom_allowed_roles",
                )
                allowed_role_ids = [str(roles_map[name]) for name in allowed_role_names if name in roles_map]
                st.caption(f"Trigger-Vorschau: {custom_prefix}{new_name.strip()}")
                st.caption("Antwort-Vorschau")
                st.code(_preview_text(new_response, "#ziel-kanal"), language="text")

                if back_btn or discard_btn:
                    st.session_state.custom_editor_open = False
                    st.rerun()

                if save_btn:
                    candidate = new_name.strip()
                    if not candidate:
                        st.error("Name darf nicht leer sein.")
                    elif any(
                        i != selected_idx and str(c.get("name", "")).strip().lower() == candidate.lower()
                        for i, c in enumerate(commands_list)
                    ):
                        st.error("Ein anderer Befehl mit diesem Namen existiert bereits.")
                    elif not new_response.strip():
                        st.error("Antwort darf nicht leer sein.")
                    else:
                        _push_undo_snapshot(settings, "custom_commands", commands_list)
                        commands_list[selected_idx]["name"] = candidate
                        commands_list[selected_idx]["response"] = new_response
                        commands_list[selected_idx]["send_as_embed"] = bool(new_embed)
                        commands_list[selected_idx]["target_channel_id"] = new_target_channel_id
                        commands_list[selected_idx]["allowed_roles"] = allowed_role_ids
                        settings["custom_commands"] = commands_list
                        settings["custom_commands_prefix"] = custom_prefix
                        settings["commands_enabled"] = custom_enabled
                        settings["custom_commands_manager_roles"] = custom_manager_roles
                        save_settings(settings)
                        _append_audit_entry("Eigene Befehle", "Befehl gespeichert", f"{custom_prefix}{candidate}")
                        st.success("Eigener Befehl gespeichert.")
                        st.session_state.custom_editor_open = False
                        st.rerun()

        elif page == "Embed Hub":
            render_page_header("Embed Hub", "Zentrale Konfiguration fuer alle wichtigen Embed-Vorlagen.")

            with st.expander("Ankündigungs-Embed", expanded=True):
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
