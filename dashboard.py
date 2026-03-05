# -*- coding: utf-8 -*-
import streamlit as st
import json
import os
from PIL import Image

SETTINGS_FILE = 'settings.json'
LOGO_FILE = 'logo.jpg'

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

# Page Config
st.set_page_config(page_title="Asward-Helper Dashboard", layout="wide", page_icon="🎮")

# Custom CSS for Modern Dark UI (Carl-Bot/Mee6 Style)
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    section[data-testid="stSidebar"] { background-color: #1e293b !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] { background-color: #38bdf8 !important; color: white !important; }
    
    /* Card Design */
    .module-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .module-title { font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; display: block; }
    </style>
    """, unsafe_allow_html=True)

if 'settings' not in st.session_state:
    st.session_state.settings = load_settings()

s = st.session_state.settings

# Sidebar
with st.sidebar:
    if os.path.exists(LOGO_FILE):
        st.image(Image.open(LOGO_FILE))
    st.title("Asward-Helper")
    st.markdown("---")
    if st.button("💾 Alle Änderungen speichern", use_container_width=True):
        save_settings(s)
        st.success("Einstellungen gespeichert!")
        st.balloons()

st.title("🎮 Bot Dashboard")

tabs = st.tabs(["🏠 Übersicht", "👋 Willkommen", "⌨️ Befehle", "👔 Management", "🎭 Rollen", "⚙️ System"])

# --- ÜBERSICHT ---
with tabs[0]:
    st.subheader("Modul-Status")
    col1, col2 = st.columns(2)
    with col1:
        s['welcome_enabled'] = st.toggle("Willkommens-System", s.get('welcome_enabled', False))
        s['commands_enabled'] = st.toggle("Custom Commands", s.get('commands_enabled', True))
    with col2:
        s['management_enabled'] = st.toggle("Fraktions-Management", s.get('management_enabled', True))
        s['role_events_enabled'] = st.toggle("Rollen-Automatisierung", s.get('role_events_enabled', False))

# --- WILLKOMMEN ---
with tabs[1]:
    st.header("👋 Willkommen & Abschied")
    if not s.get('welcome_enabled'): st.info("Modul ist in der Übersicht deaktiviert.")
    
    st.subheader("Begrüßung")
    s['welcome_channel_id'] = st.text_input("Willkommens-Kanal (ID)", s.get('welcome_channel_id', ''))
    s['welcome_message'] = st.text_area("Nachricht ({user}, {server}, {name})", s.get('welcome_message', ''))
    
    st.divider()
    
    s['goodbye_enabled'] = st.toggle("Abschied aktivieren", s.get('goodbye_enabled', False))
    s['goodbye_channel_id'] = st.text_input("Abschieds-Kanal (ID)", s.get('goodbye_channel_id', ''))
    s['goodbye_message'] = st.text_area("Abschieds-Nachricht", s.get('goodbye_message', ''))

# --- BEFEHLE ---
with tabs[2]:
    st.header("⌨️ Custom Slash Commands")
    cmds = s.get('custom_commands', [])
    for i, cmd in enumerate(cmds):
        with st.expander(f"Befehl: /{cmd.get('name', 'unbenannt')}"):
            cmd['name'] = st.text_input("Name (kleingeschrieben, ohne Leerzeichen)", cmd.get('name', ''), key=f"cmd_n_{i}")
            cmd['response'] = st.text_area("Antwort", cmd.get('response', ''), key=f"cmd_r_{i}")
            if st.button("🗑️ Löschen", key=f"cmd_d_{i}"):
                cmds.pop(i)
                s['custom_commands'] = cmds
                st.rerun()
    
    if st.button("➕ Neuen Befehl hinzufügen"):
        cmds.append({"name": "neuerbefehl", "response": "Hallo!"})
        s['custom_commands'] = cmds
        st.rerun()

# --- MANAGEMENT ---
with tabs[3]:
    st.header("👔 Fraktions-Management")
    if not s.get('management_enabled'): st.info("Modul ist deaktiviert.")
    
    s['management_log_channel'] = st.text_input("Log-Kanal (ID) für Management-Aktionen", s.get('management_log_channel', ''))
    
    def role_input(label, key, current):
        val = ", ".join(map(str, current)) if isinstance(current, list) else str(current)
        res = st.text_input(label, val, key=key, help="Mehrere IDs mit Komma trennen")
        return [int(x.strip()) for x in res.split(",") if x.strip().isdigit()] if res else []

    st.subheader("Berechtigungen")
    colA, colB = st.columns(2)
    with colA:
        st.markdown("**Einstellen & Kündigen**")
        s['einstellen_enabled'] = st.toggle("Einstellen aktiv", s.get('einstellen_enabled', True))
        s['einstellen_allowed_roles'] = role_input("Rollen für /einstellen", "perm_ein", s.get('einstellen_allowed_roles', []))
        s['kuendigen_enabled'] = st.toggle("Kündigen aktiv", s.get('kuendigen_enabled', True))
        s['kuendigen_allowed_roles'] = role_input("Rollen für /kuendigen", "perm_kue", s.get('kuendigen_allowed_roles', []))
    
    with colB:
        st.markdown("**Befördern & Ranken**")
        s['befoerdern_enabled'] = st.toggle("Befördern aktiv", s.get('befoerdern_enabled', True))
        s['befoerdern_allowed_roles'] = role_input("Rollen für /befoerdern", "perm_bef", s.get('befoerdern_allowed_roles', []))
        s['ranken_enabled'] = st.toggle("Ranken aktiv", s.get('ranken_enabled', True))
        s['ranken_allowed_roles'] = role_input("Rollen für /ranken", "perm_ran", s.get('ranken_allowed_roles', []))

# --- ROLLEN ---
with tabs[4]:
    st.header("🎭 Rollen-Automatisierung")
    rules = s.get('role_event_rules', [])
    for i, rule in enumerate(rules):
        with st.expander(f"Regel: {rule.get('name', 'Neue Regel')}"):
            rule['name'] = st.text_input("Name", rule.get('name', ''), key=f"re_n_{i}")
            rule['trigger_role'] = st.text_input("Wenn diese Rolle vergeben wird (ID)", rule.get('trigger_role', ''), key=f"re_t_{i}")
            rule['action_role'] = st.text_input("Dann gib/nimm diese Rolle (ID)", rule.get('action_role', ''), key=f"re_a_{i}")
            if st.button("🗑️ Regel löschen", key=f"re_d_{i}"):
                rules.pop(i)
                s['role_event_rules'] = rules
                st.rerun()
    
    if st.button("➕ Neue Automatisierung"):
        rules.append({"name": "Neue Regel", "trigger_role": "", "action_role": ""})
        s['role_event_rules'] = rules
        st.rerun()

# --- SYSTEM ---
with tabs[5]:
    st.header("⚙️ Bot Einstellungen")
    s['announce_title'] = st.text_input("Standard-Titel für Ankündigungen", s.get('announce_title', '📢 ANKÜNDIGUNG'))
    s['announce_color'] = st.color_picker("Farbe für Embeds", s.get('announce_color', '#38bdf8'))
    s['announce_allowed_roles'] = role_input("Wer darf /ankuendigung nutzen?", "ann_perms", s.get('announce_allowed_roles', []))

st.session_state.settings = s
