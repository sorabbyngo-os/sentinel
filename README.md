# sorabbyngo-build
> **SORABBYNGO OS** — Build system, architecture decisions, and engineering roadmap
> *Rhythm of Digital Life* · Sorabbyngo Labs · Kisii, Kenya

## What is this repo?
This repository contains the master architecture decisions, phase plans, build system, and engineering roadmap for SORABBYNGO OS.

## Structure
```
docs/
├── decisions/          # Architecture decision records (ADRs)
│   ├── ADR-001-boot-target.md
│   ├── ADR-002-novela-deployment.md
│   └── ADR-003-ai-offline-strategy.md
├── phases/             # Build phases
│   ├── PHASE-1-kernel.md
│   ├── PHASE-2-rootfs.md
│   ├── PHASE-3-init.md
│   ├── PHASE-4-ai-runtime.md
│   ├── PHASE-5-iso-builder.md
│   └── PHASE-6-installer.md
└── architecture/       # System architecture
    └── SYSTEM-OVERVIEW.md
```

## Phase Status
| Phase | Description | Status |
|---|---|---|
| 1 | Custom kernel (Linux 6.19.10) | ✅ Complete |
| 2 | Root filesystem (Buildroot) | 🔜 Next |
| 3 | Init system (systemd) | 🔜 Planned |
| 4 | AI runtime layer | 🔜 Planned |
| 5 | ISO/image builder | 🔜 Planned |
| 6 | Installer | 🔜 Planned |

## Core Architecture Decisions
- Boot → Graphical Chameha (TTY hidden fallback)
- Novela → Core runs on-device + optional remote backend
- AI → Offline-first, tiered intelligence (local → enhanced → cloud)

© 2026 Sorabbyngo Company. All rights reserved.

## OS Surfaces (ADR-004)

All OS surfaces share the Sorabbyngo AI Kernel as root base.

| OS Surface | Target | Key Requirement | Status |
|---|---|---|---|
| Sorabbyngo OS | Base / development | Current build target | 🔧 In development |
| Novela OS | Medical / clinical | PREEMPT_RT real-time | 🔜 Planned |
| Byngo OS | Consumer devices | Android compatibility | 🔜 Planned |
| Edge OS | IoT / drones / vehicles | Minimal footprint | 🔜 Planned |
| Sentinel OS | Cybersecurity ops | Hardened kernel | 🔜 Planned |
| Server OS | Infrastructure | High throughput | 🔜 Planned |

See [ADR-004](docs/decisions/ADR-004-kernel-ecosystem-strategy.md) for full rationale.

## OS Surfaces (ADR-004)

All OS surfaces share the Sorabbyngo AI Kernel as root base.

| OS Surface | Target | Key Requirement | Status |
|---|---|---|---|
| Sorabbyngo OS | Base / development | Current build target | 🔧 In development |
| Novela OS | Medical / clinical | PREEMPT_RT real-time | 🔜 Planned |
| Byngo OS | Consumer devices | Android compatibility | 🔜 Planned |
| Edge OS | IoT / drones / vehicles | Minimal footprint | 🔜 Planned |
| Sentinel OS | Cybersecurity ops | Hardened kernel | 🔜 Planned |
| Server OS | Infrastructure | High throughput | 🔜 Planned |

See [ADR-004](docs/decisions/ADR-004-kernel-ecosystem-strategy.md) for full rationale.

<p align="center">
  <img src="./assets/banner.svg" alt="Sentinel" width="900"/>
</p>

<p align="center">
  <strong>Sentinel — Autonomous Security & Trust Platform</strong><br/>
  The Security Nervous System of SORABBYNGO OS
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Security-Autonomous-darkred?style=flat-square"/>
  <img src="https://img.shields.io/badge/Zero%20Trust-Enabled-darkred?style=flat-square"/>
  <img src="https://img.shields.io/badge/Offline-First-darkred?style=flat-square"/>
  <img src="https://img.shields.io/badge/AI-Assisted-darkred?style=flat-square"/>
  <img src="https://img.shields.io/badge/CML-Integrated-darkred?style=flat-square"/>
</p>

---

# Sentinel

Sentinel is the autonomous cybersecurity platform of **SORABBYNGO OS**.

It continuously monitors the operating system, applications, hardware, users, and network activity to detect, prevent, and respond to security threats in real time.

Unlike traditional antivirus software, Sentinel is deeply integrated into the operating system and works alongside HAL, CML, Byngonet, Byngox, and Chameha to provide continuous protection.

Its goal is not only to stop attacks, but also to understand system behaviour, detect anomalies, maintain trust, and recover safely from incidents.

---

# Responsibilities

- System integrity monitoring
- Threat detection
- Malware detection
- Intrusion detection
- Behaviour analysis
- Zero Trust enforcement
- Identity verification
- Device attestation
- Secure boot validation
- Runtime protection
- File integrity monitoring
- Memory protection
- Network monitoring
- Incident response
- Security auditing
- Recovery assistance

---

# System Architecture

```text
Applications
      │
      ▼
Chameha
      │
      ▼
Byngox
      │
      ▼
CML
      │
      ▼
Sentinel
      │
 ┌────┼────────────────────────────┐
 │    │        │        │          │
 ▼    ▼        ▼        ▼          ▼
HAL Byngonet Kernel FileSystem Hardware
```

Sentinel continuously observes every layer while cooperating with the operating system rather than interrupting it.

---

# Core Components

## Threat Engine

Detects malicious behaviour and evaluates risk.

## Integrity Monitor

Continuously verifies files, processes, drivers, firmware, and configuration.

## Runtime Protection

Protects running applications from exploitation.

## Trust Engine

Calculates trust scores for users, applications, devices, and network peers.

## Incident Manager

Coordinates detection, isolation, recovery, and reporting.

## Security Telemetry

Collects system-wide security events for analysis.

---

# Zero Trust

Sentinel assumes that no device, process, application, or user is automatically trusted.

Trust is continuously evaluated using:

- Identity
- Device health
- Behaviour
- Network posture
- Security history
- Policy compliance

---

# AI-Assisted Security

Sentinel uses Byngox for advanced reasoning while CML validates every autonomous response.

AI assists with:

- Threat classification
- Root cause analysis
- Incident prioritization
- Recovery planning
- Risk prediction

Security decisions remain governed by deterministic policies whenever possible.

---

# Features

- Offline-first security
- Continuous monitoring
- AI-assisted threat detection
- Zero Trust architecture
- Behavioural analytics
- Secure boot verification
- File integrity monitoring
- Process isolation
- Network protection
- Hardware attestation
- Autonomous incident response

---

# Repository Structure

```text
architecture/
docs/
agents/
detectors/
engine/
telemetry/
trust/
response/
policies/
tests/
```

---

# Development Status

## Completed

- Security architecture
- Threat model
- Zero Trust design
- Trust architecture
- Repository organization

## Next

- Detection engine
- Behaviour analysis
- Trust engine
- Response engine
- Hardware attestation
- Security telemetry

---

# Sorabbyngo Ecosystem

| Repository | Responsibility |
|------------|----------------|
| Sorabbyngo Base | Shared platform contracts |
| Chameha | User interaction and orchestration |
| Byngox | Specialized reasoning |
| Byngonet | Networking and synchronization |
| HAL | Hardware abstraction |
| CML | Safety, policy and governance |
| Sentinel | Security, trust and system protection |

---

## Design Philosophy

Security should not be an application that reacts after compromise.

It should be a continuously operating subsystem that understands the operating system, reasons about behaviour, collaborates with intelligent services, and protects every component without disrupting the user experience.

---

<p align="center">
<strong>Sorabbyngo Company</strong><br/>
<em>The Rhythm of Digital Life</em>
</p>
