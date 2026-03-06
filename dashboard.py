# -*- coding: utf-8 -*-
import streamlit as st
import json
import os
from config import SETTINGS_FILE, LOGO_FILE

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

st.set_page_config(page_title="GTA-RP Bot Dashboard", page_icon="🎮", layout="wide")
st.title("🎮 GTA-RP Bot – Management Dashboard")

settings = load_settings()

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "⚙️ Allgemein",
    "👋 Willkommen",
    "🎫 Tickets",
    "⏱️ Stempeluhr",
    "📢 Ankuendigung",
    "👔 Personal-Befehle",
    "🤖 Custom Commands"
])

# ── TAB 1: ALLGEMEIN ──────────────────────────────────────────
with tab1:
    st.header("Allgemeine Einstellungen")
    settings["log_channel"] = st.text_input(
        "Log-Kanal ID (fuer Rollenänderungen)",
        str(settings.get("log_channel") or "")
    )
    settings["auto_role_id"] = st.text_input(
        "Auto-Rolle ID (wird neuen Membern gegeben)",
        str(settings.get("auto_role_id") or "")
    )
    settings["embed_footer"] = st.text_input(
        "Embed Footer Text",
        settings.get("embed_footer", "Asward-Helper")
    )

# ── TAB 2: WILLKOMMEN ─────────────────────────────────────────
with tab2:
    st.header("Willkommens-System")
    settings["welcome_enabled"] = st.checkbox(
        "Willkommens-Nachrichten aktivieren",
        value=settings.get("welcome_enabled", True)
    )
    settings["welcome_channel_id"] = st.text_input(
        "Willkommens-Kanal ID",
        str(settings.get("welcome_channel_id") or settings.get("welcome_channel") or "")
    )
    settings["welcome_message"] = st.text_area(
        "Willkommens-Nachricht (Variablen: {user}, {server})",
        settings.get("welcome_message", "Willkommen {user} auf {server}!")
    )
    settings["welcome_embed"] = st.checkbox(
        "Als Embed senden",
        value=settings.get("welcome_embed", True)
    )
    st.divider()
    st.subheader("Verabschiedungs-System")
    settings["goodbye_enabled"] = st.checkbox(
        "Verabschiedungs-Nachrichten aktivieren",
        value=settings.get("goodbye_enabled", False)
    )
    settings["goodbye_channel_id"] = st.text_input(
        "Abschied-Kanal ID",
        str(settings.get("goodbye_channel_id") or "")
    )
    settings["goodbye_message"] = st.text_area(
        "Abschied-Nachricht (Variable: {user})",
        settings.get("goodbye_message", "{user} hat den Server verlassen.")
    )

# ── TAB 3: TICKETS ────────────────────────────────────────────
with tab3:
    st.header("Ticket-System")
    settings["tickets_enabled"] = st.checkbox(
        "Ticket-System aktivieren",
        value=settings.get("tickets_enabled", False)
    )
    settings["tickets_panel_channel_id"] = st.text_input(
        "Ticket-Panel Kanal ID",
        str(settings.get("tickets_panel_channel_id") or "")
    )
    settings["tickets_panel_title"] = st.text_input(
        "Panel Titel",
        settings.get("tickets_panel_title", "Ticket-System")
    )
    settings["tickets_panel_description"] = st.text_area(
        "Panel Beschreibung",
        settings.get("tickets_panel_description", "Waehle eine Kategorie aus, um ein Ticket zu oeffnen.")
    )
    settings["tickets_ticket_message"] = st.text_area(
        "Nachricht im Ticket (wird beim Oeffnen gesendet)",
        settings.get("tickets_ticket_message", "Wir melden uns bald bei dir!")
    )
    ui_options = ["button", "select"]
    ui_index = ui_options.index(settings.get("tickets_ui_type", "button")) if settings.get("tickets_ui_type", "button") in ui_options else 0
    settings["tickets_ui_type"] = st.selectbox("UI-Typ", ui_options, index=ui_index)
    st.subheader("Ticket-Kategorien")
    st.caption("Eine Kategorie pro Zeile (nur bei UI-Typ 'select' aktiv)")
    cats_raw = st.text_area(
        "Kategorien",
        "\n".join(settings.get("tickets_categories", []))
    )
    settings["tickets_categories"] = [c.strip() for c in cats_raw.split("\n") if c.strip()]

# ── TAB 4: STEMPELUHR ─────────────────────────────────────────
with tab4:
    st.header("Stempeluhr-System")
    settings["stempeluhr_enabled"] = st.checkbox(
        "Stempeluhr aktivieren",
        value=settings.get("stempeluhr_enabled", False)
    )
    settings["stempeluhr_panel_channel_id"] = st.text_input(
        "Panel-Kanal ID (wo der Ein/Aus-Button gepostet wird)",
        str(settings.get("stempeluhr_panel_channel_id") or "")
    )
    settings["stempeluhr_log_channel_id"] = st.text_input(
        "Log-Kanal ID (fuer Stempel-Aktivitaeten)",
        str(settings.get("stempeluhr_log_channel_id") or "")
    )
    st.subheader("Berechtigungen")
    st.caption("Rollen-IDs eingeben – eine pro Zeile. Leer lassen = alle duerfen stempeln.")
    allowed_raw = st.text_area(
        "Rollen die selbst stempeln duerfen (Button)",
        "\n".join([str(r) for r in settings.get("stempeluhr_allowed_roles", [])])
    )
    settings["stempeluhr_allowed_roles"] = [int(r.strip()) for r in allowed_raw.split("\n") if r.strip().isdigit()]
    admin_raw = st.text_area(
        "Admin-Rollen (duerfen /stempel ein @user, /stempel aus @user, /stempel liste)",
        "\n".join([str(r) for r in settings.get("stempeluhr_admin_roles", [])])
    )
    settings["stempeluhr_admin_roles"] = [int(r.strip()) for r in admin_raw.split("\n") if r.strip().isdigit()]

# ── TAB 5: ANKUENDIGUNG ───────────────────────────────────────
with tab5:
    st.header("Ankuendigungs-System")
    st.info("/ankuendigung – sendet eine Ankuendigung in einen beliebigen Kanal. Nur Admins koennen es nutzen.")
    settings["ankuendigung_default_channel_id"] = st.text_input(
        "Standard-Ankuendigungs-Kanal ID (optional)",
        str(settings.get("ankuendigung_default_channel_id") or "")
    )

# ── TAB 6: PERSONAL-BEFEHLE ───────────────────────────────────
with tab6:
    st.header("Personal-Befehle (Rollen-Management)")
    st.caption("Hier kannst du festlegen wer die jeweiligen Befehle nutzen darf (Rollen-IDs, eine pro Zeile).")

    for cmd_key, label in [
        ("befoerdern", "/befoerdern – Rolle hinzufuegen"),
        ("rankup", "/rankup – Alte Rolle entfernen, neue geben"),
        ("drank", "/drank – Rolle entfernen (Degradierung)"),
        ("einstellen", "/einstellen – User einstellen (Rolle geben)"),
        ("kuendigen", "/kuendigen – User kuendigen (Rolle entfernen)"),
    ]:
        with st.expander(f"⚙️ {label}"):
            enabled_key = f"{cmd_key}_enabled"
            roles_key = f"{cmd_key}_allowed_roles"
            settings[enabled_key] = st.checkbox(
                f"Befehl aktivieren",
                value=settings.get(enabled_key, True),
                key=f"chk_{cmd_key}"
            )
            raw = st.text_area(
                f"Erlaubte Rollen-IDs (leer = nur Admins)",
                "\n".join([str(r) for r in settings.get(roles_key, [])]),
                key=f"roles_{cmd_key}"
            )
            settings[roles_key] = [int(r.strip()) for r in raw.split("\n") if r.strip().isdigit()]

# ── TAB 7: CUSTOM COMMANDS ────────────────────────────────────
with tab7:
    st.header("Custom Commands")
    st.caption("Eigene Befehle erstellen. Praefix '/' = Slash-Command, '!' = Prefix-Command.")

    custom_commands = settings.get("custom_commands", [])

    if "cc_count" not in st.session_state:
        st.session_state.cc_count = max(len(custom_commands), 1)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("+ Befehl hinzufuegen"):
            st.session_state.cc_count += 1
    with col2:
        if st.button("- Befehl entfernen") and st.session_state.cc_count > 1:
            st.session_state.cc_count -= 1

    new_commands = []
    for i in range(st.session_state.cc_count):
        existing = custom_commands[i] if i < len(custom_commands) else {}
        with st.expander(f"Befehl #{i+1}: {existing.get('name', 'neu')}", expanded=(i == 0)):
            c1, c2 = st.columns([1, 3])
            with c1:
                prefix = st.selectbox("Praefix", ["/", "!"], index=0 if existing.get("prefix", "/") == "/" else 1, key=f"pfx_{i}")
            with c2:
                name = st.text_input("Name", existing.get("name", ""), key=f"name_{i}")
            response = st.text_area("Antwort (Variablen: {user}, {server}, {channel})", existing.get("response", ""), key=f"resp_{i}")
            roles_raw = st.text_input("Erlaubte Rollen-IDs (kommagetrennt, leer = alle)", ",".join([str(r) for r in existing.get("allowed_roles", [])]), key=f"croles_{i}")
            allowed = [int(r.strip()) for r in roles_raw.split(",") if r.strip().isdigit()]
            if name:
                new_commands.append({"name": name, "prefix": prefix, "response": response, "allowed_roles": allowed})

    settings["custom_commands"] = new_commands

# ── SPEICHERN ─────────────────────────────────────────────────
st.divider()
if st.button("💾 Einstellungen speichern", type="primary", use_container_width=True):
    save_settings(settings)
    st.success("✅ Konfiguration wurde gespeichert!")
    st.rerun()
