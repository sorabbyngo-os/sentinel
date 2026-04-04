# Phase 2 — Root Filesystem

**Status:** 🔜 Next

## Goal
Build a minimal root filesystem using Buildroot.
No Debian. No Kali. Pure Sorabbyngo from init to shell.

## Tool
**Buildroot 2024.02**

## Config Decisions
| Option | Choice | Reason |
|---|---|---|
| Architecture | x86_64 | Matches our kernel |
| Init system | systemd | Needed for Novela/Chameha services |
| C library | glibc | Python 3.12 compatibility |
| Shell | bash | Chameha runtime needs it |
| Package manager | none | Sovereign, no external deps |
| Python | 3.12 | Novela + AI runtime |
| External kernel | 6.19.10-sorabbyngo | Use ours, not Buildroots |

## Target Output
-  — bootable ext4 root filesystem
-  — bootable ISO for deployment

## Steps
1. Download and configure Buildroot
2. Point at our external kernel
3. Build minimal rootfs — prove TTY boots
4. Add Sorabbyngo overlay (init scripts, NodeID reader, Chameha boot)
5. Add Python 3.12 + Novela dependencies
6. Add Tier 1 local LLM runtime (llama.cpp)
7. Build final ISO
