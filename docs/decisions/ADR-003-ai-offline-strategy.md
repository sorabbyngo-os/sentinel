# ADR-003 — AI Offline Strategy

**Status:** Accepted  
**Date:** 2026-04-04  
**Deciders:** Charles (Founder & CEO)

## Decision
**Offline-first, tiered intelligence system.**

Not cloud-only. Not fully local. A layered system that degrades gracefully.

## Tier System

### Tier 1 — Core Local Intelligence (Always Available)
Runs fully offline on every Sorabbyngo device:
- Small LLM (3B–8B class) — LLaMA / Phi-class
- Capabilities:
  - Conversation and reasoning (limited but reliable)
  - System control and Chameha interaction
  - Novela basic medical logic and triage
- This is the minimum viable intelligence layer

### Tier 2 — Enhanced Local Models (Optional)
Activated when device has GPU/NPU:
- Larger models (8B–13B+)
- Better reasoning, longer context
- More accurate health insights
- Does not require internet

### Tier 3 — Enhanced Intelligence (Byngox Prime, When Connected)
Byngox Prime + remote backends:
- Deep reasoning and complex diagnosis
- Large medical knowledge queries
- Continuous learning and model updates
- Multi-device sync via Byngonet

## The Key Rule
> The system must NEVER feel broken without internet.
> Only less powerful.

## Runtime Stack
```
Tier 3: Byngox Prime vLLM (self-hosted) ←— enhanced connectivity
    ↑ fallback
Tier 2: Local large model (llama.cpp / GPU)
    ↑ fallback  
Tier 1: Local small model (always running)
```

## Consequences
- llama.cpp or equivalent must be in the rootfs
- Tier 1 model ships with the OS image
- Intelligence router must detect connectivity and route accordingly
- Chameha handles tier transitions transparently — user never sees failure
