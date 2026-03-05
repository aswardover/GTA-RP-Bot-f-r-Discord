# -*- coding: utf-8 -*-
import streamlit as st
import json
import os
from config import SETTINGS_FILE, LOGO_FILE

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "welcome_channel": "",
        "welcome_message": "Willkommen {user} auf {server}!",
        "log_channel": "",
        "auto_role": ""
    }

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

st.set_page_config(page_title="GTA-RP Bot Dashboard", layout="wide")
st.title("🎮 GTA-RP Bot Management")

settings = load_settings()

tab1, tab2 = st.tabs(["Allgemein", "Willkommens-System"])

with tab1:
    st.header("Kanal-Konfiguration")
    settings["log_channel"] = st.text_input("Log-Kanal ID", settings.get("log_channel", ""))
    settings["auto_role"] = st.text_input("Auto-Rolle ID (für neue User)", settings.get("auto_role", ""))

with tab2:
    st.header("Willkommen & Abschied")
    settings["welcome_channel"] = st.text_input("Willkommens-Kanal ID", settings.get("welcome_channel", ""))
    settings["welcome_message"] = st.text_area("Nachricht", settings.get("welcome_message", ""))

if st.button("Einstellungen speichern"):
    save_settings(settings)
    st.success("Konfiguration wurde aktualisiert!")
