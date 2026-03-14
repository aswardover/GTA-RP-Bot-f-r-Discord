# -*- coding: utf-8 -*-
"""Audit-Log und Undo-Snapshot Funktionen."""

import json
import datetime
import streamlit as st
from copy import deepcopy

from utils.settings_io import _safe_read_json

AUDIT_LOG_FILE = "dashboard_audit.json"


# ── Audit-Log ────────────────────────────────────────────────────

def _append_audit_entry(module, action, details=None, status="ok"):
    entries = _safe_read_json(AUDIT_LOG_FILE, [])
    if not isinstance(entries, list):
        entries = []

    actor_id = str(st.session_state.get("user_id") or "unknown")
    server_key = str(st.session_state.get("active_server_key") or "default")
    server_label = str(st.session_state.get("active_server_label") or "-")
    entry = {
        "ts": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "module": str(module),
        "action": str(action),
        "status": str(status),
        "server_key": server_key,
        "server_label": server_label,
        "actor_id": actor_id,
        "details": str(details or ""),
    }
    entries.insert(0, entry)
    entries = entries[:500]
    with open(AUDIT_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def _read_audit_entries(server_key=None, limit=100):
    entries = _safe_read_json(AUDIT_LOG_FILE, [])
    if not isinstance(entries, list):
        return []
    if server_key:
        entries = [e for e in entries if isinstance(e, dict) and str(e.get("server_key")) == str(server_key)]
    return entries[:max(1, int(limit))]


# ── Undo-Snapshots ───────────────────────────────────────────────

def _push_undo_snapshot(settings, snapshot_key, payload):
    undo_root = settings.get("dashboard_undo", {}) if isinstance(settings.get("dashboard_undo"), dict) else {}
    stack = undo_root.get(snapshot_key, []) if isinstance(undo_root.get(snapshot_key), list) else []
    stack.append(deepcopy(payload))
    undo_root[snapshot_key] = stack[-5:]
    settings["dashboard_undo"] = undo_root


def _pop_undo_snapshot(settings, snapshot_key):
    undo_root = settings.get("dashboard_undo", {}) if isinstance(settings.get("dashboard_undo"), dict) else {}
    stack = undo_root.get(snapshot_key, []) if isinstance(undo_root.get(snapshot_key), list) else []
    if not stack:
        return None
    payload = stack.pop()
    undo_root[snapshot_key] = stack
    settings["dashboard_undo"] = undo_root
    return payload
