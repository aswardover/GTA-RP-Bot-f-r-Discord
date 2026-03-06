# -*- coding: utf-8 -*-
import streamlit as st
import json
import os
from config import SETTINGS_FILE

# Pfad zur Datendatei die vom Bot gefuellt wird
DISCORD_DATA_FILE = "discord_data.json"

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
    return {"channels": [], "roles": [], "categories": []}

st.set_page_config(page_title="GTA-RP Bot Dashboard", page_icon="🎮", layout="wide")
st.title("🎮 GTA-RP Bot – High-End Management")

settings = load_settings()
discord_data = load_discord_data()

# Dropdown Optionen vorbereiten
channels = {c["id"]: c["name"] for c in discord_data.get("channels", [])}
roles = {r["id"]: r["name"] for r in discord_data.get("roles", [])}
categories = {cat["id"]: cat["name"] for cat in discord_data.get("categories", [])}

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "⚙️ Allgemein", "👋 Willkommen", "🎫 Tickets", "⏱️ Stempeluhr", 
    "📢 Ankuendigung", "👔 Personal", "🤖 Custom"
])

# ── TAB 1: ALLGEMEIN ──────────────────────────────────────────
with tab1:
    st.header("Allgemeine Einstellungen")
    col_log, col_ar = st.columns(2)
    
    with col_log:
        st.subheader("Logging")
        current_log = str(settings.get("log_channel") or "")
        settings["log_channel"] = st.selectbox("Kanal fuer Rollen-Logs", options=list(channels.keys()), format_func=lambda x: channels[x], index=list(channels.keys()).index(current_log) if current_log in channels else 0)
    
    with col_ar:
        st.subheader("Automatisierung")
        settings["auto_role_enabled"] = st.checkbox("Auto-Rolle bei Beitritt", value=settings.get("auto_role_enabled", False))
        if settings["auto_role_enabled"]:
            current_ar = str(settings.get("auto_role_id") or "")
            settings["auto_role_id"] = st.selectbox("Zuzuweisende Rolle", options=list(roles.keys()), format_func=lambda x: roles[x], index=list(roles.keys()).index(current_ar) if current_ar in roles else 0)

# ── TAB 2: WILLKOMMEN ─────────────────────────────────────────
with tab2:
    st.header("Willkommens- & Abschieds-System")
    
    en_welcome = st.toggle("Willkommens-Nachrichten", value=settings.get("welcome_enabled", True))
    settings["welcome_enabled"] = en_welcome
    if en_welcome:
        c1, c2 = st.columns([1, 2])
        with c1:
            current_wc = str(settings.get("welcome_channel_id") or "")
            settings["welcome_channel_id"] = st.selectbox("Ziel-Kanal", options=list(channels.keys()), format_func=lambda x: channels[x], index=list(channels.keys()).index(current_wc) if current_wc in channels else 0, key="wc_sel")
            settings["welcome_embed"] = st.checkbox("Als Embed senden", value=settings.get("welcome_embed", True))
        with c2:
            settings["welcome_message"] = st.text_area("Nachricht ({user}, {server})", settings.get("welcome_message", "Willkommen {user}!"))

    st.divider()
    en_goodbye = st.toggle("Abschieds-Nachrichten", value=settings.get("goodbye_enabled", False))
    settings["goodbye_enabled"] = en_goodbye
    if en_goodbye:
        c1, c2 = st.columns([1, 2])
        with c1:
            current_gc = str(settings.get("goodbye_channel_id") or "")
            settings["goodbye_channel_id"] = st.selectbox("Ziel-Kanal ", options=list(channels.keys()), format_func=lambda x: channels[x], index=list(channels.keys()).index(current_gc) if current_gc in channels else 0, key="gc_sel")
        with c2:
            settings["goodbye_message"] = st.text_area("Nachricht  ({user})", settings.get("goodbye_message", "{user} hat uns verlassen."))

# ── TAB 3: TICKETS ────────────────────────────────────────────
with tab3:
    st.header("Ticket-System")
    en_tickets = st.toggle("Ticket-System aktivieren", value=settings.get("tickets_enabled", False))
    settings["tickets_enabled"] = en_tickets
    
    if en_tickets:
        col_setup, col_cats = st.columns([1, 1])
        with col_setup:
            st.subheader("Konfiguration")
            current_tc = str(settings.get("tickets_panel_channel_id") or "")
            settings["tickets_panel_channel_id"] = st.selectbox("Panel-Kanal", options=list(channels.keys()), format_func=lambda x: channels[x], index=list(channels.keys()).index(current_tc) if current_tc in channels else 0)
            settings["tickets_panel_title"] = st.text_input("Titel", settings.get("tickets_panel_title", "Support-Ticket"))
            
            if st.button("🚀 Panel im Discord veroeffentlichen", use_container_width=True):
                settings["tickets_publish_trigger"] = True
                st.info("Wird beim Speichern gesendet!")

        with col_cats:
            st.subheader("Kategorien")
            if "ticket_cats" not in st.session_state:
                st.session_state.ticket_cats = settings.get("tickets_categories", [])
            
            new_cat = st.text_input("Neue Kategorie Name")
            if st.button("➕ Hinzufuegen"):
                if new_cat and new_cat not in st.session_state.ticket_cats:
                    st.session_state.ticket_cats.append(new_cat)
                    st.rerun()
            
            for cat in st.session_state.ticket_cats:
                c1, c2 = st.columns([5, 1])
                c1.write(f"• {cat}")
                if c2.button("🗑️", key=f"del_{cat}"):
                    st.session_state.ticket_cats.remove(cat)
                    st.rerun()
            settings["tickets_categories"] = st.session_state.ticket_cats

# ── TAB 4: STEMPELUHR ─────────────────────────────────────────
with tab4:
    st.header("Stempeluhr")
    en_stempel = st.toggle("Stempeluhr aktivieren", value=settings.get("stempeluhr_enabled", False))
    settings["stempeluhr_enabled"] = en_stempel
    
    if en_stempel:
        c1, c2 = st.columns(2)
        with c1:
            current_sc = str(settings.get("stempeluhr_panel_channel_id") or "")
            settings["stempeluhr_panel_channel_id"] = st.selectbox("Stempel-Kanal", options=list(channels.keys()), format_func=lambda x: channels[x], index=list(channels.keys()).index(current_sc) if current_sc in channels else 0)
            
            if st.button("🚀 Stempel-Buttons veroeffentlichen", use_container_width=True):
                settings["stempeluhr_publish_trigger"] = True
        
        with c2:
            settings["stempeluhr_allowed_roles"] = st.multiselect("Erlaubte Rollen", options=list(roles.keys()), format_func=lambda x: roles[x], default=[str(r) for r in settings.get("stempeluhr_allowed_roles", [])])
            settings["stempeluhr_admin_roles"] = st.multiselect("Admin Rollen", options=list(roles.keys()), format_func=lambda x: roles[x], default=[str(r) for r in settings.get("stempeluhr_admin_roles", [])])

# ── TAB 6: PERSONAL ───────────────────────────────────────────
with tab6:
    st.header("Personal-Verwaltung")
    for cmd in ["befoerdern", "rankup", "drank", "einstellen", "kuendigen"]:
        with st.expander(f"Befehl: /{cmd}"):
            settings[f"{cmd}_enabled"] = st.toggle("Aktiviert", value=settings.get(f"{cmd}_enabled", True), key=f"tgl_{cmd}")
            if settings[f"{cmd}_enabled"]:
                settings[f"{cmd}_allowed_roles"] = st.multiselect("Wer darf das nutzen?", options=list(roles.keys()), format_func=lambda x: roles[x], default=[str(r) for r in settings.get(f"{cmd}_allowed_roles", [])], key=f"ms_{cmd}")

# ── TAB 7: CUSTOM ─────────────────────────────────────────────
with tab7:
    st.header("Custom Commands")
    if "cc_list" not in st.session_state:
        st.session_state.cc_list = settings.get("custom_commands", [])

    if st.button("➕ Neuer Custom Command"):
        st.session_state.cc_list.append({"name": "befehl", "prefix": "/", "response": "Antwort"})
        st.rerun()

    for i, cc in enumerate(st.session_state.cc_list):
        with st.expander(f"Command: {cc.get('prefix')}{cc.get('name')}"):
            cc["prefix"] = st.selectbox("Prefix", ["/", "!"], index=0 if cc.get("prefix") == "/" else 1, key=f"ccp_{i}")
            cc["name"] = st.text_input("Name", cc.get("name"), key=f"ccn_{i}")
            cc["response"] = st.text_area("Antwort", cc.get("response"), key=f"ccr_{i}")
            if st.button("Entfernen", key=f"ccd_{i}"):
                st.session_state.cc_list.pop(i)
                st.rerun()
    settings["custom_commands"] = st.session_state.cc_list

st.divider()
if st.button("💾 SPEICHERN & AN BOT SENDEN", type="primary", use_container_width=True):
    save_settings(settings)
    st.success("Konfiguration gespeichert!")
    st.rerun()
