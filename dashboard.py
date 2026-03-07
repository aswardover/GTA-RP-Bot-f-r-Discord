# -*- coding: utf-8 -*-
import streamlit as st
import json
import os
import requests
import discord
from urllib.parse import urlencode
from config import SETTINGS_FILE, DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, DASHBOARD_REDIRECT_URI

# --- KONFIGURATION ---
DISCORD_DATA_FILE = "discord_data.json"
ADMIN_ID = "202768068617699328" # Deine Discord ID

# Discord OAuth2 URLs
DISCORD_AUTH_URL = "https://discord.com/api/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_USER_URL = "https://discord.com/api/users/@me"

# --- STYLING (angepasst an Logo) ---
st.set_page_config(page_title="GTA RP Bot Dashboard", page_icon="🎮", layout="wide")

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
        display: none;
    }
    [data-testid="stToolbar"] {
        display: none;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #10192d 0%, #0e1628 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.25rem;
    }
    [data-testid="stSidebar"] .stRadio label {
        border: 1px solid rgba(255,255,255,0.08);
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
        padding: 0.35rem 0.6rem;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        border-color: rgba(95,124,255,0.45);
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
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

def load_discord_data():
    if os.path.exists(DISCORD_DATA_FILE):
        with open(DISCORD_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"channels": {}, "roles": {}, "categories": {}}

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
        return result
    return {}

def index_for_value(mapping, current_value):
    if not mapping:
        return 0
    values = list(mapping.values())
    for i, val in enumerate(values):
        if str(val) == str(current_value):
            return i
    return 0

def render_page_header(title, subtitle):
    st.markdown(f"<h2 class='section-title'>{title}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p class='section-sub'>{subtitle}</p>", unsafe_allow_html=True)

# --- OAUTH2 HILFSFUNKTIONEN ---
def get_discord_auth_url():
    params = {
        "client_id": DISCORD_CLIENT_ID,
        "redirect_uri": DASHBOARD_REDIRECT_URI,
        "response_type": "code",
        "scope": "identify"
    }
    url = DISCORD_AUTH_URL + "?" + urlencode(params)
    return url

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
    
    auth_url = get_discord_auth_url()
    st.markdown(f'[Mit Discord anmelden]({auth_url})')
    
    # Check for code in query params
    query_params = st.query_params
    code = query_params.get("code")
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
    # Check Admin Status
    is_admin = st.session_state.user_id == ADMIN_ID
    
    if not is_admin:
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
        st.sidebar.markdown("### ASWARD Modules")
        st.sidebar.caption("Steuere alle Bot-Systeme zentral")
        settings = load_settings()
        discord_data = load_discord_data()
        channels_map = normalize_named_mapping(discord_data.get("channels", {}))
        roles_map = normalize_named_mapping(discord_data.get("roles", {}))
        categories_map = normalize_named_mapping(discord_data.get("categories", {}))
        
        # Navigation immer vollständig anzeigen; Aktivierung erfolgt im jeweiligen Reiter.
        page_map = {
            "Overview": "Übersicht",
            "Tickets": "Tickets",
            "Time Clock": "Stempeluhr",
            "Auto Mod": "Automod",
            "If Rules": "Wenn-Funktionen",
            "Giveaway": "Giveaway",
            "Announcements": "Ankündigungen",
            "Reaction Roles": "Reaction Roles",
            "Polls": "Umfragen",
            "Moderation": "Moderation",
            "Logging": "Logging",
            "Settings": "Einstellungen",
        }

        page_choice = st.sidebar.radio("Navigation", list(page_map.keys()))
        page = page_map[page_choice]
        st.sidebar.markdown("<span class='pill-ok'>System Online</span>", unsafe_allow_html=True)
        
        if st.sidebar.button("Abmelden"):
            st.session_state.logged_in = False
            st.rerun()
        
        if page == "Übersicht":
            render_page_header("Bot Übersicht", "Schneller MEE6-Style Überblick über Status und Kernmetriken.")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Status", "Online", delta="Aktiv")
            with col2:
                st.metric("Server", "1", delta="Verbunden")
            with col3:
                st.metric("Tickets", settings.get("ticket_count", 0))
            
            st.markdown("### Letzte Aktivitäten")
            st.markdown('<div class="status-card">Bot erfolgreich gestartet. Alle Systeme laufen nominal.</div>', unsafe_allow_html=True)

        elif page == "Tickets":
            render_page_header("Ticket System", "Panel, Kategorien und Ticket-Aktivierung konfigurieren.")
            tickets_enabled = st.checkbox("Tickets aktivieren", value=settings.get("tickets_enabled", False))
            
            st.subheader("Channel & Kategorien")
            
            # Channel Auswahl
            channel_names = list(channels_map.keys())
            current_ticket_channel = settings.get("tickets_panel_channel_id", settings.get("ticket_channel_id", ""))
            def_idx = index_for_value(channels_map, current_ticket_channel)
            new_channel = st.selectbox("Ticket Panel Channel", options=[""] + channel_names, index=(def_idx + 1) if channel_names else 0)

            category_names = list(categories_map.keys())
            selected_categories = st.multiselect("Ticket Kategorien", options=category_names, default=settings.get("tickets_categories", []))

            if st.button("Ticket Einstellungen speichern"):
                settings["tickets_enabled"] = tickets_enabled
                settings["ticket_channel_id"] = channels_map.get(new_channel) if new_channel else None
                settings["tickets_panel_channel_id"] = channels_map.get(new_channel) if new_channel else None
                settings["tickets_categories"] = selected_categories
                save_settings(settings)
                st.success("Ticket Einstellungen gespeichert!")

            if st.button("Ticket Panel veröffentlichen"):
                settings["tickets_enabled"] = tickets_enabled
                settings["tickets_panel_channel_id"] = channels_map.get(new_channel) if new_channel else settings.get("tickets_panel_channel_id")
                settings["tickets_categories"] = selected_categories
                settings["tickets_publish_trigger"] = True
                save_settings(settings)
                st.success("Ticket Panel wird veröffentlicht.")

        elif page == "Stempeluhr":
            render_page_header("Stempeluhr System", "Berechtigungen und Panel-Channel für die Zeit-Erfassung.")
            stempeluhr_enabled = st.checkbox("Stempeluhr aktivieren", value=settings.get("stempeluhr_enabled", False))
            
            role_names = list(roles_map.keys())
            
            st.subheader("Berechtigungen")
            
            # Multi-Select für Rollen
            selected_ein_roles = st.multiselect("Wer darf /stempel_ein nutzen?", options=role_names)
            selected_aus_roles = st.multiselect("Wer darf /stempel_aus nutzen?", options=role_names)

            channel_names = list(channels_map.keys())
            current_panel_channel = settings.get("stempeluhr_panel_channel_id", "")
            panel_idx = index_for_value(channels_map, current_panel_channel)
            panel_channel = st.selectbox("Stempeluhr Panel Channel", options=[""] + channel_names, index=(panel_idx + 1) if channel_names else 0)
            
            if st.button("Stempel-Berechtigungen speichern"):
                settings["stempeluhr_enabled"] = stempeluhr_enabled
                settings["stempel_ein_roles"] = [roles_map[r] for r in selected_ein_roles]
                settings["stempel_aus_roles"] = [roles_map[r] for r in selected_aus_roles]
                settings["stempeluhr_panel_channel_id"] = channels_map.get(panel_channel) if panel_channel else None
                save_settings(settings)
                st.success("Stempel-Berechtigungen wurden aktualisiert!")

            if st.button("Stempeluhr Panel veröffentlichen"):
                settings["stempeluhr_enabled"] = stempeluhr_enabled
                settings["stempeluhr_panel_channel_id"] = channels_map.get(panel_channel) if panel_channel else settings.get("stempeluhr_panel_channel_id")
                settings["stempeluhr_publish_trigger"] = True
                save_settings(settings)
                st.success("Stempeluhr Panel wird veröffentlicht.")

        elif page == "Automod":
            render_page_header("Automod", "Schütze den Server mit Spam-, Caps- und Wortfiltern.")
            
            automod_enabled = st.checkbox("Automod aktivieren", value=settings.get("automod_enabled", False))
            banned_words = st.text_area("Verbotene Wörter (kommasepariert)", value=", ".join(settings.get("automod_banned_words", [])))
            spam_threshold = st.number_input("Spam-Schwellenwert", value=settings.get("automod_spam_threshold", 5), min_value=1)
            caps_threshold = st.slider("Caps-Schwellenwert", 0.0, 1.0, value=settings.get("automod_caps_threshold", 0.7))
            action = st.selectbox("Aktion bei Verstoß", ["delete", "warn", "mute", "ban"], index=["delete", "warn", "mute", "ban"].index(settings.get("automod_action", "delete")))
            
            caps_enabled = st.checkbox("Caps-Lock Filter aktivieren", value=settings.get("automod_caps_enabled", True))

            channel_names = list(channels_map.keys())
            log_channel = st.selectbox("Log-Channel", options=[""] + channel_names, index=0)
            
            role_names = list(roles_map.keys())
            mute_role = st.selectbox("Mute-Rolle", options=[""] + role_names, index=0)
            
            if st.button("Automod speichern"):
                settings["automod_enabled"] = automod_enabled
                settings["automod_banned_words"] = [w.strip() for w in banned_words.split(",") if w.strip()]
                settings["automod_spam_threshold"] = spam_threshold
                settings["automod_caps_enabled"] = caps_enabled
                settings["automod_caps_threshold"] = caps_threshold
                settings["automod_action"] = action
                settings["automod_log_channel"] = channels_map.get(log_channel) if log_channel else None
                settings["automod_mute_role"] = roles_map.get(mute_role) if mute_role else None
                save_settings(settings)
                st.success("Automod-Einstellungen gespeichert!")

        elif page == "Wenn-Funktionen":
            render_page_header("Wenn-Funktionen", "Eventbasierte Regeln fuer Rollen-Events und Auto-Aktionen.")
            
            custom_rules = settings.get("custom_rules", [])
            
            st.subheader("Neue Regel hinzufügen")
            event = st.selectbox("Event", ["role_add", "role_remove"])
            custom_enabled = st.checkbox("Wenn-Funktionen aktivieren", value=settings.get("custom_rules_enabled", False))
            role_names = list(roles_map.keys())
            selected_role = st.selectbox("Rolle", options=role_names)
            action = st.selectbox("Aktion", ["send_message"])
            channel_names = list(channels_map.keys())
            selected_channel = st.selectbox("Channel", options=channel_names)
            message = st.text_area("Nachricht", placeholder="Verwende {user} und {server}")
            
            if st.button("Regel hinzufügen"):
                settings["custom_rules_enabled"] = custom_enabled
                new_rule = {
                    "event": event,
                    "role": str(roles_map[selected_role]),
                    "action": action,
                    "channel": str(channels_map[selected_channel]),
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
            channel_names = list(channels_map.keys())
            current_announce_channel = settings.get("announce_channel_id", "")
            ann_idx = index_for_value(channels_map, current_announce_channel)
            announce_channel_name = st.selectbox("Ankündigungs-Channel", options=[""] + channel_names, index=(ann_idx + 1) if channel_names else 0)
            
            announce_embed_enabled = st.checkbox("Als Embed senden", value=settings.get("announce_embed_enabled", False))
            if announce_embed_enabled:
                announce_embed_title = st.text_input("Embed Titel", value=settings.get("announce_embed_title", "📢 Ankündigung"))
                announce_embed_description = st.text_area("Embed Beschreibung", value=settings.get("announce_embed_description", "{text}"))
                announce_embed_color = st.text_input("Embed Farbe (Hex)", value=settings.get("announce_embed_color", "#38bdf8"))
                announce_embed_footer = st.text_input("Embed Footer", value=settings.get("announce_embed_footer", "Gesendet von {user}"))
                
                if st.button("Ankündigung Embed speichern"):
                    settings["announce_enabled"] = announce_enabled
                    settings["announce_channel_id"] = channels_map.get(announce_channel_name) if announce_channel_name else settings.get("announce_channel_id")
                    settings["announce_embed_title"] = announce_embed_title
                    settings["announce_embed_description"] = announce_embed_description
                    settings["announce_embed_color"] = announce_embed_color
                    settings["announce_embed_footer"] = announce_embed_footer
                    save_settings(settings)
                    st.success("Ankündigung Embed gespeichert!")
            else:
                if st.button("Einstellung speichern"):
                    settings["announce_enabled"] = announce_enabled
                    settings["announce_channel_id"] = channels_map.get(announce_channel_name) if announce_channel_name else settings.get("announce_channel_id")
                    settings["announce_embed_enabled"] = announce_embed_enabled
                    save_settings(settings)
                    st.success("Gespeichert!")

            if st.button("Ankündigung veröffentlichen"):
                settings["announce_enabled"] = announce_enabled
                settings["announce_channel_id"] = channels_map.get(announce_channel_name) if announce_channel_name else settings.get("announce_channel_id")
                settings["announce_publish_trigger"] = True
                save_settings(settings)
                st.success("Ankündigung wird veröffentlicht.")

        elif page == "Reaction Roles":
            render_page_header("Reaction Roles", "Baue selbsterklaerende Rollen-Panels mit Emoji-Zuordnung.")
            reaction_roles_enabled = st.checkbox("Reaction Roles aktivieren", value=settings.get("reaction_roles_enabled", False))
            rr_data = load_reaction_roles()
            
            st.subheader("Neue Reaction Role Nachricht")
            channel = st.selectbox("Channel", options=[""] + list(channels_map.keys()))
            title = st.text_input("Embed Titel", "Wähle deine Rollen")
            description = st.text_area("Embed Beschreibung", "Reagiere mit Emojis um Rollen zu bekommen.")
            color = st.text_input("Embed Farbe (Hex)", "#8a2be2")
            
            st.subheader("Rollen zuweisen")
            role_names = list(roles_map.keys())
            emoji1 = st.text_input("Emoji 1", "🔴")
            role1 = st.selectbox("Rolle 1", options=[""] + role_names)
            emoji2 = st.text_input("Emoji 2", "🔵")
            role2 = st.selectbox("Rolle 2", options=[""] + role_names)
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
                if channel and title:
                    emoji_role_map = {}
                    if emoji1 and role1:
                        emoji_role_map[emoji1] = str(roles_map[role1])
                    if emoji2 and role2:
                        emoji_role_map[emoji2] = str(roles_map[role2])

                    bot = st.session_state.get("bot")
                    if bot is None:
                        st.error("Bot-Session nicht verfügbar. Nutze den Befehl im Discord oder verbinde den Bot mit dem Dashboard.")
                    else:
                        settings["reaction_roles_enabled"] = reaction_roles_enabled
                        save_settings(settings)
                        ch = int(channels_map[channel])
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
            sanktion_role = st.selectbox("Sanktions-Rolle", options=[""] + list(roles_map.keys()))
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
            log_channel = st.selectbox("Moderation Log Channel", options=[""] + list(channels_map.keys()))
            
            if st.button("Moderation speichern"):
                settings["management_enabled"] = moderation_enabled
                settings["sanktion_role_id"] = roles_map.get(sanktion_role)
                settings["sanktion_embed_title"] = sanktion_embed_title
                settings["sanktion_embed_description"] = sanktion_embed_description
                settings["sanktion_embed_color"] = sanktion_embed_color
                settings["sanktion_embed_footer"] = sanktion_embed_footer
                settings["warn_embed_title"] = warn_embed_title
                settings["warn_embed_description"] = warn_embed_description
                settings["warn_embed_color"] = warn_embed_color
                settings["warn_embed_footer"] = warn_embed_footer
                settings["moderation_log_channel"] = channels_map.get(log_channel)
                save_settings(settings)
                st.success("Moderation gespeichert!")

        elif page == "Logging":
            render_page_header("Logging", "Aktiviere Logging und ordne den Ziel-Channel zu.")
            logging_enabled = st.checkbox("Logging aktivieren", value=settings.get("logging_enabled", True))
            
            logging_channel = st.selectbox("Logging Channel", options=[""] + list(channels_map.keys()))
            
            if st.button("Logging speichern"):
                settings["logging_enabled"] = logging_enabled
                settings["logging_channel_id"] = channels_map.get(logging_channel)
                save_settings(settings)
                st.success("Logging gespeichert!")

        elif page == "Einstellungen":
            render_page_header("Allgemeine Einstellungen", "Globale Basiswerte fuer Prefix und Kern-Module.")
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
