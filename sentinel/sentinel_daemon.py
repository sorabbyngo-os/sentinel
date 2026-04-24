"""
Sorabbyngo Sentinel Daemon — Wired Version
Fixes:
  1. Uses port 4223 (JetStream NATS) not 4222
  2. Watches Novela, Byngox, Gateway, CML, novela-monitors heartbeats
  3. Publishes heartbeat requests to all services
  4. Alerts on missing heartbeats

Run:
  NATS_URL=nats://localhost:4223 python3 sentinel_wired.py
"""

import asyncio
import json
import logging
import os
import signal
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import nats
    NATS_AVAILABLE = True
except ImportError:
    NATS_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
log = logging.getLogger("sentinel")

NATS_URL = os.environ.get("NATS_URL", "nats://localhost:4223")

BANNER = """
╔══════════════════════════════════════════════════════════╗
║       Sorabbyngo Sentinel — System Watchdog              ║
║       Watching: Novela · Byngox · CML · Gateway · CW     ║
╚══════════════════════════════════════════════════════════╝
"""

# ── Subjects ──────────────────────────────────────────────────────────────────
SUBJECTS = {
    # Inbound — services publish to these
    "heartbeat":        "sorabbyngo.*.heartbeat",
    "cw_alert":         "sorabbyngo.cyberwall.alert",
    "cml_audit":        "sorabbyngo.cml.audit.verify",
    "vitals_alert":     "novela.monitors.alerts.>",
    "twin_updated":     "health.twin.updated",
    "byngox_health":    "byngox.health.analyse",

    # Outbound — sentinel publishes to these
    "health":           "sorabbyngo.sentinel.health",
    "escalation":       "sorabbyngo.sentinel.escalation",
    "heartbeat_req":    "sorabbyngo.sentinel.heartbeat_request",
}

# Services sentinel watches
WATCHED_SERVICES = {
    "novela":           {"timeout": 120, "last_seen": 0, "critical": True},
    "byngox":           {"timeout": 60,  "last_seen": 0, "critical": True},
    "cml":              {"timeout": 60,  "last_seen": 0, "critical": True},
    "novela-monitors":  {"timeout": 30,  "last_seen": 0, "critical": False},
    "cyberwall":        {"timeout": 120, "last_seen": 0, "critical": False},
    "chameha":          {"timeout": 120, "last_seen": 0, "critical": False},
}


class SentinelDaemon:

    def __init__(self):
        self._nc       = None
        self._running  = False
        self._services = dict(WATCHED_SERVICES)
        self._ledger   = []   # In-memory audit log

    async def start(self):
        self._running = True
        print(BANNER)
        log.info("Sentinel starting — NATS: %s", NATS_URL)

        if not NATS_AVAILABLE:
            log.error("nats-py not installed — pip install nats-py")
            return

        await self._connect()

        tasks = [
            asyncio.create_task(self._watchdog_loop(),   name="watchdog"),
            asyncio.create_task(self._heartbeat_loop(),  name="heartbeat"),
            asyncio.create_task(self._health_loop(),     name="health_broadcast"),
        ]

        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: [t.cancel() for t in tasks])

        log.info("Sentinel online — watching %d services", len(self._services))
        self._record("sentinel_start", {"nats": NATS_URL})

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            log.info("Sentinel shutting down...")
        finally:
            self._record("sentinel_stop", {})
            if self._nc:
                await self._nc.close()

    async def _connect(self):
        try:
            self._nc = await nats.connect(
                NATS_URL,
                max_reconnect_attempts=-1,
                reconnect_time_wait=3,
                disconnected_cb=self._on_disconnect,
                reconnected_cb=self._on_reconnect,
            )
            log.info("Connected to NATS at %s", NATS_URL)
            await self._subscribe_all()
        except Exception as e:
            log.error("NATS connection failed: %s", e)

    async def _subscribe_all(self):
        await self._nc.subscribe(SUBJECTS["heartbeat"],    cb=self._on_heartbeat)
        await self._nc.subscribe(SUBJECTS["cw_alert"],     cb=self._on_cw_alert)
        await self._nc.subscribe(SUBJECTS["vitals_alert"], cb=self._on_vitals_alert)
        await self._nc.subscribe(SUBJECTS["twin_updated"], cb=self._on_twin_updated)
        log.info("Subscribed to all Sorabbyngo subjects")

    # ── Message handlers ──────────────────────────────────────────────────────

    async def _on_heartbeat(self, msg):
        """Service heartbeat received — mark as alive."""
        try:
            data    = json.loads(msg.data.decode())
            service = data.get("service") or msg.subject.split(".")[1]
            if service in self._services:
                self._services[service]["last_seen"] = time.time()
                log.debug("Heartbeat: %s", service)
        except Exception as e:
            log.error("Heartbeat error: %s", e)

    async def _on_cw_alert(self, msg):
        """Cyberwall threat alert — escalate if high severity."""
        try:
            data  = json.loads(msg.data.decode())
            level = data.get("level", "LOW")
            score = float(data.get("score", 0))
            self._services["cyberwall"]["last_seen"] = time.time()
            self._record("cyberwall_alert", data)

            if level in ("HIGH", "CRITICAL") or score >= 7.0:
                log.warning("[Sentinel] ESCALATING CW alert: %s score=%.1f",
                            data.get("threat_type"), score)
                await self._escalate(
                    f"Cyberwall {level} threat: {data.get('threat_type')}",
                    data
                )
        except Exception as e:
            log.error("CW alert error: %s", e)

    async def _on_vitals_alert(self, msg):
        """Clinical alert from novela-monitors — log and escalate if CODE."""
        try:
            data  = json.loads(msg.data.decode())
            level = data.get("alert_level", "normal")
            self._services["novela-monitors"]["last_seen"] = time.time()

            if level == "code":
                log.warning("[Sentinel] CODE ALERT — Patient: %s Ward: %s/%s",
                            data.get("patient_id"), data.get("ward"), data.get("bed"))
                await self._escalate(f"CODE clinical alert: {data.get('patient_id')}", data)
            self._record("vitals_alert", {
                "patient_id":  data.get("patient_id"),
                "alert_level": level,
                "ward":        data.get("ward"),
            })
        except Exception as e:
            log.error("Vitals alert error: %s", e)

    async def _on_twin_updated(self, msg):
        """Byngox twin update — confirms Byngox is alive."""
        try:
            data = json.loads(msg.data.decode())
            self._services["byngox"]["last_seen"] = time.time()
            risk = data.get("risk_label", "unknown")
            if risk == "critical":
                log.warning("[Sentinel] CRITICAL twin risk: %s", data.get("patient_ref"))
        except Exception as e:
            log.error("Twin update error: %s", e)

    # ── Watchdog ──────────────────────────────────────────────────────────────

    async def _watchdog_loop(self):
        """Check service health every 30 seconds."""
        while self._running:
            await asyncio.sleep(30)
            now  = time.time()
            dead = []
            for service, info in self._services.items():
                last = info["last_seen"]
                if last == 0:
                    continue   # Never seen — may not be deployed
                age = now - last
                if age > info["timeout"]:
                    dead.append(service)
                    severity = "CRITICAL" if info["critical"] else "WARNING"
                    log.warning("[Sentinel][%s] %s unresponsive for %.0fs",
                                severity, service, age)

            if dead:
                self._record("services_dead", {"services": dead})
                if any(self._services[s]["critical"] for s in dead):
                    await self._escalate(
                        f"Critical services unresponsive: {', '.join(dead)}",
                        {"dead_services": dead}
                    )

    async def _heartbeat_loop(self):
        """Request heartbeats from all services every 30 seconds."""
        while self._running:
            await asyncio.sleep(30)
            if not self._nc:
                continue
            try:
                await self._nc.publish(
                    SUBJECTS["heartbeat_req"],
                    json.dumps({
                        "from":      "sentinel",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }).encode()
                )
            except Exception as e:
                log.error("Heartbeat request error: %s", e)

    async def _health_loop(self):
        """Broadcast sentinel health every 60 seconds."""
        while self._running:
            await asyncio.sleep(60)
            if not self._nc:
                continue
            try:
                await self._nc.publish(
                    SUBJECTS["health"],
                    json.dumps({
                        "node":      "sentinel",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "services":  {
                            s: {
                                "last_seen_ago": int(time.time() - i["last_seen"]) if i["last_seen"] else None,
                                "critical":      i["critical"],
                            }
                            for s, i in self._services.items()
                        },
                        "audit_entries": len(self._ledger),
                    }).encode()
                )
            except Exception as e:
                log.error("Health broadcast error: %s", e)

    # ── Escalation ────────────────────────────────────────────────────────────

    async def _escalate(self, reason: str, data: dict):
        if not self._nc:
            return
        try:
            await self._nc.publish(
                SUBJECTS["escalation"],
                json.dumps({
                    "reason":    reason,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "data":      data,
                }).encode()
            )
            self._record("escalation", {"reason": reason})
        except Exception as e:
            log.error("Escalation error: %s", e)

    # ── Audit ─────────────────────────────────────────────────────────────────

    def _record(self, event: str, data: dict):
        entry = {
            "event":     event,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data":      data,
        }
        self._ledger.append(entry)
        log.info("[Audit] %s", event)

    # ── NATS callbacks ────────────────────────────────────────────────────────

    async def _on_disconnect(self):
        log.warning("NATS disconnected")

    async def _on_reconnect(self):
        log.info("NATS reconnected — resubscribing")
        await self._subscribe_all()


if __name__ == "__main__":
    asyncio.run(SentinelDaemon().start())
