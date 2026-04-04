# Phase 3 — Init System

**Status:** 🔜 Planned

## Goal
Define the full systemd service graph for SORABBYNGO OS.

## Boot Order
```
1. kernel init
2. systemd starts
3. hardware services (udev, network)
4. sorabbyngo-nodeid.service  — reads and exports NodeID
5. byngonet.service           — mesh identity layer
6. novela.service             — health platform core
7. chameha.service            — AI personality + Wayland compositor
8. graphical.target           — system ready
```

## Key Services
| Service | Type | Depends on |
|---|---|---|
| sorabbyngo-nodeid | oneshot | kernel |
| byngonet | simple | sorabbyngo-nodeid |
| novela | notify | byngonet, network |
| chameha | simple | novela |
