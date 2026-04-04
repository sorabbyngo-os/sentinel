# SORABBYNGO OS — System Architecture Overview

**Version:** 1.0  
**Date:** 2026-04-04  
**Author:** Sorabbyngo Engineering

## Full Stack
```
┌─────────────────────────────────────────────────────┐
│                  USER EXPERIENCE                    │
│         Chameha — Wayland + Voice + AI Shell        │
├─────────────────────────────────────────────────────┤
│                APPLICATION LAYER                    │
│      Novela — On-device AI health platform          │
├─────────────────────────────────────────────────────┤
│               AI INTELLIGENCE LAYER                 │
│  Tier 1: Local LLM  │  Tier 2: GPU  │  Tier 3: API │
├─────────────────────────────────────────────────────┤
│                COGNITIVE LAYER                      │
│         Byngox — 12-agent swarm engine              │
│         CML — Safety and alignment                  │
├─────────────────────────────────────────────────────┤
│                 NETWORK LAYER                       │
│      Byngonet — Distributed mesh identity           │
├─────────────────────────────────────────────────────┤
│                  KERNEL LAYER                       │
│   Linux 6.19.10-sorabbyngo                          │
│   NodeID driver │ Byngonet driver │ Boot config     │
└─────────────────────────────────────────────────────┘
```

## Design Principles
1. **Offline-first** — core functionality never requires internet
2. **Identity-aware** — every node cryptographically identified from boot
3. **Africa-native** — designed for low connectivity, distributed deployment
4. **Sovereign** — data stays on-device by default
5. **Tiered intelligence** — graceful degradation, never broken

## Key Interfaces
| Interface | From | To | Protocol |
|---|---|---|---|
| Chameha-ByngoX | Chameha | Byngox | ACP v1.0 |
| Byngox-CML | Byngox | CML | Internal |
| CML-Novela | CML | Novela | REST/DRF |
| Novela-Byngonet | Novela | Byngonet | TCP mesh |
| NodeID export | Kernel | Userspace | /proc/sorabbyngo/nodeid |
| Byngonet stats | Kernel | Userspace | /proc/byngonet_stats |
