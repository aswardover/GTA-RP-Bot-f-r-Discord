# -*- coding: utf-8 -*-
import streamlit as st
import json
import os
from PIL import Image

SETTINGS_FILE = 'settings.json'
LOGO_FILE = 'logo.jpg'  # Speichere dein Logo unter diesem Namen im Bot-Ordner

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

# Page Config & Design
st.set_page_config(page_title="Asward-Helper Dashboard", layout="wide", page_icon="🎮")

# Custom CSS für das Design (Farben basierend auf Logo: Blau, Lila, Pink)
st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: #1e293b;
        padding: 10px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom-color: #38bdf8 !important;
    }
    div[data-testid="stExpander"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
        color: white;
        border: none;
        border-radius: 5px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        opacity: 0.8;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar mit Logo
with st.sidebar:
    if os.path.exists(LOGO_FILE):
        logo = Image.open(LOGO_FILE)
        st.image(logo, use_container_width=True)
    else:
        st.info("💡 Tipp: Speichere dein Logo als 'logo.jpg' im Ordner, damit es hier erscheint.")
    
    st.title("Asward-Helper")
    st.markdown("---")
    st.info("Steuere deinen GTA RP Bot einfach über dieses Dashboard.")
    if st.button("💾 Alle Änderungen speichern", use_container_width=True):
        save_settings(st.session_state.settings_data)
        st.success("Gespeichert!")

# Hauptinhalt
st.title("🎮 Bot Management Dashboard")
settings = load_settings()

# Session State für Live-Updates
if 'settings_data' not in st.session_state:
    st.session_state.settings_data = settings

sd = st.session_state.settings_data

tab1, tab2, tab3, tab4 = st.tabs(["🏠 Allgemein", "⌨️ Custom Commands", "👔 Fraktion", "🎫 Tickets"])

with tab1:
    st.header("Allgemeine Einstellungen")
    col1, col2 = st.columns(2)
    with col1:
        sd['welcome_message'] = st.text_input("Willkommensnachricht", sd.get('welcome_message', ''))
        sd['welcome_channel_id'] = st.number_input("Willkommens-Kanal ID", value=sd.get('welcome_channel_id', 0), step=1)
    with col2:
        sd['goodbye_enabled'] = st.toggle("Verabschiedung aktivieren", sd.get('goodbye_enabled', False))
        sd['goodbye_channel_id'] = st.number_input("Goodbye-Kanal ID", value=sd.get('goodbye_channel_id', 0), step=1)
    
    st.markdown("---")
    st.subheader("📢 Ankündigungen")
    sd['announce_channel_id'] = st.number_input("Ankündigungs-Kanal ID", value=sd.get('announce_channel_id', 0), step=1)
    sd['announce_title'] = st.text_input("Standard Titel", sd.get('announce_title', '📢 Ankündigung'))

with tab2:
    st.header("Benutzerdefinierte Befehle")
    sd['custom_commands_enabled'] = st.toggle("Befehle aktiv", sd.get('custom_commands_enabled', True))
    
    cmds = sd.get('custom_commands', [])
    for i, cmd in enumerate(cmds):
        with st.expander(f"Befehl: {cmd.get('name', 'Neu')}"):
            c1, c2 = st.columns(2)
            cmd['name'] = c1.text_input(f"Name", cmd.get('name', ''), key=f"cmd_n_{i}")
            cmd['prefix'] = c2.selectbox(f"Prefix", ["!", "/", "?"], index=["!", "/", "?"].index(cmd.get('prefix', '!')), key=f"cmd_p_{i}")
            cmd['response'] = st.text_area(f"Antwort", cmd.get('response', ''), key=f"cmd_r_{i}")
            if st.button(f"Löschen", key=f"cmd_d_{i}"):
                cmds.pop(i)
                st.rerun()
    
    if st.button("➕ Neuen Befehl erstellen"):
        cmds.append({"name": "befehl", "prefix": "!", "response": "Hier die Antwort"})
        sd['custom_commands'] = cmds
        st.rerun()

with tab3:
    st.header("Fraktions & Management")
    st.write("Lege fest, wer die Management-Befehle nutzen darf.")
    
    # Helferfunktion für Rollen-Eingabe (Simulation von Multiselect als Text für IDs)
    def role_input(label, key, current_val):
        val_str = ", ".join(map(str, current_val))
        res = st.text_input(label, val_str, key=key, help="Rollen-IDs mit Komma getrennt eingeben")
        if res:
            return [int(x.strip()) for x in res.split(",") if x.strip().isdigit()]
        return []

    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.subheader("Befördern & Rankup")
        sd['befoerdern_enabled'] = st.toggle("Befördern Aktiv", sd.get('befoerdern_enabled', True))
        sd['befoerdern_allowed_roles'] = role_input("Berechtigte Rollen (IDs)", "bef_roles", sd.get('befoerdern_allowed_roles', []))
        
        sd['rankup_enabled'] = st.toggle("Rankup Aktiv", sd.get('rankup_enabled', True))
        sd['rankup_allowed_roles'] = role_input("Rankup Rollen (IDs)", "rank_roles", sd.get('rankup_allowed_roles', []))

    with m_col2:
        st.subheader("Einstellen & Kündigen")
        sd['einstellen_enabled'] = st.toggle("Einstellen Aktiv", sd.get('einstellen_enabled', True))
        sd['einstellen_allowed_roles'] = role_input("Einstellen Rollen (IDs)", "ein_roles", sd.get('einstellen_allowed_roles', []))
        
        sd['kuendigen_enabled'] = st.toggle("Kündigen Aktiv", sd.get('kuendigen_enabled', True))
        sd['kuendigen_allowed_roles'] = role_input("Kündigen Rollen (IDs)", "kuen_roles", sd.get('kuendigen_allowed_roles', []))

with tab4:
    st.header("Ticket-System")
    sd['tickets_enabled'] = st.toggle("Ticket-System Aktivieren", sd.get('tickets_enabled', False))
    sd['tickets_panel_title'] = st.text_input("Panel Überschrift", sd.get('tickets_panel_title', '🎫 Ticket-System'))
    st.info("Weitere Ticket-Kategorien können direkt in der 'settings.json' definiert werden.")

st.session_state.settings_data = sd
