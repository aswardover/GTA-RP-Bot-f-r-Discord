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
st.set_page_config(page_title="Asward-Helper Dashboard\", layout=\"wide\", page_icon=\"🎮\")

# Advanced Design (Inspired by Carl-Bot & Mee6)
st.markdown(\"\"\"
    <style>
    /* Global Styles */
    .main { background-color: #0f172a; color: #f8fafc; font-family: 'Inter', sans-serif; }
    
    /* Sidebar Styling */
    section[data-testid=\"stSidebar\"] { background-color: #1e293b !important; border-right: 1px solid #334155; }
    .sidebar-status { padding: 10px; border-radius: 8px; background-color: #0f172a; margin-bottom: 20px; border-left: 4px solid #10b981; }
    
    /* Tabs Styling */
    .stTabs [data-baseweb=\"tab-list\"] { gap: 12px; background-color: transparent; padding: 0; }
    .stTabs [data-baseweb=\"tab\"] { 
        background-color: #1e293b; color: #94a3b8; border-radius: 8px 8px 0 0; 
        padding: 10px 20px; font-weight: 600; border: 1px solid #334155; border-bottom: none;
    }
    .stTabs [aria-selected=\"true\"] { background-color: #38bdf8 !important; color: white !important; }

    /* Card Layout (Carl-Bot Style) */
    .module-card {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #334155;
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }
    .module-card:hover {
        border-color: #38bdf8;
        box-shadow: 0 4px 20px rgba(56, 189, 248, 0.1);
        transform: translateY(-2px);
    }
    .module-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    .module-title { font-size: 1.25rem; font-weight: 700; color: #f8fafc; }
    .module-desc { color: #94a3b8; font-size: 0.9rem; line-height: 1.5; }
    
    /* Button Styling */
    .stButton>button { 
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%); 
        color: white; border: none; border-radius: 8px; font-weight: 700; 
        padding: 12px 24px; width: 100%; transition: opacity 0.2s;
    }
    .stButton>button:hover { opacity: 0.9; color: white; }
    
    /* Form Elements */
    .stTextInput input, .stTextArea textarea { background-color: #0f172a !important; color: #f8fafc !important; border: 1px solid #334155 !important; border-radius: 8px !important; }
    </style>
    \"\"\", unsafe_allow_html=True)

settings = load_settings()
if 'settings_data' not in st.session_state:
    st.session_state.settings_data = settings

sd = st.session_state.settings_data

# Sidebar
with st.sidebar:
    if os.path.exists(LOGO_FILE):
        st.image(Image.open(LOGO_FILE), use_container_width=True)
    
    st.markdown('<div class="sidebar-status">🟢 Bot Status: Online<br><small>Verbunden mit Discord</small></div>', unsafe_allow_html=True)
    
    st.title(\"Asward-Helper\")
    st.caption(\"GTA-RP Management Suite\")
    
    st.markdown(\"---\")
    if st.button(\"💾 Alle Änderungen speichern\"):
        # ID Conversion Logic
        def safe_int_convert(data, keys):
            for k in keys:
                if k in data and isinstance(data[k], str) and data[k].strip().isdigit():
                    data[k] = int(data[k].strip())
        
        safe_int_convert(sd, ['welcome_channel_id', 'announce_channel_id', 'goodbye_channel_id'])
        if 'role_event_rules' in sd:
            for rule in sd['role_event_rules']:
                for key in ['trigger_role', 'action_role', 'channel_id']:
                    if isinstance(rule.get(key), str) and rule[key].isdigit():
                        rule[key] = int(rule[key])

        save_settings(sd)
        st.success(\"Erfolgreich gespeichert!\")
        st.balloons()

st.title(\"🎮 Dashboard\")

# Main Tabs
tab_index, tab1, tab2, tab3, tab4, tab5 = st.tabs([\"🏠 Übersicht\", \"👋 Willkommen\", \"⌨️ Befehle\", \"👔 Management\", \"🎫 Tickets\", \"🎭 Rollen\"])

# Overview with Module Cards (Mee6/Carl-Bot Style)
with tab_index:
    st.subheader(\"🔌 Deine Module\")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class=\"module-card\"><div class=\"module-header\"><span class=\"module-title\">👋 Willkommen</span></div><p class=\"module-desc\">Begrüße neue Spieler automatisch auf dem Server.</p></div>', unsafe_allow_html=True)
        sd['welcome_enabled'] = st.toggle(\"Modul Aktivieren\", sd.get('welcome_enabled', False), key=\"tog_welcome\")
        
        st.markdown('<div class=\"module-card\"><div class=\"module-header\"><span class=\"module-title\">👔 Management</span></div><p class=\"module-desc\">Beförderungen, Einstellungen und Fraktions-Verwaltung.</p></div>', unsafe_allow_html=True)
        sd['management_enabled'] = st.toggle(\"Modul Aktivieren\", sd.get('management_enabled', True), key=\"tog_mgmt\")

    with col2:
        st.markdown('<div class=\"module-card\"><div class=\"module-header\"><span class=\"module-title\">⌨️ Befehle</span></div><p class=\"module-desc\">Verwalte deine Custom Slash-Commands und Antworten.</p></div>', unsafe_allow_html=True)
        sd['commands_enabled'] = st.toggle(\"Modul Aktivieren\", sd.get('commands_enabled', True), key=\"tog_cmds\")
        
        st.markdown('<div class=\"module-card\"><div class=\"module-header\"><span class=\"module-title\">🎭 Rollen-Events</span></div><p class=\"module-desc\">Automatisierung basierend auf Rollen-Änderungen.</p></div>', unsafe_allow_html=True)
        sd['role_events_enabled'] = st.toggle(\"Modul Aktivieren\", sd.get('role_events_enabled', False), key=\"tog_roles\")

# Sub-Pages (Old Content with improved styling)
with tab1:
    st.header(\"👋 Willkommens-System\")
    if not sd.get('welcome_enabled'): st.warning(\"Dieses Modul ist deaktiviert.\")
    sd['welcome_message'] = st.text_area(\"Nachricht (Platzhalter: {user}, {server})\", sd.get('welcome_message', ''))
    sd['welcome_channel_id'] = st.text_input(\"Kanal ID\", value=str(sd.get('welcome_channel_id', '')))

with tab2:
    st.header(\"⌨️ Custom Commands\")
    if not sd.get('commands_enabled'): st.warning(\"Dieses Modul ist deaktiviert.\")
    cmds = sd.get('custom_commands', [])
    for i, cmd in enumerate(cmds):
        with st.expander(f\"Befehl: {cmd.get('name', 'Neu')}\"):
            cmd['name'] = st.text_input(f\"Name\", cmd.get('name', ''), key=f\"n_{i}\")
            cmd['response'] = st.text_area(f\"Antwort\", cmd.get('response', ''), key=f\"r_{i}\")
            if st.button(\"🗑️ Löschen\", key=f\"d_{i}\"):
                cmds.pop(i); st.rerun()
    if st.button(\"➕ Neuer Befehl\"):
        cmds.append({\"name\": \"befehl\", \"response\": \"Text\"}); sd['custom_commands'] = cmds; st.rerun()

with tab3:
    st.header(\"👔 Management\")
    if not sd.get('management_enabled'): st.warning(\"Dieses Modul ist deaktiviert.\")Modernize dashboard design (Carl-bot/Mee6 style) with Module Index and Custom CSS
    def role_list_input(label, current, key):
        val = \", \".join(map(str, current)) if isinstance(current, list) else str(current)
        res = st.text_input(label, val, key=key)
        return [int(x.strip()) for x in res.split(\",\") if x.strip().isdigit()] if res else []
    
    sd['befoerdern_allowed_roles'] = role_list_input(\"Wer darf befördern? (IDs)\", sd.get('befoerdern_allowed_roles', []), \"b_roles\")
    sd['rankup_allowed_roles'] = role_list_input(\"Wer darf Rankup? (IDs)\", sd.get('rankup_allowed_roles', []), \"r_roles\")

with tab4:
    st.header(\"🎫 Ticket System\")
    sd['tickets_enabled'] = st.toggle(\"Ticket Modul Aktiv\", sd.get('tickets_enabled', False))
    sd['tickets_panel_title'] = st.text_input(\"Panel Titel\", sd.get('tickets_panel_title', '🎫 Ticket-System'))

with tab5:
    st.header(\"🎭 Rollen-Automatisierung\")
    if not sd.get('role_events_enabled'): st.warning(\"Dieses Modul ist deaktiviert.\")
    rules = sd.get('role_event_rules', [])
    for i, rule in enumerate(rules):
        with st.expander(f\"Regel {i+1}: {rule.get('name', 'Regel')}\"):
            rule['name'] = st.text_input(\"Bezeichnung\", rule.get('name', ''), key=f\"re_n_{i}\")
            rule['trigger_role'] = st.text_input(\"Trigger-Rolle (ID)\", value=str(rule.get('trigger_role', '')), key=f\"re_t_{i}\")
            rule['event_type'] = st.selectbox(\"Event\", [\"Hinzugefügt\", \"Entfernt\"], key=f\"re_e_{i}\")
            rule['message'] = st.text_area(\"Nachricht (Optional)\", rule.get('message', ''), key=f\"re_m_{i}\")
            rule['channel_id'] = st.text_input(\"Kanal ID\", value=str(rule.get('channel_id', '')), key=f\"re_c_{i}\")
            rule['action_role'] = st.text_input(\"Rolle geben/nehmen (ID)\", value=str(rule.get('action_role', '')), key=f\"re_a_{i}\")
            if st.button(\"🗑️ Regel entfernen\", key=f\"re_d_{i}\"):
                rules.pop(i); st.rerun()
    if st.button(\"➕ Neue Regel\"):
        rules.append({\"name\": \"Neue Regel\"}); sd['role_event_rules'] = rules; st.rerun()

st.session_state.settings_data = sd
