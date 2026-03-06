# -*- coding: utf-8 -*-
import streamlit as st
import json
import os
from config import SETTINGS_FILE

# ─── KONFIGURATION ────────────────────────────────────────────
DISCORD_DATA_FILE = "discord_data.json"
DASHBOARD_PASSWORD = "GTA2026"  # Passwort aendern!

# ─── HILFSFUNKTIONEN ──────────────────────────────────────────
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

def sel_channel(label, key, settings_key, channels, settings, placeholder="Kanal waehlen..."):
    """Hilfsfunktion: Channel-Selectbox mit Fallback"""
    opts = list(channels.keys())
    current = str(settings.get(settings_key) or "")
    idx = opts.index(current) if current in opts else 0
    val = st.selectbox(label, options=opts, format_func=lambda x: f"# {channels[x]}", index=idx, key=key)
    settings[settings_key] = val

def sel_role(label, key, settings_key, roles, settings):
    """Hilfsfunktion: Rollen-Selectbox mit Fallback"""
    opts = list(roles.keys())
    current = str(settings.get(settings_key) or "")
    idx = opts.index(current) if current in opts else 0
    val = st.selectbox(label, options=opts, format_func=lambda x: f"@{roles[x]}", index=idx, key=key)
    settings[settings_key] = val

# ─── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="GTA-RP Bot Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ───────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    border-right: 2px solid #334155;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 4px; background-color: #1e293b;
    padding: 8px; border-radius: 12px;
}
.stTabs [data-baseweb="tab"] {
    background-color: #334155; color: #94a3b8;
    border-radius: 8px; padding: 8px 16px;
    font-weight: 600; border: none;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    color: white !important;
}
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: white; border: none; border-radius: 8px;
    font-weight: 700; transition: all 0.2s;
}
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 15px rgba(59,130,246,0.4); }
.publish-btn > button {
    background: linear-gradient(135deg, #22c55e, #16a34a) !important;
}
.card {
    background: #1e293b; border: 1px solid #334155;
    border-radius: 12px; padding: 20px; margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# ─── PASSWORTSCHUTZ ───────────────────────────────────────────
def check_password():
    def pw_check():
        if st.session_state.get("_pw_input") == DASHBOARD_PASSWORD:
            st.session_state["auth"] = True
        else:
            st.session_state["auth"] = False
    
    if st.session_state.get("auth"):
        return True
    
    st.markdown("""
    <div style='text-align:center; padding: 80px 0 40px 0;'>
        <div style='font-size:64px;'>🎮</div>
        <h1 style='color:#38bdf8; font-size:40px; margin:10px 0 5px 0;'>GTA-RP Bot Dashboard</h1>
        <p style='color:#64748b; font-size:16px;'>High-End Server Management</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.text_input(
            "🔒 Passwort",
            type="password",
            key="_pw_input",
            on_change=pw_check,
            placeholder="Dashboard-Passwort eingeben..."
        )
        if "auth" in st.session_state and not st.session_state["auth"]:
            st.error("❌ Falsches Passwort! Versuche es erneut.")
        st.markdown("""
        <p style='color:#475569; font-size:12px; text-align:center; margin-top:10px;'>
        Tipp: Das Passwort kann in dashboard.py geaendert werden.
        </p>
        """, unsafe_allow_html=True)
    return False

if not check_password():
    st.stop()

# ─── DATEN LADEN ───────────────────────────────────────────────
settings = load_settings()
discord_data = load_discord_data()

# Dropdown Optionen
channels = {str(c["id"]): c["name"] for c in discord_data.get("channels", [])}
roles    = {str(r["id"]): r["name"] for r in discord_data.get("roles", [])}
categories = {str(cat["id"]): cat["name"] for cat in discord_data.get("categories", [])}

# Fallback wenn Bot noch nicht lief
if not channels:
    channels = {"KANAL_ID": "(Bot starten um Kanaele zu laden)"}
if not roles:
    roles = {"ROLLEN_ID": "(Bot starten um Rollen zu laden)"}
if not categories:
    categories = {"KAT_ID": "(Bot starten um Kategorien zu laden)"}

# ─── HEADER ─────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding:20px 0 10px 0;'>
    <h1 style='color:#38bdf8; font-size:38px; margin:0;'>🎮 GTA-RP Bot</h1>
    <p style='color:#64748b; font-size:15px; margin:4px 0;'>High-End Discord Server Management</p>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='color:#38bdf8; text-align:center;'>🛡️ Dashboard</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div style='background:#0f172a; border:1px solid #334155; border-radius:10px; padding:15px;'>
    <p style='color:#94a3b8; font-weight:700; margin:0 0 8px 0;'>📌 Platzhalter fuer Nachrichten</p>
    <p style='color:#64748b; font-size:13px; margin:0;'>
    • <code style='background:#1e293b; padding:1px 5px; border-radius:4px;'>{user}</code> Benutzername<br>
    • <code style='background:#1e293b; padding:1px 5px; border-radius:4px;'>{server}</code> Servername<br>
    • <code style='background:#1e293b; padding:1px 5px; border-radius:4px;'>{member}</code> @Erwaehnung<br>
    • <code style='background:#1e293b; padding:1px 5px; border-radius:4px;'>{count}</code> Mitgliederzahl<br>
    </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")
    st.markdown("""
    <div style='background:#0f172a; border:1px solid #334155; border-radius:10px; padding:15px;'>
    <p style='color:#94a3b8; font-weight:700; margin:0 0 8px 0;'>ℹ️ Wichtige Hinweise</p>
    <p style='color:#64748b; font-size:13px; margin:0;'>
    • Aenderungen nach <b>Speichern</b> sofort aktiv<br>
    • <b>Veroeffentlichen</b> sendet Embed direkt in Discord<br>
    • Bot muss laufen damit Kanaele/Rollen erscheinen<br>
    • Passwort in <code>dashboard.py</code> aenderbar
    </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🚪 Ausloggen", use_container_width=True):
        st.session_state["auth"] = False
        st.rerun()

# ─── TABS ──────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "⚙️ Allgemein", "👋 Willkommen", "🎫 Tickets",
    "⏱️ Stempeluhr", "📢 Ankuendigung", "👔 Personal", "🤖 Custom"
])

# ══ TAB 1: ALLGEMEIN ═══════════════════════════════════════════
with tab1:
    st.header("⚙️ Allgemeine Einstellungen")
    st.caption("Grundlegende Servereinstellungen fuer den Bot.")
    st.markdown("---")
    
    col_log, col_ar = st.columns(2)
    
    with col_log:
        st.subheader("📜 Log-System")
        st.caption("Alle wichtigen Aktionen (Kick, Ban, Rollen etc.) werden in diesen Kanal geloggt.")
        log_opts = list(channels.keys())
        current_log = str(settings.get("log_channel") or log_opts[0])
        if current_log not in log_opts:
            current_log = log_opts[0]
        settings["log_channel"] = st.selectbox(
            "Log-Kanal",
            options=log_opts,
            format_func=lambda x: f"# {channels[x]}",
            index=log_opts.index(current_log),
            key="s_log_ch",
            help="z.B. #mod-logs oder #bot-logs"
        )
    
    with col_ar:
        st.subheader("🤖 Auto-Rolle")
        st.caption("Jedem neuen Mitglied wird beim Beitritt automatisch eine Rolle zugewiesen.")
        settings["auto_role_enabled"] = st.checkbox(
            "Auto-Rolle aktivieren",
            value=settings.get("auto_role_enabled", False)
        )
        if settings["auto_role_enabled"]:
            ar_opts = list(roles.keys())
            current_ar = str(settings.get("auto_role_id") or ar_opts[0])
            if current_ar not in ar_opts:
                current_ar = ar_opts[0]
            settings["auto_role_id"] = st.selectbox(
                "Automatisch zugewiesene Rolle",
                options=ar_opts,
                format_func=lambda x: f"@{roles[x]}",
                index=ar_opts.index(current_ar),
                key="s_ar_role",
                help="z.B. @Neuling oder @Buerger"
            )

# ══ TAB 2: WILLKOMMEN ═════════════════════════════════════════
with tab2:
    st.header("👋 Willkommens- & Abschieds-System")
    st.caption("Begruesst neue Mitglieder automatisch und verabschiedet sie beim Verlassen.")
    st.markdown("---")
    
    # Willkommen
    c_wl, c_wr = st.columns([1, 2])
    with c_wl:
        st.subheader("🎉 Willkommen")
        settings["welcome_enabled"] = st.toggle(
            "Willkommen-Nachrichten aktivieren",
            value=settings.get("welcome_enabled", True)
        )
        if settings["welcome_enabled"]:
            wc_opts = list(channels.keys())
            current_wc = str(settings.get("welcome_channel_id") or wc_opts[0])
            if current_wc not in wc_opts:
                current_wc = wc_opts[0]
            settings["welcome_channel_id"] = st.selectbox(
                "Kanal fuer Willkommensnachrichten",
                options=wc_opts,
                format_func=lambda x: f"# {channels[x]}",
                index=wc_opts.index(current_wc),
                key="s_wc_ch",
                help="z.B. #willkommen oder #allgemein"
            )
            settings["welcome_embed"] = st.checkbox(
                "Als Embed senden (schoeneres Design)",
                value=settings.get("welcome_embed", True)
            )
    with c_wr:
        if settings["welcome_enabled"]:
            st.markdown("<br>", unsafe_allow_html=True)
            settings["welcome_message"] = st.text_area(
                "Willkommensnachricht",
                value=settings.get("welcome_message", "Willkommen auf unserem Server, {user}! Wir freuen uns dich dabei zu haben."),
                height=120,
                help="Platzhalter: {user}, {server}, {member}, {count}"
            )
            st.caption("💡 Tipp: Nutze {user} fuer den Namen und {server} fuer den Servernamen.")
    
    st.markdown("---")
    
    # Abschied
    c_gl, c_gr = st.columns([1, 2])
    with c_gl:
        st.subheader("👋 Abschied")
        settings["goodbye_enabled"] = st.toggle(
            "Abschieds-Nachrichten aktivieren",
            value=settings.get("goodbye_enabled", False)
        )
        if settings["goodbye_enabled"]:
            gc_opts = list(channels.keys())
            current_gc = str(settings.get("goodbye_channel_id") or gc_opts[0])
            if current_gc not in gc_opts:
                current_gc = gc_opts[0]
            settings["goodbye_channel_id"] = st.selectbox(
                "Kanal fuer Abschieds-Nachrichten",
                options=gc_opts,
                format_func=lambda x: f"# {channels[x]}",
                index=gc_opts.index(current_gc),
                key="s_gc_ch",
                help="z.B. #abschiede"
            )
    with c_gr:
        if settings["goodbye_enabled"]:
            st.markdown("<br>", unsafe_allow_html=True)
            settings["goodbye_message"] = st.text_area(
                "Abschieds-Nachricht",
                value=settings.get("goodbye_message", "{user} hat unseren Server verlassen. Auf Wiedersehen!"),
                height=100,
                help="Platzhalter: {user}, {server}"
            )

# ══ TAB 3: TICKETS ══════════════════════════════════════════
with tab3:
    st.header("🎫 Ticket-System")
    st.caption("Mitglieder koennen per Button ein Ticket eroeffnen um Support zu erhalten.")
    st.markdown("---")
    
    settings["tickets_enabled"] = st.toggle(
        "Ticket-System aktivieren",
        value=settings.get("tickets_enabled", False)
    )
    
    if settings["tickets_enabled"]:
        col_setup, col_cats = st.columns([1, 1])
        
        with col_setup:
            st.subheader("🔧 Konfiguration")
            
            tc_opts = list(channels.keys())
            current_tc = str(settings.get("tickets_panel_channel_id") or tc_opts[0])
            if current_tc not in tc_opts:
                current_tc = tc_opts[0]
            settings["tickets_panel_channel_id"] = st.selectbox(
                "Panel-Kanal (wo der Button erscheint)",
                options=tc_opts,
                format_func=lambda x: f"# {channels[x]}",
                index=tc_opts.index(current_tc),
                key="s_tc_ch",
                help="z.B. #support oder #ticket-eroeffnen"
            )
            
            tcat_opts = list(categories.keys())
            current_tcat = str(settings.get("tickets_category_id") or tcat_opts[0])
            if current_tcat not in tcat_opts:
                current_tcat = tcat_opts[0]
            settings["tickets_category_id"] = st.selectbox(
                "Ticket-Kategorie (wo neue Tickets erstellt werden)",
                options=tcat_opts,
                format_func=lambda x: categories[x],
                index=tcat_opts.index(current_tcat),
                key="s_tcat",
                help="z.B. TICKETS Kategorie im Discord"
            )
            
            settings["tickets_panel_title"] = st.text_input(
                "Panel-Titel",
                value=settings.get("tickets_panel_title", "Support & Hilfe"),
                placeholder="z.B. Support & Hilfe, Kontakt zum Team"
            )
            
            st.markdown("")
            if st.button("🚀 Ticket-Panel veroeffentlichen", use_container_width=True, key="pub_tickets"):
                settings["tickets_publish_trigger"] = True
                save_settings(settings)
                st.success("✅ Ticket-Panel wird in Discord gepostet!")
        
        with col_cats:
            st.subheader("📌 Ticket-Kategorien")
            st.caption("Der Nutzer kann beim Erstellen eine Kategorie waehlen.")
            
            if "ticket_cats" not in st.session_state:
                st.session_state.ticket_cats = settings.get("tickets_categories", [])
            
            new_cat = st.text_input("Neue Kategorie", placeholder="z.B. Allgemein, Beschwerde, Frage...")
            if st.button("➕ Hinzufuegen", key="add_tcat"):
                if new_cat and new_cat not in st.session_state.ticket_cats:
                    st.session_state.ticket_cats.append(new_cat)
                    st.rerun()
            
            for cat in list(st.session_state.ticket_cats):
                c1, c2 = st.columns([5, 1])
                c1.markdown(f"• **{cat}**")
                if c2.button("🗑️", key=f"del_{cat}"):
                    st.session_state.ticket_cats.remove(cat)
                    st.rerun()
            settings["tickets_categories"] = st.session_state.ticket_cats

# ══ TAB 4: STEMPELUHR ════════════════════════════════════════
with tab4:
    st.header("⏱️ Stempeluhr")
    st.caption("Zeiterfassung fuer dein Team. Ein- und Ausstempeln direkt per Button in Discord.")
    st.markdown("---")
    
    settings["stempeluhr_enabled"] = st.toggle(
        "Stempeluhr aktivieren",
        value=settings.get("stempeluhr_enabled", False)
    )
    
    if settings["stempeluhr_enabled"]:
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("📌 Kanal & Panel")
            st.caption("In diesem Kanal wird der Stempel-Button gepostet.")
            
            sc_opts = list(channels.keys())
            current_sc = str(settings.get("stempeluhr_panel_channel_id") or sc_opts[0])
            if current_sc not in sc_opts:
                current_sc = sc_opts[0]
            settings["stempeluhr_panel_channel_id"] = st.selectbox(
                "Stempel-Kanal",
                options=sc_opts,
                format_func=lambda x: f"# {channels[x]}",
                index=sc_opts.index(current_sc),
                key="s_sc_ch",
                help="z.B. #stempeluhr oder #zeiterfassung"
            )
            
            st.markdown("")
            if st.button("🚀 Stempel-Panel veroeffentlichen", use_container_width=True, key="pub_stempel"):
                settings["stempeluhr_publish_trigger"] = True
                save_settings(settings)
                st.success("✅ Stempel-Panel wird in Discord gepostet!")
        
        with c2:
            st.subheader("🔑 Berechtigungen")
            st.caption("Wer darf stempeln und wer hat Admin-Rechte ueber die Stempeluhr?")
            
            role_opts = list(roles.keys())
            current_allowed = [str(r) for r in settings.get("stempeluhr_allowed_roles", []) if str(r) in role_opts]
            settings["stempeluhr_allowed_roles"] = st.multiselect(
                "Wer darf Ein-/Ausstempeln?",
                options=role_opts,
                format_func=lambda x: f"@{roles[x]}",
                default=current_allowed,
                help="Leer lassen = Alle duerfen stempeln"
            )
            
            current_admin = [str(r) for r in settings.get("stempeluhr_admin_roles", []) if str(r) in role_opts]
            settings["stempeluhr_admin_roles"] = st.multiselect(
                "Wer darf Stempel verwalten? (/stempel ein @user)",
                options=role_opts,
                format_func=lambda x: f"@{roles[x]}",
                default=current_admin,
                help="Nur diese Rollen koennen andere einstempeln und /stempel liste nutzen"
            )
        
        st.markdown("---")
        st.markdown("""
        <div style='background:#0f172a; border:1px solid #1e4d2b; border-radius:10px; padding:15px;'>
        <p style='color:#22c55e; font-weight:700; margin:0 0 5px 0;'>⏱️ Verfuegbare Stempel-Befehle</p>
        <p style='color:#64748b; font-size:13px; margin:0;'>
        • <code>/stempel ein @User</code> – Person einstempeln (Admin)<br>
        • <code>/stempel aus @User</code> – Person ausstempeln (Admin)<br>
        • <code>/stempel status</code> – Eigenen Status anzeigen (Alle)<br>
        • <code>/stempel liste</code> – Alle Zeiten anzeigen (Admin)<br>
        • Button im Kanal – Selbst ein-/ausstempeln
        </p>
        </div>
        """, unsafe_allow_html=True)

# ══ TAB 5: ANKUENDIGUNG ═══════════════════════════════════════
with tab5:
    st.header("📢 Ankuendigung senden")
    st.caption("Sende Embeds und Nachrichten direkt in jeden Discord-Kanal.")  
    st.markdown("---")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("📄 Einstellungen")
        ac_opts = list(channels.keys())
        current_ac = str(settings.get("announce_channel_id") or ac_opts[0])
        if current_ac not in ac_opts:
            current_ac = ac_opts[0]
        settings["announce_channel_id"] = st.selectbox(
            "Ziel-Kanal",
            options=ac_opts,
            format_func=lambda x: f"# {channels[x]}",
            index=ac_opts.index(current_ac),
            key="s_ac_ch",
            help="z.B. #ankuendigungen oder #news"
        )
        settings["announce_title"] = st.text_input(
            "Titel der Ankuendigung",
            value=settings.get("announce_title", ""),
            placeholder="z.B. Wichtige Server-Information!"
        )
    
    with c2:
        st.subheader("✍️ Nachricht")
        settings["announce_message"] = st.text_area(
            "Inhalt der Ankuendigung",
            value=settings.get("announce_message", ""),
            height=160,
            placeholder="Schreibe hier deine Ankuendigung...\n\nDu kannst mehrere Zeilen verwenden."
        )
        st.caption("💡 Die Ankuendigung wird als schoenes Embed in Discord gesendet.")
    
    st.markdown("")
    if st.button("🚀 Ankuendigung jetzt senden", use_container_width=True, key="pub_announce"):
        if settings.get("announce_message"):
            settings["announce_publish_trigger"] = True
            save_settings(settings)
            st.success("✅ Ankuendigung wird sofort in Discord gepostet!")
        else:
            st.error("❌ Bitte Nachricht eingeben!")
    
    st.info("ℹ️ Tipp: Du kannst mehrere Ankuendigungen hintereinander senden indem du den Text aenderst und erneut auf Senden drueckst.")

# ══ TAB 6: PERSONAL ═════════════════════════════════════════
with tab6:
    st.header("👔 Personal-Verwaltung")
    st.caption("Konfiguriere welche Rollen die Personal-Befehle nutzen duerfen.")
    st.markdown("---")
    
    cmd_info = {
        "befoerdern": {"label": "Befoerdern", "desc": "Eine Person in eine hoehere Rolle befoerdern", "icon": "⬆️"},
        "rankup": {"label": "Rank Up", "desc": "Automatischen Rangaufstieg geben", "icon": "📈"},
        "drank": {"label": "Degradieren", "desc": "Eine Person in eine niedrigere Rolle degradieren", "icon": "⬇️"},
        "einstellen": {"label": "Einstellen", "desc": "Ein neues Mitglied offiziell einstellen", "icon": "➕"},
        "kuendigen": {"label": "Kuendigen", "desc": "Einem Mitglied kuendigen / entlassen", "icon": "❌"},
    }
    role_opts = list(roles.keys())
    
    for cmd, info in cmd_info.items():
        with st.expander(f"{info['icon']} Befehl: /{cmd} – {info['desc']}"):
            col_en, col_role = st.columns([1, 3])
            with col_en:
                settings[f"{cmd}_enabled"] = st.toggle(
                    "Aktiviert",
                    value=settings.get(f"{cmd}_enabled", True),
                    key=f"tgl_{cmd}"
                )
            with col_role:
                if settings[f"{cmd}_enabled"]:
                    current_roles = [str(r) for r in settings.get(f"{cmd}_allowed_roles", []) if str(r) in role_opts]
                    settings[f"{cmd}_allowed_roles"] = st.multiselect(
                        f"Wer darf /{cmd} nutzen?",
                        options=role_opts,
                        format_func=lambda x: f"@{roles[x]}",
                        default=current_roles,
                        key=f"ms_{cmd}",
                        help="Leer = nur Admins"
                    )

# ══ TAB 7: CUSTOM COMMANDS ══════════════════════════════════
with tab7:
    st.header("🤖 Custom Commands")
    st.caption("Erstelle eigene Befehle mit automatischen Antworten.")
    st.markdown("---")
    
    if "cc_list" not in st.session_state:
        st.session_state.cc_list = settings.get("custom_commands", [])
    
    col_new, col_info = st.columns([2, 1])
    with col_new:
        if st.button("➕ Neuen Custom Command erstellen", use_container_width=True):
            st.session_state.cc_list.append({"name": "meinbefehl", "prefix": "/", "response": "Hier kommt die Antwort..."})
            st.rerun()
    with col_info:
        st.markdown("""
        <div style='background:#0f172a; border-radius:8px; padding:10px; font-size:12px; color:#64748b;'>
        Befehle koennen mit <code>/</code> oder <code>!</code> genutzt werden.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    for i, cc in enumerate(st.session_state.cc_list):
        with st.expander(f"💬 Befehl: {cc.get('prefix')}{cc.get('name')}"):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                cc["prefix"] = st.selectbox(
                    "Typ",
                    ["/", "!"],
                    index=0 if cc.get("prefix") == "/" else 1,
                    key=f"ccp_{i}"
                )
            with c2:
                cc["name"] = st.text_input(
                    "Befehlsname",
                    value=cc.get("name", ""),
                    key=f"ccn_{i}",
                    placeholder="z.B. regeln, info, kontakt"
                )
            with c3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️ Loeschen", key=f"ccd_{i}"):
                    st.session_state.cc_list.pop(i)
                    st.rerun()
            cc["response"] = st.text_area(
                "Antwort des Bots",
                value=cc.get("response", ""),
                key=f"ccr_{i}",
                height=100,
                placeholder="z.B. Unsere Serverregeln findest du hier: ..."
            )
    settings["custom_commands"] = st.session_state.cc_list

# ─── SPEICHERN-BUTTON ───────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; margin-bottom:10px;'>
    <p style='color:#94a3b8; font-size:14px;'>💾 Speichern uebernimmt alle Einstellungen ausser Veroeffentlichungen - diese werden sofort gesendet.</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("💾 ALLE EINSTELLUNGEN SPEICHERN", type="primary", use_container_width=True):
        save_settings(settings)
        st.success("✅ Einstellungen erfolgreich gespeichert! Der Bot uebernimmt die Aenderungen sofort.")
        st.balloons()
        st.rerun()
