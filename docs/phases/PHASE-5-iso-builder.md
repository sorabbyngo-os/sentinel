# Phase 5 — ISO/Image Builder

**Status:** 🔜 Planned

## Goal
Produce a bootable ISO that can be flashed to Novela devices.

## Output Formats
-  — for USB boot and testing
-  — for direct flash to eMMC/SD on Novela devices
-  — for over-the-air updates via Byngonet

## Build Pipeline
```
kernel (bzImage)
    + rootfs (Buildroot ext4)
    + Sorabbyngo overlay
    + Tier 1 AI model
    → GRUB bootloader
    → sorabbyngo-os-v1.0.iso
```
