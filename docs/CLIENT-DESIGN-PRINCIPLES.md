# CLIENT-DESIGN-PRINCIPLES

Version: 0.1 (Draft)

Status: Draft

Category: Client Specification

Project: Human Connection Network

Repository: hcp-client-telegram

License: Apache-2.0

Depends On:

- HCP-0000 Overview
- HCP Client Role
- BOT-FLOW
- CLIENT-ARCHITECTURE

---

# 1. Purpose

This document defines the design principles that should guide the behavior and user experience of every Humanitarian Connection Protocol (HCP) client.

These principles are technology-independent.

They apply equally to Telegram, WhatsApp, Web, SMS, mobile applications and future HCP clients.

The objective is to ensure that every HCP implementation provides a consistent, ethical and accessible humanitarian experience.

---

# 2. Human Before Technology

Every design decision should prioritize people over technology.

The client exists to assist individuals during stressful humanitarian situations.

Technology is only the tool.

Human dignity is the priority.

---

# 3. Guide, Don't Interrogate

The client should behave like a humanitarian assistant.

Never like a bureaucratic form.

Questions should be presented naturally.

Only one question should be asked at a time.

Users should always understand why information is being requested.

---

# 4. One Step at a Time

Each screen should request only one piece of information.

Avoid presenting multiple questions simultaneously.

Progressive conversations reduce stress, improve comprehension and increase data quality.

---

# 5. Buttons Before Free Text

Whenever possible, users should select predefined options.

Buttons reduce ambiguity.

Buttons improve accessibility.

Buttons increase consistency.

Buttons improve future data correlation.

Free text should only be requested when structured information is insufficient.

---

# 6. Ask Only What Is Useful

Every requested field should have a humanitarian purpose.

If information is not useful for creating or correlating Humanitarian Records, it should not be requested.

Collect less.

Understand more.

---

# 7. Approximate Information Is Valuable

Users should never feel obligated to provide perfect information.

Approximate observations are acceptable.

Examples:

- Estimated age
- Approximate location
- Unknown name

HCP is designed to correlate observations, not perfect identities.

---

# 8. Explain Before Requesting

Whenever users are asked to contribute information, the client should explain why the information is important.

People collaborate better when they understand the purpose of their contribution.

---

# 9. Human Language First

Users should never see protocol identifiers.

Examples

Instead of

event_type = missing

Display

🚨 Missing Person

Instead of

source = friend_acquaintance

Display

👤 Friend / Acquaintance

Protocol terminology belongs to software.

Human language belongs to users.

---

# 10. Review Before Publishing

Every report should be reviewed before submission.

Users must have the opportunity to:

- Review
- Edit
- Cancel

before publishing a Humanitarian Record.

---

# 11. Transparency Builds Trust

The client should clearly explain:

- what will happen after submission,
- why the information is collected,
- how it may be used.

Users should never feel that information disappears into an unknown system.

---

# 12. Encourage Honest Reporting

The client should gently encourage honest participation.

Example

Please submit only information you believe to be true or reasonably reliable.

An honest report may help connect important information for other people.

Trust is built through responsible participation.

---

# 13. HCP Does Not Identify People

The client should communicate one of the central principles of HCP.

HCP does not attempt to identify people.

HCP records humanitarian observations.

Different observations may describe the same person.

Future correlation may reveal useful relationships between independent observations.

---

# 14. Correlation Is Not Identification

Search results represent probabilities.

They are not confirmations.

The client should communicate this distinction clearly.

Correlation helps humanitarian work.

Human verification remains essential.

---

# 15. Accessibility By Default

Clients should remain usable by people with different abilities and educational backgrounds.

Recommendations

- Simple language
- Short sentences
- Large buttons
- High contrast
- Screen reader compatibility
- Icons supporting text
- Keyboard accessibility where applicable

Accessibility is a requirement.

Not an enhancement.

---

# 16. Offline-First Mindset

Future HCP clients should assume that connectivity may be limited.

Whenever possible:

- preserve user input,
- support delayed synchronization,
- minimize bandwidth,
- tolerate unstable connections.

Connectivity should improve the experience, not define it.

---

# 17. Reusable Humanitarian Observations

A Humanitarian Record should remain useful beyond the moment it was created.

It should become a reusable humanitarian observation that may later assist:

- Families
- Hospitals
- Emergency organizations
- Humanitarian initiatives
- HCP Nodes
- Future AI systems

The value of a record increases as new compatible observations are received.

---

# 18. Privacy Through Purpose

The client should avoid collecting unnecessary information.

Every requested field should have a clear humanitarian justification.

Collecting less information often increases trust while improving interoperability.

---

# 19. Every Contribution Matters

Users should leave the conversation feeling that their contribution has value.

Even incomplete observations may later become useful through correlation.

No honest contribution is insignificant.

---

# 20. Design For Humanity

The purpose of an HCP client is not simply to create records.

Its purpose is to help people communicate humanitarian observations in a way that allows future collaboration between individuals, organizations and technology.

The interface should always reflect empathy, clarity, responsibility and hope.

Technology changes.

Human needs remain.

---

# 21. Summary

Every HCP client should feel like a calm, trustworthy humanitarian assistant.

It should guide rather than interrogate.

Explain rather than confuse.

Encourage rather than pressure.

By following these principles, every implementation—regardless of platform or programming language—can provide a consistent humanitarian experience while preserving the integrity of the Humanitarian Connection Protocol.
