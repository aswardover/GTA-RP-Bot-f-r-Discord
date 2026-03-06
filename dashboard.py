# -*- coding: utf-8 -*-
import streamlit as st
import json
import os
import requests
from config import SETTINGS_FILE

# --- KONFIGURATION ---
DISCORD_DATA_FILE = "discord_data.json"
ADMIN_ID = "202768068617699328" # Deine Discord ID

# --- STYLING (MEE6 LOOK) ---
st.set_page_config(page_title="GTA RP Bot Dashboard", page_icon="🎮", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #1a1c1e;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #5865f2;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #4752c4;
        border: none;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #2f3136;
        color: white;
        border: 1px solid #4f545c;
    }
    .sidebar .sidebar-content {
        background-color: #23272a;
    }
    div[data-testid="stMetricValue"] {
        color: #5865f2;
    }
    .status-card {
        background-color: #2f3136;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #5865f2;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_index=True)

# --- HILFSFUNKTIONEN ---
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

# --- LOGIN LOGIK ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None

def login_form():
    st.title("🔒 Dashboard Login")
    
    tab1, tab2 = st.tabs(["Discord Login (Simuliert)", "Passwort Login"])
    
    with tab1:
        st.info("Logge dich mit deinem Discord Account ein.")
        discord_id_input = st.text_input("Discord User ID eingeben (für Demo)", placeholder="Deine ID...")
        if st.button("Mit Discord anmelden"):
            if discord_id_input:
                st.session_state.logged_in = True
                st.session_state.user_id = discord_id_input
                st.rerun()
            else:
                st.error("Bitte gib eine ID ein!")
                
    with tab2:
        password = st.text_input("Admin Passwort", type="password")
        if st.button("Anmelden"):
            if password == "GTA2026": # Standardpasswort
                st.session_state.logged_in = True
                st.session_state.user_id = ADMIN_ID # Passwort Login gibt Admin Rechte
                st.rerun()
            else:
                st.error("Falsches Passwort!")

# --- HAUPTTEIL ---
if not st.session_state.logged_in:
    login_form()
else:
    # Check Admin Status
    is_admin = st.session_state.user_id == ADMIN_ID
    
    if not is_admin:
        st.title("🚧 Zugriff eingeschränkt")
        st.warning("Das Dashboard ist noch in Bearbeitung")
        st.info(f"Eingeloggt als: {st.session_state.user_id}")
        if st.button("Abmelden"):
            st.session_state.logged_in = False
            st.rerun()
    else:
        # ADMIN DASHBOARD
        st.sidebar.title("🎮 Bot Control Panel")
        page = st.sidebar.radio("Navigation", ["Übersicht", "Tickets", "Stempeluhr", "Einstellungen"])
        
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

        elif page == "Einstellungen":
            st.title("⚙️ Allgemeine Einstellungen")
            bot_prefix = st.text_input("Bot Prefix", value=settings.get("prefix", "!"))
            if st.button("Speichern"):
                settings["prefix"] = bot_prefix
                save_settings(settings)
                st.success("Einstellungen gespeichert!")
