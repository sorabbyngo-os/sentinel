# ADR-001 — Boot Target

**Status:** Accepted  
**Date:** 2026-04-04  
**Deciders:** Charles (Founder & CEO)

## Decision
**Graphical Chameha boot as primary target. TTY as hidden fallback.**

## Context
Two fundamentally different products emerge from this decision:
- TTY-first → Linux distro with AI features
- Graphical-first → AI-native operating system

These are different categories. Sorabbyngo is the second.

## Architecture
```
Bootloader (GRUB)
    → Kernel (Linux 6.19.10-sorabbyngo)
        → init (systemd)
            → graphical.target (default)
                → Chameha (Wayland compositor + AI shell)
                    → Voice-first interaction from boot
```

## TTY Fallback
- TTY available on Ctrl+Alt+F2–F6 at all times
- Emergency shell on boot failure
- TTY is the debug layer, NOT the user interface

## Consequences
- Chameha must be production-stable before OS ships
- Wayland compositor required in rootfs
- systemd graphical.target as default — not multi-user.target
- Boot failure must gracefully fall to TTY, never hang
