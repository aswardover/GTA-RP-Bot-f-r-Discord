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
        "welcome_channel_id": "",
        "welcome_message": "Willkommen {user} auf {server}!",
        "welcome_enabled": True,
        "welcome_embed": True,
        "auto_role_id": None,
        "embed_footer": "Asward-Helper",
        "goodbye_enabled": False,
        "goodbye_channel_id": None,
        "goodbye_message": "{user} hat den Server verlassen.",
        "tickets_enabled": False,
        "tickets_panel_channel_id": None,
        "tickets_categories": [],
        "tickets_panel_publish": False,
        "tickets_dashboard_enabled": True,
        "tickets_panel_title": "Ticket-System",
        "tickets_panel_description": "Waehle eine Kategorie aus, um ein Ticket zu oeffnen.",
        "tickets_ticket_message": "Wir melden uns bald bei dir!",
        "tickets_ui_type": "button",
        "stempeluhr_enabled": False,
        "stempeluhr_log_channel_id": None,
        "stempeluhr_allowed_roles": [],
        "stempeluhr_admin_roles": [],
        "stempeluhr_panel_channel_id": None,
    }

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

st.set_page_config(page_title="GTA-RP Bot Dashboard", layout="wide")
st.title("GTA-RP Bot Management")

settings = load_settings()

tab1, tab2, tab3, tab4 = st.tabs(["Allgemein", "Willkommens-System", "Ticket-System", "Stempeluhr"])

with tab1:
    st.header("Allgemeine Konfiguration")
    settings["log_channel"] = st.text_input("Log-Kanal ID", settings.get("log_channel", ""))
    settings["auto_role_id"] = st.text_input("Auto-Rolle ID (fuer neue Mitglieder)", str(settings.get("auto_role_id") or ""))
    settings["embed_footer"] = st.text_input("Embed Footer Text", settings.get("embed_footer", "Asward-Helper"))

with tab2:
    st.header("Willkommens-System")
    settings["welcome_enabled"] = st.checkbox("Willkommens-Nachrichten aktivieren", value=settings.get("welcome_enabled", True))
    settings["welcome_channel_id"] = st.text_input("Willkommens-Kanal ID", str(settings.get("welcome_channel_id") or ""))
    settings["welcome_message"] = st.text_area("Willkommens-Nachricht (Variablen: {user}, {server})", settings.get("welcome_message", "Willkommen {user} auf {server}!"))
    settings["welcome_embed"] = st.checkbox("Als Embed senden", value=settings.get("welcome_embed", True))
    st.divider()
    st.subheader("Verabschiedungs-System")
    settings["goodbye_enabled"] = st.checkbox("Verabschiedungs-Nachrichten aktivieren", value=settings.get("goodbye_enabled", False))
    settings["goodbye_channel_id"] = st.text_input("Abschied-Kanal ID", str(settings.get("goodbye_channel_id") or ""))
    settings["goodbye_message"] = st.text_area("Abschied-Nachricht (Variablen: {user})", settings.get("goodbye_message", "{user} hat den Server verlassen."))

with tab3:
    st.header("Ticket-System")
    settings["tickets_enabled"] = st.checkbox("Ticket-System aktivieren", value=settings.get("tickets_enabled", False))
    settings["tickets_panel_channel_id"] = st.text_input("Ticket-Panel Kanal ID", str(settings.get("tickets_panel_channel_id") or ""))
    settings["tickets_panel_title"] = st.text_input("Panel Titel", settings.get("tickets_panel_title", "Ticket-System"))
    settings["tickets_panel_description"] = st.text_area("Panel Beschreibung", settings.get("tickets_panel_description", "Waehle eine Kategorie aus, um ein Ticket zu oeffnen."))
    settings["tickets_ticket_message"] = st.text_area("Ticket Nachricht (wird im Ticket gesendet)", settings.get("tickets_ticket_message", "Wir melden uns bald bei dir!"))
    settings["tickets_ui_type"] = st.selectbox("UI-Typ", ["button", "select"], index=0 if settings.get("tickets_ui_type", "button") == "button" else 1)
    st.subheader("Ticket-Kategorien")
    cats_raw = st.text_area("Kategorien (eine pro Zeile)", "\n".join(settings.get("tickets_categories", [])))
    settings["tickets_categories"] = [c.strip() for c in cats_raw.split("\n") if c.strip()]

with tab4:
    st.header("Stempeluhr-System")
    settings["stempeluhr_enabled"] = st.checkbox("Stempeluhr aktivieren", value=settings.get("stempeluhr_enabled", False))
    settings["stempeluhr_panel_channel_id"] = st.text_input("Stempeluhr-Panel Kanal ID (fuer den Button)", str(settings.get("stempeluhr_panel_channel_id") or ""))
    settings["stempeluhr_log_channel_id"] = st.text_input("Stempeluhr Log-Kanal ID", str(settings.get("stempeluhr_log_channel_id") or ""))
    st.subheader("Berechtigungen")
    st.info("Rollen-IDs eingeben (eine pro Zeile)")
    allowed_raw = st.text_area("Rollen die stempeln duerfen (leer = alle)", "\n".join([str(r) for r in settings.get("stempeluhr_allowed_roles", [])]))
    settings["stempeluhr_allowed_roles"] = [int(r.strip()) for r in allowed_raw.split("\n") if r.strip().isdigit()]
    admin_raw = st.text_area("Admin-Rollen (duerfen /stempel ein und aus @user nutzen + /stempel liste)", "\n".join([str(r) for r in settings.get("stempeluhr_admin_roles", [])]))
    settings["stempeluhr_admin_roles"] = [int(r.strip()) for r in admin_raw.split("\n") if r.strip().isdigit()]

if st.button("Einstellungen speichern", type="primary"):
    save_settings(settings)
    st.success("Konfiguration wurde gespeichert!")
    st.rerun()
