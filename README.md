# HCP Telegram Client

> The official Telegram client for the Humanitarian Connection Protocol (HCP).

![Status](https://img.shields.io/badge/status-draft-orange)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)
![Protocol](https://img.shields.io/badge/HCP-v0.1-green)

---

## Overview

This repository contains the reference Telegram client for the Humanitarian Connection Protocol (HCP).

Its purpose is to provide a simple conversational interface that allows people to create and query Humanitarian Records through Telegram.

The Telegram Bot is **not an HCP Node**.

Instead, it acts as an HCP Client that communicates with any compatible HCP Node through the protocol's public API.

---

## Position inside the HCN Ecosystem

```
Human Connection Network (HCN)
│
├── HCP Specification
│       Defines the protocol
│
├── HCP Reference Node
│       Reference implementation of an HCP Node
│
├── HCP Telegram Client   ← This repository
│
├── HCP Web Client
│
└── Other future HCP Clients
```

The protocol is independent from any specific application.

Different clients may exist while speaking the same humanitarian language.

---

## Purpose

The Telegram Client allows users to:

- Create Humanitarian Records
- Query existing records
- Receive updates from HCP Nodes
- Submit humanitarian observations
- Work with a simple conversational interface

The client itself does **not** store humanitarian data permanently.

Its responsibility is only to interact with HCP Nodes.

---

## Architecture

```
Telegram User
        │
        ▼
Telegram Bot
        │
        ▼
HCP Telegram Client
        │
 REST API
        │
        ▼
HCP Node
        │
        ▼
Humanitarian Records
        │
        ▼
Other HCP Nodes
```

---

## Repository Structure

```
app/
    Telegram application

docs/
    Client documentation

examples/
    Sample Humanitarian Records

tests/
    Automated tests
```

---

## Relationship with HCP

The Telegram Client implements the user experience.

The HCP Node implements the protocol.

This separation allows multiple independent applications to interact with the same humanitarian network without changing the protocol itself.

---

## Current Status

Current implementation includes:

- Telegram Bot
- Humanitarian Record creation
- Communication with an HCP Node
- Reference client implementation

Future versions may include:

- Record search
- Follow-up notifications
- Offline queue
- Multiple language support
- Voice-assisted registration
- Media attachments (when supported by future HCP extensions)

---

## Running

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure:

```text
TELEGRAM_BOT_TOKEN=...
HCP_API_BASE_URL=http://localhost:8000
```

Run:

```bash
python -m app.bot
```

---

## Related Repositories

| Repository | Description |
|------------|-------------|
| **hcp-specification** | Humanitarian Connection Protocol specification |
| **hcp-reference** | Reference HCP Node implementation |
| **hcp-node-web** | Reference Web Client |
| **humanconnectionnetwork.org** | Human Connection Network |
| **redconexionhumana.org** | First humanitarian implementation built on HCP |

---

## License

Apache License 2.0

---

## Human Connection Network

HCP is part of the Human Connection Network initiative.

Our mission is to enable humanitarian interoperability through open, decentralized and vendor-neutral protocols.

Learn more at the Human Connection Network project.
