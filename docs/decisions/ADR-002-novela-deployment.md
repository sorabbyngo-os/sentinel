# ADR-002 — Novela Deployment Model

**Status:** Accepted  
**Date:** 2026-04-04  
**Deciders:** Charles (Founder & CEO)

## Decision
**Hybrid — biased toward on-device core. Remote backend optional.**

## On-Device (Non-Negotiable)
Runs locally with zero internet:
- Patient interaction (chat + voice)
- Basic triage and health record viewing
- Local embeddings and memory
- Emergency decision logic
- Counterfeit medication detection (offline model)

## Remote Backend (Optional)
Used only when connected:
- Model upgrades and updates
- Heavy diagnostics
- Medical knowledge base updates
- Multi-user sync (hospitals, doctors, clinics)

## Why This Matters
| Scenario | Cloud-only | On-device |
|---|---|---|
| Rural Africa | ❌ Fails | ✅ Works |
| Poor connectivity | ❌ Fails | ✅ Works |
| Critical medical situation | ❌ Fails | ✅ Works |
| Hospital multi-user sync | ✅ Works | 🔄 Via Byngonet |

## Architecture
Novela runs as a **core system service**, not an app.
It starts at boot via systemd alongside Chameha.

## Consequences
- Novela must ship with an embedded local model
- Django backend compiles to run on-device
- Byngonet handles multi-device sync when available
- Cloud Claude API used only for Tier 3 intelligence
