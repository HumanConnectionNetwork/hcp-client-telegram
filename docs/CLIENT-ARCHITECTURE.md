# CLIENT-ARCHITECTURE

Version: 0.1 (Draft)

Status: Draft

Category: Client Specification

Project: Human Connection Network

Repository: hcp-client-telegram

License: Apache-2.0

Depends On:

* HCP Client Role
* BOT-FLOW
* CREATE-RECORD-FLOW
* SEARCH-RECORD-FLOW
* ERROR-HANDLING
* LOCALIZATION

---

# 1. Purpose

This document defines the internal architecture of the HCP Telegram Client.

The objective is to provide a clean, modular and reusable architecture that separates user interaction from HCP protocol logic.

The Telegram Client should be viewed as one implementation of an HCP Client, not as the protocol itself.

---

# 2. Design Philosophy

The architecture follows a **Protocol First** approach.

The Humanitarian Connection Protocol (HCP) is the center of the application.

Telegram is only one communication channel.

This separation allows future HCP clients to reuse most of the same architecture with minimal changes.

---

# 3. Architectural Principles

The client should follow these principles.

## Separation of Responsibilities

Each component should have a single responsibility.

Conversation management, protocol communication, models and utilities should remain independent.

---

## Reusability

HCP-specific logic should be reusable across future clients.

Only the user interface should change.

---

## Simplicity

The architecture should remain understandable by contributors with different experience levels.

Avoid unnecessary abstraction.

---

## Testability

Every module should be independently testable.

Business logic should not depend directly on Telegram.

---

# 4. Repository Structure

```text
hcp-client-telegram/

│
├── app/
│
│   ├── bot.py
│   ├── config.py
│   ├── messages.py
│
│   ├── conversation/
│   │
│   │   ├── start.py
│   │   ├── create_record.py
│   │   ├── search_record.py
│   │   └── help.py
│
│   ├── hcp/
│   │
│   │   ├── client.py
│   │   ├── health.py
│   │   ├── records.py
│   │   └── search.py
│
│   ├── models/
│   │
│   │   ├── humanitarian_record.py
│   │   └── correlation_candidate.py
│
│   ├── utils/
│   │
│   │   ├── validation.py
│   │   └── formatting.py
│
│   └── locales/
│
│       ├── en.json
│       ├── es.json
│       ├── pt.json
│       └── ...
│
├── docs/
├── tests/
├── examples/
│
├── README.md
├── LICENSE
├── requirements.txt
└── .env.example
```

---

# 5. Component Responsibilities

## bot.py

Application entry point.

Responsibilities

* Initialize Telegram.
* Register conversation handlers.
* Load configuration.
* Start the client.

It should contain very little business logic.

---

## config.py

Centralizes application configuration.

Examples

Telegram Token

HCP Node URL

Timeout values

Logging configuration

Localization settings

Configuration should never be hardcoded.

---

## messages.py

Provides access to localized messages.

The rest of the application should request translated text through this module instead of directly reading language files.

---

# 6. Conversation Layer

The conversation layer is responsible for interacting with users.

Responsibilities

* Ask questions.
* Display buttons.
* Validate user responses.
* Guide conversations.
* Display search results.
* Display error messages.

This layer should not implement HCP protocol logic.

---

## start.py

Main menu.

---

## create_record.py

Guided creation of Humanitarian Records.

---

## search_record.py

Guided search for reported cases.

---

## help.py

General help and explanations.

---

# 7. HCP Layer

The HCP layer communicates with HCP Nodes.

Responsibilities

* Send requests.
* Receive responses.
* Parse protocol messages.
* Handle HTTP communication.

The HCP layer should remain independent from Telegram.

---

## client.py

Low-level communication with the HCP Node.

Responsibilities

GET

POST

Timeouts

Retries

Authentication (future)

---

## records.py

Operations related to Humanitarian Records.

Examples

Create Record

Retrieve Record

Future Update Record

---

## search.py

Search-related operations.

Examples

Search Reported Cases

Receive Correlation Candidates

Parse Correlation Probability

Future Explainable Correlation

---

## health.py

Checks HCP Node availability.

Example

GET /health

---

# 8. Models

Models represent HCP objects.

Models should closely follow the HCP Specification.

---

## humanitarian_record.py

Represents a Humanitarian Record.

Responsibilities

Validation

Serialization

JSON conversion

---

## correlation_candidate.py

Represents a possible match returned by the HCP Node.

Fields may include

Reference ID

Correlation Probability

Matching Factors (future)

Humanitarian Record summary

---

# 9. Utilities

Utilities provide reusable helper functions.

Examples

Validation

Formatting

Date handling

Input normalization

Utilities should never contain business rules.

---

# 10. Localization

Localization remains completely independent.

Language files should contain only user-facing text.

Business logic must never depend on language.

---

# 11. Data Flow

```text
User

↓

Telegram

↓

Conversation Layer

↓

HCP Layer

↓

HCP Node

↓

HCP Response

↓

Conversation Layer

↓

User
```

Every layer has a clearly defined responsibility.

---

# 12. Future Extensions

The architecture should allow new capabilities without major restructuring.

Examples

Pending Report Queue

Offline Synchronization

Authentication

Digital Signatures

Attachments (if adopted by future HCP versions)

Multiple HCP Nodes

Automatic Node Discovery

---

# 13. Future Clients

The architecture should serve as a reference for future HCP clients.

Examples

* hcp-client-whatsapp
* hcp-client-web
* hcp-client-sms
* hcp-client-ios
* hcp-client-android
* hcp-client-cli

Only the communication interface should change.

The HCP layer should remain largely identical.

---

# 14. Testing Strategy

Every architectural layer should have dedicated tests.

Conversation tests

HCP communication tests

Model validation tests

Localization tests

Utility tests

Testing should focus on behavior rather than implementation details.

---

# 15. Summary

The HCP Telegram Client follows a modular **Protocol First** architecture where Telegram is treated as the user interface and the Humanitarian Connection Protocol remains the core of the application.

By separating conversation management, protocol communication, data models, localization and reusable utilities, the client becomes easier to maintain, easier to test and ready to serve as the reference implementation for future HCP clients across different communication platforms.
