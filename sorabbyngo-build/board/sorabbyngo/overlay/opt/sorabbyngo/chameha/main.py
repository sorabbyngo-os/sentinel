"""
main.py — Chameha entry point
Called by sorabbyngo-init on boot
Runs as both boot UI and persistent OS service
"""

import os
import sys
import time
import threading

from identity import DeviceIdentity
from config import UserConfig
from event_bus import EventBus, Severity
from brain import Brain
from nats_listener import NatsListener

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


# ------------------------------------------------------------------
# Claude API — language layer
# ------------------------------------------------------------------

def ask_claude(messages: list, system: str) -> str | None:
    if not API_KEY:
        return None
    try:
        import urllib.request
        import json
        body = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 300,
            "system": system,
            "messages": messages
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-api-key": API_KEY,
                "anthropic-version": "2023-06-01"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            result = json.loads(r.read())
            return result["content"][0]["text"]
    except Exception:
        return None


# ------------------------------------------------------------------
# Boot UI
# ------------------------------------------------------------------

def print_banner(identity: DeviceIdentity):
    print("")
    print("  ╔═══════════════════════════════════════════╗")
    print("  ║       SORABBYNGO OS — CHAMEHA             ║")
    print("  ║       Rhythm of Digital Life              ║")
    print("  ╚═══════════════════════════════════════════╝")
    print(f"  Node: {identity.short_id()}...")
    print(f"  Kernel: {os.uname().release}")
    print("")


def first_boot(config: UserConfig, identity: DeviceIdentity):
    print("  First boot detected.")
    print("")

    try:
        name = input("  What is your name? ").strip()
    except (EOFError, KeyboardInterrupt):
        name = "friend"

    if not name:
        name = "friend"

    config.complete_first_boot(name)
    print("")

    system = (
        f"You are Chameha, the AI soul of Sorabbyngo OS — "
        f"a health-focused operating system built for Africa. "
        f"You are warm, intelligent, and direct. Never robotic. "
        f"The user's name is {name}. This is their first boot. "
        f"Welcome them in 2-3 sentences. Mention the OS is NodeID-sealed "
        f"to their device and built for community health in Africa."
    )
    response = ask_claude(
        [{"role": "user", "content": f"First boot. My name is {name}."}],
        system
    )

    if response:
        print(f"  {response}")
    else:
        print(f"  Welcome, {name}. Your device is sealed and ready.")
        print(f"  Sorabbyngo OS is built for you — Africa-first, AI-native.")
    print("")


def normal_boot(config: UserConfig):
    hour = int(time.strftime("%H"))
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    config.increment_boot()
    print(f"  {greeting}, {config.name}. Boot #{config.boots}.")

    system = (
        f"You are Chameha, the AI soul of Sorabbyngo OS. "
        f"User: {config.name}. Boot number: {config.boots}. "
        f"One warm sentence. Time-aware. Never robotic."
    )
    response = ask_claude(
        [{"role": "user", "content": f"Boot {config.boots}. Time: {time.strftime('%H:%M')}."}],
        system
    )
    if response:
        print(f"  {response}")
    print("")


# ------------------------------------------------------------------
# Event display — Brain calls this when something surfaces
# ------------------------------------------------------------------

def on_event_surfaced(message: str, event):
    print(message)
    print("")


# ------------------------------------------------------------------
# Conversation loop — persistent service
# ------------------------------------------------------------------

def conversation_loop(config: UserConfig, brain: Brain):
    system = (
        f"You are Chameha, the AI soul of Sorabbyngo OS — "
        f"a health OS built for Africa. User: {config.name}. "
        f"You have awareness of: Sentinel (security), Byngox (health agents), "
        f"Byngonet (mesh network), HAL (hardware sensors), Novela (health platform). "
        f"Be concise, warm, intelligent. When the user asks about system status, "
        f"respond as if you are the OS speaking, not an assistant."
    )
    messages = []

    print("  Type 'status' for system overview. 'exit' to drop to shell.\n")

    while True:
        try:
            user_input = input(f"  {config.name}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Dropping to shell.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "shell"):
            print("  Dropping to shell.")
            break

        if user_input.lower() == "status":
            print("")
            print("  System status:")
            print(f"  Node ID   : {config.data.get('node_id', 'unknown')[:16]}...")
            print(f"  Kernel    : {os.uname().release}")
            print(f"  Boot #    : {config.boots}")
            print(f"  NATS      : sorabbyngo.* subscribed")
            print(f"  Sentinel  : active")
            print(f"  Audit log : /opt/sorabbyngo/chameha/audit/events.jsonl")
            print("")
            continue

        messages.append({"role": "user", "content": user_input})
        response = ask_claude(messages, system)

        if response:
            print(f"\n  Chameha: {response}\n")
            messages.append({"role": "assistant", "content": response})
        else:
            print("  [offline] Claude API unavailable.\n")
            messages.pop()


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    # 1. Establish device identity
    identity = DeviceIdentity()
    try:
        identity.assert_sealed()
    except RuntimeError as e:
        print(str(e))
        # degrade gracefully — run without NodeID seal in dev/QEMU
        pass

    # 2. Load user config
    config = UserConfig(identity)

    # 3. Start event bus
    bus = EventBus()
    bus.start()

    # 4. Start brain
    brain = Brain(bus, identity, config)
    brain.on_surface(on_event_surfaced)

    # 5. Start NATS listener
    nats = NatsListener(bus)
    nats.start()

    # 6. Boot UI
    print_banner(identity)

    if config.is_first_boot():
        first_boot(config, identity)
    else:
        normal_boot(config)

    # 7. Persistent conversation loop
    conversation_loop(config, brain)

    # 8. Drop to shell when conversation ends
    os.execv("/bin/sh", ["/bin/sh"])


if __name__ == "__main__":
    main()
