"""
nats_listener.py — Chameha NATS subscriber
Listens to sorabbyngo.* subject hierarchy
Translates raw NATS messages into ChamehaEvents
Feeds them into the event bus
"""

import json
import threading
import time
from event_bus import EventBus, ChamehaEvent, EventType, Severity

# NATS subject → (source, event_type, severity) mapping
SUBJECT_MAP = {
    "sorabbyngo.cyberwall.alert":    ("sentinel.core",  EventType.LOCK,   Severity.CRITICAL),
    "sorabbyngo.sentinel.threat":    ("sentinel.core",  EventType.LOCK,   Severity.CRITICAL),
    "sorabbyngo.sentinel.escalation":("sentinel.red",   EventType.LOCK,   Severity.CRITICAL),
    "sorabbyngo.security.summary":   ("sentinel.blue",  EventType.NOTIFY, Severity.MEDIUM),
    "sorabbyngo.sentinel.threat":    ("sentinel.core",  EventType.LOCK,   Severity.CRITICAL),
    "sorabbyngo.sentinel.contained": ("sentinel.blue",  EventType.NOTIFY, Severity.HIGH),
    "sorabbyngo.sentinel.learned":   ("sentinel.brain", EventType.NOTIFY, Severity.LOW),
    "sorabbyngo.byngox.risk":        ("byngox.health",  EventType.NOTIFY, Severity.HIGH),
    "sorabbyngo.byngox.update":      ("byngox.agent",   EventType.NOTIFY, Severity.LOW),
    "sorabbyngo.byngonet.mesh":      ("byngonet.mesh",  EventType.NOTIFY, Severity.MEDIUM),
    "sorabbyngo.byngonet.trust":     ("byngonet.trust", EventType.NOTIFY, Severity.LOW),
    "sorabbyngo.hal.sensors":        ("hal.sensors",    EventType.NOTIFY, Severity.LOW),
    "sorabbyngo.novela.risk":        ("novela.risk",    EventType.NOTIFY, Severity.HIGH),
}

NATS_HOST = "127.0.0.1"
NATS_PORT = 4222


class NatsListener:
    def __init__(self, event_bus: EventBus):
        self.bus      = event_bus
        self._running = False
        self._thread  = None
        self._sock    = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(
            target=self._connect_loop,
            daemon=True,
            name="chameha-nats-listener"
        )
        self._thread.start()

    def stop(self):
        self._running = False

    # ------------------------------------------------------------------
    # Connection loop — reconnects automatically if NATS is unavailable
    # ------------------------------------------------------------------

    def _connect_loop(self):
        while self._running:
            try:
                self._run()
            except Exception:
                # NATS not available — retry in 5s, Chameha keeps running
                time.sleep(5)

    def _run(self):
        import socket
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(2)
        self._sock.connect((NATS_HOST, NATS_PORT))
        self._sock.settimeout(None)

        # NATS protocol handshake
        self._sock.recv(1024)  # INFO line
        self._sock.sendall(b'CONNECT {"verbose":false,"pedantic":false}\r\n')

        # Subscribe to all sorabbyngo subjects
        for i, subject in enumerate(SUBJECT_MAP.keys()):
            self._sock.sendall(
                f'SUB {subject} {i}\r\n'.encode()
            )

        # Read messages
        buf = ""
        while self._running:
            chunk = self._sock.recv(4096).decode("utf-8", errors="ignore")
            if not chunk:
                break
            buf += chunk
            buf = self._process_buffer(buf)

    def _process_buffer(self, buf: str) -> str:
        while "\r\n" in buf:
            line, buf = buf.split("\r\n", 1)
            if line.startswith("MSG "):
                parts = line.split()
                if len(parts) >= 4:
                    subject  = parts[1]
                    byte_len = int(parts[3])
                    if len(buf) >= byte_len:
                        payload = buf[:byte_len]
                        buf     = buf[byte_len:]
                        if buf.startswith("\r\n"):
                            buf = buf[2:]
                        self._dispatch(subject, payload)
        return buf

    def _dispatch(self, subject: str, payload: str):
        mapping = SUBJECT_MAP.get(subject)
        if not mapping:
            return

        source, event_type, severity = mapping

        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            data = {"raw": payload}

        event = ChamehaEvent(
            source=source,
            event_type=event_type,
            severity=severity,
            message=data.get("message", f"Event from {source}"),
            action_taken=data.get("action_taken"),
            confidence=data.get("confidence"),
            payload=data
        )

        self.bus.publish(event)
