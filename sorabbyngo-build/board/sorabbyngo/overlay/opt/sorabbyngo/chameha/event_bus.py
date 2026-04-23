"""
event_bus.py — Chameha event bus
The ONLY way OS components communicate with Chameha
Three event types: NOTIFY, ASK, LOCK
No component talks to the user except through here
"""

import json
import time
import queue
import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Callable

class EventType(Enum):
    NOTIFY = "NOTIFY"   # inform only, no user action needed
    ASK    = "ASK"      # ambiguous — needs user confirmation
    LOCK   = "LOCK"     # system locked — tell user what happened

class Severity(Enum):
    LOW      = 1
    MEDIUM   = 2
    HIGH     = 3
    CRITICAL = 4

@dataclass
class ChamehaEvent:
    source:       str                    # e.g. "sentinel.core", "byngox.agent"
    event_type:   EventType
    severity:     Severity
    message:      str                    # human-readable summary
    action_taken: Optional[str] = None  # what the OS already did
    confidence:   Optional[float] = None
    payload:      dict = field(default_factory=dict)
    timestamp:    float = field(default_factory=time.time)

    def to_dict(self):
        return {
            "source":       self.source,
            "event_type":   self.event_type.value,
            "severity":     self.severity.value,
            "message":      self.message,
            "action_taken": self.action_taken,
            "confidence":   self.confidence,
            "payload":      self.payload,
            "timestamp":    self.timestamp
        }

    def should_surface(self):
        """Only HIGH and CRITICAL events reach the user"""
        return self.severity.value >= Severity.HIGH.value

    def __repr__(self):
        return (f"[{self.event_type.value}] {self.source} "
                f"(sev={self.severity.name}): {self.message}")


class EventBus:
    def __init__(self):
        self._queue = queue.PriorityQueue()
        self._handlers: list[Callable] = []
        self._lock = threading.Lock()
        self._running = False
        self._thread = None

    def publish(self, event: ChamehaEvent):
        """Any OS component calls this to send an event"""
        priority = -event.severity.value  # higher severity = lower number = first out
        self._queue.put((priority, time.time(), event))

    def subscribe(self, handler: Callable):
        """Chameha brain subscribes to receive events"""
        with self._lock:
            self._handlers.append(handler)

    def start(self):
        """Start processing events in background thread"""
        self._running = True
        self._thread = threading.Thread(
            target=self._process_loop,
            daemon=True,
            name="chameha-event-bus"
        )
        self._thread.start()

    def stop(self):
        self._running = False

    def _process_loop(self):
        while self._running:
            try:
                _, _, event = self._queue.get(timeout=0.5)
                with self._lock:
                    for handler in self._handlers:
                        try:
                            handler(event)
                        except Exception as e:
                            pass  # never let a bad handler kill the bus
            except queue.Empty:
                continue


# Convenience functions for OS components to emit events

def notify(bus: EventBus, source: str, message: str,
           severity: Severity = Severity.LOW, **kwargs):
    bus.publish(ChamehaEvent(
        source=source,
        event_type=EventType.NOTIFY,
        severity=severity,
        message=message,
        **kwargs
    ))

def ask(bus: EventBus, source: str, message: str, **kwargs):
    bus.publish(ChamehaEvent(
        source=source,
        event_type=EventType.ASK,
        severity=Severity.HIGH,
        message=message,
        **kwargs
    ))

def lock(bus: EventBus, source: str, message: str,
         action_taken: str = None, **kwargs):
    bus.publish(ChamehaEvent(
        source=source,
        event_type=EventType.LOCK,
        severity=Severity.CRITICAL,
        message=message,
        action_taken=action_taken,
        **kwargs
    ))
