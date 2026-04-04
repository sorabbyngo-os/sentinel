# Phase 6 — Installer

**Status:** 🔜 Planned

## Goal
A minimal graphical installer that runs from the ISO
and installs SORABBYNGO OS to the target device.

## Requirements
- Runs before Chameha (pre-install environment)
- Detects target disk automatically
- Configures NodeID on first boot
- Sets up Byngonet mesh identity
- Launches Chameha on first successful boot

## Flow
```
Boot ISO
    → Installer (minimal Chameha UI)
        → Select disk
        → Flash rootfs
        → Configure NodeID
        → Reboot
            → First boot Chameha experience
```
