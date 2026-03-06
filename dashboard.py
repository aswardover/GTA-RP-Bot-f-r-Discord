# -*- coding: utf-8 -*-
import streamlit as st
import json
import os
import requests
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
    .main {
        background-color: #0f0f0f;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #8a2be2;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #6a1cb0;
        border: none;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #1a1a1a;
        color: white;
        border: 1px solid #333333;
    }
    .sidebar .sidebar-content {
        background-color: #1a1a1a;
    }
    div[data-testid="stMetricValue"] {
        color: #8a2be2;
    }
    .status-card {
        background-color: #1a1a1a;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #8a2be2;
        margin-bottom: 10px;
    }
    .logo {
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_index=True)

# --- LOGO ---
st.markdown('<div class="logo"><img src="https://cdn.discordapp.com/attachments/1317606543952183367/1479593240884805794/oVer.png?ex=69ac9a16&is=69ab4896&hm=e46c698ec82f7ab40b02d1b266cb4d9a69d94d8b3831122b31e46a87c84d8f3e&" width="200"></div>', unsafe_allow_index=True)

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

# --- OAUTH2 HILFSFUNKTIONEN ---
def get_discord_auth_url():
    params = {
        "client_id": DISCORD_CLIENT_ID,
        "redirect_uri": DASHBOARD_REDIRECT_URI,
        "response_type": "code",
        "scope": "identify"
    }
    url = DISCORD_AUTH_URL + "?" + "&".join([f"{k}={v}" for k, v in params.items()])
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
    st.title("🔒 Dashboard Login")
    
    st.info("Logge dich mit deinem Discord Account ein.")
    
    auth_url = get_discord_auth_url()
    st.markdown(f'[Mit Discord anmelden]({auth_url})', unsafe_allow_index=True)
    
    # Check for code in query params
    query_params = st.experimental_get_query_params()
    if "code" in query_params:
        code = query_params["code"][0]
        token_data = exchange_code_for_token(code)
        if "access_token" in token_data:
            st.session_state.access_token = token_data["access_token"]
            user_info = get_user_info(st.session_state.access_token)
            if "id" in user_info:
                st.session_state.user_id = user_info["id"]
                st.session_state.logged_in = True
                st.experimental_set_query_params()  # Clear params
                st.rerun()
        else:
            st.error("Fehler beim Anmelden. Versuche es erneut.")

# --- HAUPTTEIL ---
if not st.session_state.logged_in:
    login_form()
else:
    # Check Admin Status
    is_admin = st.session_state.user_id == ADMIN_ID
    
    if not is_admin:
        st.title("🚧 Zugriff verweigert")
        st.error("Du kannst aktuell nicht auf diese Seite zugreifen")
        st.info(f"Eingeloggt als: {st.session_state.user_id}")
        if st.button("Abmelden"):
            st.session_state.logged_in = False
            st.session_state.access_token = None
            st.session_state.user_id = None
            st.rerun()
    else:
        # ADMIN DASHBOARD
        st.sidebar.title("🎮 Bot Control Panel")
        
        # Dynamische Navigation basierend auf enabled-Status
        pages = ["Übersicht"]
        if settings.get("tickets_enabled", False):
            pages.append("Tickets")
        if settings.get("stempeluhr_enabled", False):
            pages.append("Stempeluhr")
        if settings.get("automod_enabled", False):
            pages.append("Automod")
        if settings.get("custom_rules_enabled", False):
            pages.append("Wenn-Funktionen")
        if settings.get("giveaway_enabled", False):
            pages.append("Giveaway")
        pages.append("Ankündigungen")  # Immer verfügbar für Embed-Konfiguration
        if settings.get("reaction_roles_enabled", False):
            pages.append("Reaction Roles")
        if settings.get("polls_enabled", False):
            pages.append("Umfragen")
        pages.append("Moderation")  # Immer verfügbar
        pages.append("Logging")  # Immer verfügbar
        pages.append("Einstellungen")  # Immer verfügbar
        
        page = st.sidebar.radio("Navigation", pages)
        
        if st.sidebar.button("Abmelden"):
            st.session_state.logged_in = False
            st.rerun()

        settings = load_settings()
        discord_data = load_discord_data()
        
        if page == "Übersicht":
            st.title("📊 Bot Übersicht")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Status", "Online", delta="Aktiv")
            with col2:
                st.metric("Server", "1", delta="Verbunden")
            with col3:
                st.metric("Tickets", settings.get("ticket_count", 0))
            
            st.markdown("### 🔔 Letzte Aktivitäten")
            st.markdown('<div class="status-card">Bot erfolgreich gestartet. Alle Systeme laufen nominal.</div>', unsafe_allow_index=True)

        elif page == "Tickets":
            st.title("🎫 Ticket System")
            st.write("Konfiguriere hier die Ticket-Einstellungen.")
            
            channels = discord_data.get("channels", {})
            categories = discord_data.get("categories", {})
            
            st.subheader("Channel & Kategorien")
            
            # Channel Auswahl
            channel_names = list(channels.keys())
            current_ticket_channel = settings.get("ticket_channel_id", "")
            
            # Suche Index für Default
            def_idx = 0
            for i, cid in enumerate(channels.values()):
                if str(cid) == str(current_ticket_channel):
                    def_idx = i
                    break
            
            new_channel = st.selectbox("Ticket Log Channel", options=channel_names, index=def_idx if channel_names else 0)
            if new_channel:
                settings["ticket_channel_id"] = channels[new_channel]
                
            if st.button("Einstellungen speichern"):
                save_settings(settings)
                st.success("Ticket Einstellungen gespeichert!")

        elif page == "Stempeluhr":
            st.title("🕐 Stempeluhr System")
            st.write("Berechtigungen und Logs für die Stempeluhr.")
            
            roles = discord_data.get("roles", {})
            role_names = list(roles.keys())
            
            st.subheader("Berechtigungen")
            
            # Multi-Select für Rollen
            selected_ein_roles = st.multiselect("Wer darf /stempel_ein nutzen?", options=role_names)
            selected_aus_roles = st.multiselect("Wer darf /stempel_aus nutzen?", options=role_names)
            
            if st.button("Stempel-Berechtigungen speichern"):
                settings["stempel_ein_roles"] = [roles[r] for r in selected_ein_roles]
                settings["stempel_aus_roles"] = [roles[r] for r in selected_aus_roles]
                save_settings(settings)
                st.success("Stempel-Berechtigungen wurden aktualisiert!")

        elif page == "Automod":
            st.title("🤖 Automod System")
            st.write("Konfiguriere automatische Moderation.")
            
            automod_enabled = st.checkbox("Automod aktivieren", value=settings.get("automod_enabled", False))
            banned_words = st.text_area("Verbotene Wörter (kommasepariert)", value=", ".join(settings.get("automod_banned_words", [])))
            spam_threshold = st.number_input("Spam-Schwellenwert", value=settings.get("automod_spam_threshold", 5), min_value=1)
            caps_threshold = st.slider("Caps-Schwellenwert", 0.0, 1.0, value=settings.get("automod_caps_threshold", 0.7))
            action = st.selectbox("Aktion bei Verstoß", ["delete", "warn", "mute", "ban"], index=["delete", "warn", "mute", "ban"].index(settings.get("automod_action", "delete")))
            
            channels = discord_data.get("channels", {})
            channel_names = list(channels.keys())
            log_channel = st.selectbox("Log-Channel", options=[""] + channel_names, index=0)
            
            roles = discord_data.get("roles", {})
            role_names = list(roles.keys())
            mute_role = st.selectbox("Mute-Rolle", options=[""] + role_names, index=0)
            
            if st.button("Automod speichern"):
                settings["automod_enabled"] = automod_enabled
                settings["automod_banned_words"] = [w.strip() for w in banned_words.split(",") if w.strip()]
                settings["automod_spam_threshold"] = spam_threshold
                settings["automod_caps_threshold"] = caps_threshold
                settings["automod_action"] = action
                settings["automod_log_channel"] = channels.get(log_channel) if log_channel else None
                settings["automod_mute_role"] = roles.get(mute_role) if mute_role else None
                save_settings(settings)
                st.success("Automod-Einstellungen gespeichert!")

        elif page == "Wenn-Funktionen":
            st.title("🔀 Wenn-Funktionen")
            st.write("Definiere bedingte Aktionen, z.B. bei Rollenänderungen.")
            
            custom_rules = settings.get("custom_rules", [])
            
            st.subheader("Neue Regel hinzufügen")
            event = st.selectbox("Event", ["role_add", "role_remove"])
            roles = discord_data.get("roles", {})
            role_names = list(roles.keys())
            selected_role = st.selectbox("Rolle", options=role_names)
            action = st.selectbox("Aktion", ["send_message"])
            channels = discord_data.get("channels", {})
            channel_names = list(channels.keys())
            selected_channel = st.selectbox("Channel", options=channel_names)
            message = st.text_area("Nachricht", placeholder="Verwende {user} und {server}")
            
            if st.button("Regel hinzufügen"):
                new_rule = {
                    "event": event,
                    "role": str(roles[selected_role]),
                    "action": action,
                    "channel": str(channels[selected_channel]),
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
            st.title("🎉 Giveaway System")
            st.write("Konfiguriere das Embed für Giveaways.")
            
            giveaway_embed_title = st.text_input("Embed Titel", value=settings.get("giveaway_embed_title", "🎉 Giveaway!"))
            giveaway_embed_description = st.text_area("Embed Beschreibung", value=settings.get("giveaway_embed_description", "Gegenstand: {item}\nEndet in: {time}"))
            giveaway_embed_color = st.text_input("Embed Farbe (Hex)", value=settings.get("giveaway_embed_color", "#ff4500"))
            giveaway_embed_footer = st.text_input("Embed Footer", value=settings.get("giveaway_embed_footer", "Klicke auf Teilnehmen!"))
            
            if st.button("Giveaway Embed speichern"):
                settings["giveaway_embed_title"] = giveaway_embed_title
                settings["giveaway_embed_description"] = giveaway_embed_description
                settings["giveaway_embed_color"] = giveaway_embed_color
                settings["giveaway_embed_footer"] = giveaway_embed_footer
                save_settings(settings)
                st.success("Giveaway Embed gespeichert!")

        elif page == "Ankündigungen":
            st.title("📢 Ankündigungen")
            st.write("Konfiguriere Embed für /ankündigen.")
            
            announce_embed_enabled = st.checkbox("Als Embed senden", value=settings.get("announce_embed_enabled", False))
            if announce_embed_enabled:
                announce_embed_title = st.text_input("Embed Titel", value=settings.get("announce_embed_title", "📢 Ankündigung"))
                announce_embed_description = st.text_area("Embed Beschreibung", value=settings.get("announce_embed_description", "{text}"))
                announce_embed_color = st.text_input("Embed Farbe (Hex)", value=settings.get("announce_embed_color", "#38bdf8"))
                announce_embed_footer = st.text_input("Embed Footer", value=settings.get("announce_embed_footer", "Gesendet von {user}"))
                
                if st.button("Ankündigung Embed speichern"):
                    settings["announce_embed_title"] = announce_embed_title
                    settings["announce_embed_description"] = announce_embed_description
                    settings["announce_embed_color"] = announce_embed_color
                    settings["announce_embed_footer"] = announce_embed_footer
                    save_settings(settings)
                    st.success("Ankündigung Embed gespeichert!")
            else:
                if st.button("Einstellung speichern"):
                    settings["announce_embed_enabled"] = announce_embed_enabled
                    save_settings(settings)
                    st.success("Gespeichert!")

        elif page == "Reaction Roles":
            st.title("🔄 Reaction Roles")
            st.write("Erstelle Reaction Role Messages.")
            
            st.subheader("Neue Reaction Role Nachricht")
            channel = st.selectbox("Channel", options=[""] + list(discord_data.get("channels", {}).keys()))
            title = st.text_input("Embed Titel", "Wähle deine Rollen")
            description = st.text_area("Embed Beschreibung", "Reagiere mit Emojis um Rollen zu bekommen.")
            color = st.text_input("Embed Farbe (Hex)", "#8a2be2")
            
            st.subheader("Rollen zuweisen")
            roles = discord_data.get("roles", {})
            role_names = list(roles.keys())
            emoji1 = st.text_input("Emoji 1", "🔴")
            role1 = st.selectbox("Rolle 1", options=[""] + role_names)
            emoji2 = st.text_input("Emoji 2", "🔵")
            role2 = st.selectbox("Rolle 2", options=[""] + role_names)
            # Mehr können hinzugefügt werden
            
            if st.button("Reaction Role Nachricht senden"):
                if channel and title:
                    ch = discord_data["channels"][channel]
                    embed = discord.Embed(title=title, description=description, color=int(color.lstrip("#"), 16))
                    message = await st.session_state.bot.get_channel(int(ch)).send(embed=embed)
                    # Reaktionen hinzufügen
                    if emoji1 and role1:
                        await message.add_reaction(emoji1)
                    if emoji2 and role2:
                        await message.add_reaction(emoji2)
                    # Speichere in DB
                    from database import add_reaction_role
                    await add_reaction_role(str(message.id), json.dumps(rr_data[str(message.id)]))
                    st.success("Reaction Role Nachricht gesendet!")
                else:
                    st.error("Channel und Titel erforderlich!")

        elif page == "Umfragen":
            st.title("📊 Umfragen")
            st.write("Konfiguriere Embed für /poll.")
            
            poll_embed_title = st.text_input("Embed Titel", value=settings.get("poll_embed_title", "📊 Umfrage"))
            poll_embed_color = st.text_input("Embed Farbe (Hex)", value=settings.get("poll_embed_color", "#8a2be2"))
            poll_embed_footer = st.text_input("Embed Footer", value=settings.get("poll_embed_footer", "Stimme ab!"))
            
            if st.button("Umfrage Embed speichern"):
                settings["poll_embed_title"] = poll_embed_title
                settings["poll_embed_color"] = poll_embed_color
                settings["poll_embed_footer"] = poll_embed_footer
                save_settings(settings)
                st.success("Umfrage Embed gespeichert!")

        elif page == "Moderation":
            st.title("🛡️ Moderation")
            st.write("Konfiguriere Sanktionen, Warnungen und Logs.")
            
            st.subheader("Sanktionen")
            sanktion_role = st.selectbox("Sanktions-Rolle", options=[""] + list(discord_data.get("roles", {}).keys()))
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
            log_channel = st.selectbox("Moderation Log Channel", options=[""] + list(discord_data.get("channels", {}).keys()))
            
            if st.button("Moderation speichern"):
                settings["sanktion_role_id"] = discord_data.get("roles", {}).get(sanktion_role)
                settings["sanktion_embed_title"] = sanktion_embed_title
                settings["sanktion_embed_description"] = sanktion_embed_description
                settings["sanktion_embed_color"] = sanktion_embed_color
                settings["sanktion_embed_footer"] = sanktion_embed_footer
                settings["warn_embed_title"] = warn_embed_title
                settings["warn_embed_description"] = warn_embed_description
                settings["warn_embed_color"] = warn_embed_color
                settings["warn_embed_footer"] = warn_embed_footer
                settings["moderation_log_channel"] = discord_data.get("channels", {}).get(log_channel)
                save_settings(settings)
                st.success("Moderation gespeichert!")

        elif page == "Logging":
            st.title("📝 Logging")
            st.write("Konfiguriere erweiterte Logs.")
            
            logging_channel = st.selectbox("Logging Channel", options=[""] + list(discord_data.get("channels", {}).keys()))
            
            if st.button("Logging speichern"):
                settings["logging_channel_id"] = discord_data.get("channels", {}).get(logging_channel)
                save_settings(settings)
                st.success("Logging gespeichert!")

        elif page == "Einstellungen":
            st.title("⚙️ Allgemeine Einstellungen")
            
            st.subheader("Funktionen aktivieren/deaktivieren")
            tickets_enabled = st.checkbox("Tickets aktivieren", value=settings.get("tickets_enabled", False))
            stempeluhr_enabled = st.checkbox("Stempeluhr aktivieren", value=settings.get("stempeluhr_enabled", False))
            automod_enabled = st.checkbox("Automod aktivieren", value=settings.get("automod_enabled", False))
            custom_rules_enabled = st.checkbox("Wenn-Funktionen aktivieren", value=settings.get("custom_rules_enabled", False))
            giveaway_enabled = st.checkbox("Giveaway aktivieren", value=settings.get("giveaway_enabled", False))
            reaction_roles_enabled = st.checkbox("Reaction Roles aktivieren", value=settings.get("reaction_roles_enabled", False))
            polls_enabled = st.checkbox("Umfragen aktivieren", value=settings.get("polls_enabled", False))
            
            st.subheader("Sonstige Einstellungen")
            bot_prefix = st.text_input("Bot Prefix", value=settings.get("prefix", "!"))
            
            if st.button("Speichern"):
                settings["tickets_enabled"] = tickets_enabled
                settings["stempeluhr_enabled"] = stempeluhr_enabled
                settings["automod_enabled"] = automod_enabled
                settings["custom_rules_enabled"] = custom_rules_enabled
                settings["giveaway_enabled"] = giveaway_enabled
                settings["reaction_roles_enabled"] = reaction_roles_enabled
                settings["polls_enabled"] = polls_enabled
                settings["prefix"] = bot_prefix
                save_settings(settings)
                st.success("Einstellungen gespeichert!")
                st.rerun()  # Seite neu laden, um Navigation zu aktualisieren
