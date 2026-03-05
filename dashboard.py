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

# Design
st.markdown(\"\"\"
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stTabs [data-baseweb=\"tab-list\"] { gap: 24px; background-color: #1e293b; padding: 10px; border-radius: 10px; }
    .stTabs [data-baseweb=\"tab\"] { color: #94a3b8; font-weight: 600; }
    .stTabs [aria-selected=\"true\"] { color: #38bdf8 !important; border-bottom-color: #38bdf8 !important; }
    div[data-testid=\"stExpander\"] { background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; }
    .stButton>button { background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%); color: white; border: none; border-radius: 5px; font-weight: bold; }
    </style>
    \"\"\", unsafe_allow_html=True)

settings = load_settings()
if 'settings_data' not in st.session_state:
    st.session_state.settings_data = settings

sd = st.session_state.settings_data

with st.sidebar:
    if os.path.exists(LOGO_FILE):
        st.image(Image.open(LOGO_FILE), use_container_width=True)
    st.title(\"Asward-Helper\")
    
    if st.button(\"💾 Speichern\", use_container_width=True):
        # Konvertiere Text-IDs zurück in Zahlen beim Speichern
        def safe_int_convert(data, keys):
            for k in keys:
                if k in data and isinstance(data[k], str) and data[k].strip().isdigit():
                    data[k] = int(data[k].strip())
        
        safe_int_convert(sd, ['welcome_channel_id', 'announce_channel_id', 'goodbye_channel_id'])
        
        # Konvertiere IDs in den Regeln
        if 'role_event_rules' in sd:
            for rule in sd['role_event_rules']:
                if isinstance(rule.get('trigger_role'), str) and rule['trigger_role'].isdigit():
                    rule['trigger_role'] = int(rule['trigger_role'])
                if isinstance(rule.get('action_role'), str) and rule['action_role'].isdigit():
                    rule['action_role'] = int(rule['action_role'])
                if isinstance(rule.get('channel_id'), str) and rule['channel_id'].isdigit():
                    rule['channel_id'] = int(rule['channel_id'])

        save_settings(sd)
        st.success(\"Gespeichert!\")

st.title(\"🎮 Bot Management\")

tab1, tab2, tab3, tab4, tab5 = st.tabs([\"🏠 Allgemein\", \"⌨️ Befehle\", \"👔 Management\", \"🎫 Tickets\", \"🎭 Rollen-Events\"])

with tab1:
    st.header(\"Allgemeine Einstellungen\")
    
    st.subheader(\"👋 Willkommen\")
    sd['welcome_enabled'] = st.toggle(\"Willkommens-Nachricht Aktiv\", sd.get('welcome_enabled', False))
    sd['welcome_message'] = st.text_input(\"Willkommensnachricht\", sd.get('welcome_message', ''))
    w_cid = st.text_input(\"Willkommens-Kanal ID\", value=str(sd.get('welcome_channel_id', '')))
    sd['welcome_channel_id'] = w_cid
    
    st.markdown(\"---\")
    
    st.subheader(\"📢 Ankündigungen\")
    sd['announce_enabled'] = st.toggle(\"Ankündigungen Aktiv\", sd.get('announce_enabled', True))
    a_cid = st.text_input(\"Ankündigungs-Kanal ID\", value=str(sd.get('announce_channel_id', '')))
    sd['announce_channel_id'] = a_cid
    sd['announce_title'] = st.text_input(\"Standard Titel\", sd.get('announce_title', '📢 Ankündigung'))

with tab2:
    st.header(\"⌨️ Custom Commands\")
    sd['commands_enabled'] = st.toggle(\"Befehle Aktiv\", sd.get('commands_enabled', True))
    
    cmds = sd.get('custom_commands', [])
    for i, cmd in enumerate(cmds):
        with st.expander(f\"Befehl: {cmd.get('name', 'Neu')}\"):
            cmd['name'] = st.text_input(f\"Name\", cmd.get('name', ''), key=f\"n_{i}\")
            cmd['response'] = st.text_area(f\"Antwort\", cmd.get('response', ''), key=f\"r_{i}\")
            if st.button(\"🗑️ Löschen\", key=f\"d_{i}\"):
                cmds.pop(i)
                st.rerun()
                
    if st.button(\"➕ Neuer Befehl\"):
        cmds.append({\"name\": \"befehl\", \"prefix\": \"!\", \"response\": \"Text\"})
        sd['custom_commands'] = cmds
        st.rerun()

with tab3:
    st.header(\"👔 Management & Berechtigungen\")
    sd['management_enabled'] = st.toggle(\"Management-Befehle Aktiv\", sd.get('management_enabled', True))
    
    def role_list_input(label, current, key):
        val = \", \".join(map(str, current)) if isinstance(current, list) else str(current)
        res = st.text_input(label, val, key=key)
        if res:
            return [int(x.strip()) for x in res.split(\",\") if x.strip().isdigit()]
        return []

    sd['befoerdern_allowed_roles'] = role_list_input(\"Wer darf befördern? (IDs)\", sd.get('befoerdern_allowed_roles', []), \"b_roles\")
    sd['rankup_allowed_roles'] = role_list_input(\"Wer darf Rankup? (IDs)\", sd.get('rankup_allowed_roles', []), \"r_roles\")

with tab4:
    st.header(\"🎫 Tickets\")
    sd['tickets_enabled'] = st.toggle(\"Ticket-System Aktiv\", sd.get('tickets_enabled', False))
    sd['tickets_panel_title'] = st.text_input(\"Titel\", sd.get('tickets_panel_title', '🎫 Ticket-System'))

with tab5:
    st.header(\"🎭 Rollen-Events\")
    sd['role_events_enabled'] = st.toggle(\"Rollen-Automatisierung Aktiv\", sd.get('role_events_enabled', False))
    
    rules = sd.get('role_event_rules', [])
    for i, rule in enumerate(rules):
        with st.expander(f\"Regel {i+1}: {rule.get('name', 'Unbenannt')}\"):
            rule['name'] = st.text_input(\"Name\", rule.get('name', 'Regel'), key=f\"re_name_{i}\")
            rule['trigger_role'] = st.text_input(\"Wenn diese Rolle (ID)\", value=str(rule.get('trigger_role', '')), key=f\"re_trig_{i}\")
            rule['event_type'] = st.selectbox(\"Event\", [\"Hinzugefügt\", \"Entfernt\"], index=0 if rule.get('event_type') == \"Hinzugefügt\" else 1, key=f\"re_event_{i}\")
            
            st.markdown(\"**Aktionen:**\")
            rule['message'] = st.text_area(\"Nachricht senden (Optional)\", rule.get('message', ''), key=f\"re_msg_{i}\")
            rule['channel_id'] = st.text_input(\"Kanal ID für Nachricht\", value=str(rule.get('channel_id', '')), key=f\"re_chan_{i}\")
            rule['action_role'] = st.text_input(\"Diese Rolle geben/nehmen (ID, Optional)\", value=str(rule.get('action_role', '')), key=f\"re_act_{i}\")
            
            if st.button(\"🗑️ Löschen\", key=f\"re_del_{i}\"):
                rules.pop(i)
                sd['role_event_rules'] = rules
                st.rerun()

    if st.button(\"➕ Neue Regel hinzufügen\"):
        rules.append({\"name\": \"Neue Regel\", \"trigger_role\": \"\", \"event_type\": \"Hinzugefügt\", \"message\": \"\", \"channel_id\": \"\", \"action_role\": \"\"})
        sd['role_event_rules'] = rules
        st.rerun()

st.session_state.settings_data = sd
