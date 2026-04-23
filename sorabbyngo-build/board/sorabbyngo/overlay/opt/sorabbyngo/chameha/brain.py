"""
brain.py — Chameha Brain
Receives all OS events via event bus
Normalizes, prioritizes, routes
Decides: show to user / log silently / escalate
"""

import time
import json
import os
import threading
from typing import Optional
from event_bus import EventBus, ChamehaEvent, EventType, Severity

AUDIT_DIR  = "/opt/sorabbyngo/chameha/audit"
AUDIT_FILE = os.path.join(AUDIT_DIR, "events.jsonl")

# How long to suppress duplicate events from same source (seconds)
DEDUP_WINDOW = 30


class Brain:
    def __init__(self, event_bus: EventBus, identity, config):
        self.bus      = event_bus
        self.identity = identity
        self.config   = config

        self._lock         = threading.Lock()
        self._last_seen    = {}   # source -> last timestamp (dedup)
        self._ui_callbacks = []   # registered by main.py UI layer
        self._ask_callback = None # registered by conversation layer

        # subscribe to all events
        self.bus.subscribe(self._handle)

    # ------------------------------------------------------------------
    # Registration — UI and conversation layer hook in here
    # ------------------------------------------------------------------

    def on_surface(self, callback):
        """UI registers here to receive events that should be shown"""
        self._ui_callbacks.append(callback)

    def on_ask(self, callback):
        """Conversation layer registers here for ASK events"""
        self._ask_callback = callback

    # ------------------------------------------------------------------
    # Core handler
    # ------------------------------------------------------------------

    def _handle(self, event: ChamehaEvent):
        self._audit(event)

        if self._is_duplicate(event):
            return

        self._record_seen(event)

        if event.event_type == EventType.LOCK:
            self._route_lock(event)
        elif event.event_type == EventType.ASK:
            self._route_ask(event)
        elif event.event_type == EventType.NOTIFY:
            self._route_notify(event)

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    def _route_lock(self, event: ChamehaEvent):
        """LOCK — always surfaces to user, highest priority"""
        msg = self._format_for_user(event)
        self._surface(msg, event)

    def _route_ask(self, event: ChamehaEvent):
        """ASK — route to conversation layer if available"""
        if self._ask_callback:
            try:
                self._ask_callback(event)
            except Exception:
                self._surface(self._format_for_user(event), event)
        else:
            self._surface(self._format_for_user(event), event)

    def _route_notify(self, event: ChamehaEvent):
        """NOTIFY — only surface HIGH and CRITICAL, swallow the rest"""
        if event.should_surface():
            self._surface(self._format_for_user(event), event)
        # LOW and MEDIUM are already audited, nothing more to do

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    def _format_for_user(self, event: ChamehaEvent) -> str:
        """
        Convert raw OS event into clean human language
        No raw logs, no technical noise
        """
        source_label = self._source_label(event.source)

        if event.event_type == EventType.LOCK:
            parts = [f"\n  [{source_label}] {event.message}"]
            if event.action_taken:
                parts.append(f"  Action taken: {event.action_taken}")
            if event.confidence:
                parts.append(f"  Confidence: {int(event.confidence * 100)}%")
            parts.append("  Defense updated.")
            return "\n".join(parts)

        if event.event_type == EventType.ASK:
            return f"\n  [{source_label}] {event.message}\n  Your input is needed."

        # NOTIFY HIGH/CRITICAL
        return f"\n  [{source_label}] {event.message}"

    def _source_label(self, source: str) -> str:
        labels = {
            "sentinel.core":    "Sentinel",
            "sentinel.red":     "Sentinel",
            "sentinel.blue":    "Sentinel",
            "byngox.agent":     "Byngox",
            "byngox.health":    "Health Monitor",
            "byngonet.mesh":    "Byngonet",
            "byngonet.trust":   "Byngonet",
            "hal.sensors":      "HAL",
            "hal.nodeid":       "Device Identity",
            "novela.risk":      "Health Risk",
        }
        return labels.get(source, source.split(".")[0].capitalize())

    # ------------------------------------------------------------------
    # Deduplication
    # ------------------------------------------------------------------

    def _is_duplicate(self, event: ChamehaEvent) -> bool:
        with self._lock:
            last = self._last_seen.get(event.source)
            if last is None:
                return False
            return (event.timestamp - last) < DEDUP_WINDOW

    def _record_seen(self, event: ChamehaEvent):
        with self._lock:
            self._last_seen[event.source] = event.timestamp

    # ------------------------------------------------------------------
    # Surface to UI
    # ------------------------------------------------------------------

    def _surface(self, message: str, event: ChamehaEvent):
        for cb in self._ui_callbacks:
            try:
                cb(message, event)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Audit trail — every event logged, no exceptions
    # ------------------------------------------------------------------

    def _audit(self, event: ChamehaEvent):
        try:
            os.makedirs(AUDIT_DIR, exist_ok=True)
            record = event.to_dict()
            record["node_id"] = self.identity.node_id
            with open(AUDIT_FILE, "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception:
            pass  # audit must never crash Chameha
