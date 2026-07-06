# ERROR-HANDLING

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

---

# 1. Purpose

This document defines how the HCP Telegram Client should respond when errors, interruptions or unexpected situations occur.

The objective is not only to report errors, but to help users continue their task with confidence.

The client should always remain calm, informative and supportive.

---

# 2. Design Principles

Every error message should follow these principles.

## Clear

Explain what happened using simple language.

Avoid technical terminology whenever possible.

---

## Helpful

Whenever an error occurs, the client should explain what the user can do next.

Never leave the user without guidance.

---

## Respectful

Never imply that the user caused the problem unless the input is clearly invalid.

---

## Calm

Humanitarian emergencies are stressful situations.

Messages should reduce uncertainty rather than increase it.

---

## Transparent

The client should honestly communicate what happened.

Do not hide failures.

Do not invent successful operations.

---

# 3. Error Categories

Errors can be grouped into several categories.

---

## User Input Errors

Examples

• Empty required field

• Invalid age

• Description too long

• Unsupported characters

The client should explain the problem and allow immediate correction.

Example

"The estimated age appears to be invalid.

Please enter a number or an approximate age."

---

## Communication Errors

Examples

• Internet unavailable

• Telegram connection interrupted

• Timeout

• DNS failure

Example

"We couldn't contact the HCP Node.

Please check your connection and try again."

---

## Server Errors

Examples

• Internal server error

• Service temporarily unavailable

• Maintenance

Example

"The HCP Node is temporarily unavailable.

Please try again in a few minutes."

---

## Unexpected Errors

Unexpected situations should never expose technical details.

Instead, display

"An unexpected problem occurred.

Please try again later."

Technical information should be written only to application logs.

---

# 4. Pending Report

One of the fundamental principles of the HCP Telegram Client is that information entered by the user should not be lost whenever possible.

If a report cannot be submitted because the HCP Node or the network is unavailable, the client should place it in a **Pending Report** state.

Example

---

⚠️ Your report could not be submitted at this moment.

The information has been safely preserved.

It will remain available until you decide to submit it again.

Status

Pending Report

---

Future implementations may automatically submit pending reports when connectivity becomes available.

---

# 5. Validation Errors

Validation should happen as early as possible.

Examples

Invalid age

↓

Explain the problem

↓

Ask again

The user should never be forced to restart the entire conversation because of a single incorrect answer.

---

# 6. Search Errors

If a search cannot be completed

The client should explain

"The search could not be completed at this moment.

Please try again later."

Do not display partial or unreliable search results.

---

# 7. No Results

"No results" is not an error.

The client should clearly distinguish between

• No matching reports found

and

• Search failed

Example

"No similar humanitarian reports were found.

New reports may become available over time."

---

# 8. Timeout Handling

If communication exceeds the configured timeout

The client should display

"The request is taking longer than expected.

Please wait a moment or try again."

Avoid duplicate submissions while waiting.

---

# 9. Duplicate Submission Prevention

If the user presses the confirmation button multiple times

The client should prevent duplicate requests.

Example

"Your report is already being submitted."

Only one request should be processed.

---

# 10. Interrupted Conversations

If the conversation is interrupted

Examples

• User closes Telegram

• User changes device

• Connection is lost

The client should allow the conversation to continue whenever technically possible.

Future versions may restore unfinished conversations automatically.

---

# 11. Logging

Internal logs should contain technical information useful for developers.

Examples

Request ID

Timestamp

Error Type

HTTP Status

Exception

Node Response

Logs must never expose sensitive humanitarian information unnecessarily.

---

# 12. Privacy

Error messages should never reveal confidential information.

Examples

Avoid

"Database connection failed."

Prefer

"The service is temporarily unavailable."

---

# 13. Accessibility

Error messages should remain accessible.

Recommendations

• Short sentences.

• Clear language.

• Icons with descriptive text.

• Avoid excessive punctuation.

• Avoid all-uppercase text.

---

# 14. Future Compatibility

Future HCP clients should implement the same error-handling philosophy.

Examples

Telegram

WhatsApp

SMS

Mobile Applications

Web Clients

Offline-first Clients

Only the interface should change.

The user experience should remain consistent.

---

# 15. Summary

The HCP Telegram Client should treat every error as an opportunity to help the user continue.

Whenever possible, information should be preserved, conversations should remain recoverable and users should always understand what happened and what they can do next.

The client should communicate failures honestly, protect user information and never create unnecessary anxiety during humanitarian emergencies.
