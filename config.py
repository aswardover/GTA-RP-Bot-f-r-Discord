# -*- coding: utf-8 -*-
"""
Konfigurationsdatei fuer den GTA RP Bot
"""

# ========================================
# GUILD / SERVER KONFIGURATION
# ========================================
GUILD_ID = 678706941014573059

# ========================================
# BOT IDENTITAET
# ========================================
BOT_NAME = "Asward-Helper"
BOT_LOGO_URL = None

# ========================================
# FARBEN (Hex-Format)
# ========================================
COLOR_PRIMARY = 0x38bdf8
COLOR_SUCCESS = 0x22c55e
COLOR_ERROR   = 0xef4444
COLOR_WARNING = 0xf59e0b
COLOR_INFO    = 0x6366f1

# ========================================
# WELCOME/GOODBYE
# ========================================
WELCOME_CHANNEL_ID = None
WELCOME_MESSAGE = "👋 Willkommen {user} auf **{server}**!"
WELCOME_ROLE_ID = None

GOODBYE_CHANNEL_ID = None
GOODBYE_MESSAGE = "👋 {user} hat den Server verlassen. Bis bald!"

# ========================================
# LOGGING
# ========================================
LOG_CHANNEL_ID = None
RANKUP_CHANNEL_ID = None
RANKUP_MESSAGE = "{user} wurde befoerdert! Von **{old_rank}** auf **{new_rank}**! 🎉"

# ========================================
# STEMPELUHR
# ========================================
STEMPELUHR_CHANNEL_ID = None
STEMPELUHR_ALLOWED_ROLES = []
STEMPELUHR_NOTIFY_AFTER_HOURS = 8

# ========================================
# TICKET-SYSTEM
# ========================================
TICKET_STAFF_ROLES = []
TICKET_CATEGORIES = {
    "bewerbung":  {"name": "Bewerbung",        "emoji": "📝", "role_id": None, "category_id": None},
    "support":    {"name": "Support",           "emoji": "🆘", "role_id": None, "category_id": None},
    "whitelist":  {"name": "Whitelist-Antrag",  "emoji": "✅", "role_id": None, "category_id": None},
    "beschwerde": {"name": "Beschwerde",        "emoji": "⚠️", "role_id": None, "category_id": None},
}
