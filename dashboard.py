# -*- coding: utf-8 -*-
import streamlit as st
import json
import os

SETTINGS_FILE = 'settings.json'

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

st.set_page_config(page_title="GTA RP Bot Dashboard", layout="wide")
st.title("🎮 GTA RP Bot Dashboard")

settings = load_settings()

tab1, tab2, tab3, tab4 = st.tabs(["Allgemein", "Custom Commands", "Fraktion/Management", "Tickets"])

with tab1:
    st.header("Allgemeine Einstellungen")
    settings['welcome_message'] = st.text_input("Willkommensnachricht", settings.get('welcome_message', ''))
    settings['welcome_channel_id'] = st.number_input("Willkommens-Kanal ID", value=settings.get('welcome_channel_id', 0), step=1)
    
    st.subheader("Ankündigungen")
    settings['announce_channel_id'] = st.number_input("Ankündigungs-Kanal ID", value=settings.get('announce_channel_id', 0), step=1)
    settings['announce_title'] = st.text_input("Standard Titel", settings.get('announce_title', '📢 Ankündigung'))

with tab2:
    st.header("Custom Commands")
    settings['custom_commands_enabled'] = st.checkbox("Custom Commands Aktivieren", settings.get('custom_commands_enabled', True))
    
    commands_list = settings.get('custom_commands', [])
    new_commands = []
    
    for i, cmd in enumerate(commands_list):
        with st.expander(f"Command: {cmd.get('name', 'Neu')}"):
            col1, col2 = st.columns(2)
            name = col1.text_input(f"Name #{i}", cmd.get('name', ''), key=f"name_{i}")
            prefix = col2.selectbox(f"Prefix #{i}", ["!", "/", "?"], index=["!", "/", "?"].index(cmd.get('prefix', '!')), key=f"prefix_{i}")
            response = st.text_area(f"Antwort #{i}", cmd.get('response', ''), key=f"resp_{i}")
            
            if st.button(f"Löschen #{i}", key=f"del_{i}"):
                continue
            new_commands.append({"name": name, "prefix": prefix, "response": response})
            
    if st.button("➕ Neuen Command hinzufügen"):
        new_commands.append({"name": "neu", "prefix": "!", "response": "Antwort hier"})
    
    settings['custom_commands'] = new_commands

with tab3:
    st.header("Fraktions & Management Befehle")
    
    # Beförderung
    st.subheader("Befördern (Rolle geben)")
    settings['befoerdern_enabled'] = st.checkbox("Befördern Aktiviert", settings.get('befoerdern_enabled', True))
    settings['befoerdern_allowed_roles'] = st.multiselect("Wer darf /befoerdern nutzen? (Rollen IDs)", [], default=settings.get('befoerdern_allowed_roles', []))

    # Rankup
    st.subheader("Rankup (Rolle tauschen)")
    settings['rankup_enabled'] = st.checkbox("Rankup Aktiviert", settings.get('rankup_enabled', True))
    settings['rankup_allowed_roles'] = st.multiselect("Wer darf /rankup nutzen? (Rollen IDs)", [], default=settings.get('rankup_allowed_roles', []))

    # Einstellen
    st.subheader("Einstellen")
    settings['einstellen_enabled'] = st.checkbox("Einstellen Aktiviert", settings.get('einstellen_enabled', True))
    settings['einstellen_allowed_roles'] = st.multiselect("Wer darf /einstellen nutzen? (Rollen IDs)", [], default=settings.get('einstellen_allowed_roles', []))

    # Kündigen
    st.subheader("Kündigen")
    settings['kuendigen_enabled'] = st.checkbox("Kündigen Aktiviert", settings.get('kuendigen_enabled', True))
    settings['kuendigen_allowed_roles'] = st.multiselect("Wer darf /kuendigen nutzen? (Rollen IDs)", [], default=settings.get('kuendigen_allowed_roles', []))

    # Drank
    st.subheader("Drank (Degradieren)")
    settings['drank_enabled'] = st.checkbox("Drank Aktiviert", settings.get('drank_enabled', True))
    settings['drank_allowed_roles'] = st.multiselect("Wer darf /drank nutzen? (Rollen IDs)", [], default=settings.get('drank_allowed_roles', []))

with tab4:
    st.header("Ticket System")
    settings['tickets_enabled'] = st.checkbox("Tickets Aktivieren", settings.get('tickets_enabled', False))
    settings['tickets_panel_title'] = st.text_input("Panel Titel", settings.get('tickets_panel_title', '🎫 Ticket-System'))

if st.button("💾 Einstellungen Speichern"):
    save_settings(settings)
    st.success("Einstellungen wurden gespeichert! Starte den Bot neu, um Änderungen zu übernehmen.")
