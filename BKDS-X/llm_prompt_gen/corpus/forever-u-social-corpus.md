On this page

RFC / Experimental Concept

# The Social Corpus

A proposal for a **governed communication layer**. It enables profoundly autistic users to receive messages and photos from a trusted network without exposure to the complexity and risk surface of standard applications.

!

**PROOF OF CONCEPT NOTICE** This document describes a hypothetical architecture. No affiliation exists with any telecom carrier. This is a safety-first design proposal for controlled ingestion, not a clinical tool.

## 01 The Purpose

The Social Corpus acts as **middleware** , not a social network. It receives communications from allowlisted sources and presents them through a stable, predictable interface compatible with the user's content library.

The Paradigm Shift

  - **From:** An open inbox with evolving UI patterns and varying risk.
  - **To:** A governed inbox using stable templates (Postcard, Album).
  - **From:** "Figure out how this app works."
  - **To:** "Browse messages like a deck."

## 02 Inputs & Adapters

The system ingests items from specific channels, normalizes them into internal assets, and stores them in a versioned "Social Library."

SMS / MMS Ingest

Receives media from allowlisted numbers only. Normalizes photos into "postcards" and text into stable cards. Strips thread complexity.

APPLICATION "Photos from Dad," daily highlights.

Email (Allowlisted) Ingest

Accepts messages from approved domains. Strips HTML/Tracking pixels. Quarantines attachments. Presents as a clean "Message Card."

APPLICATION Family newsletters, simple updates.

Calendar (Read-Only) Context

Reads scheduled events to generate "What's Next" cards. Does not allow editing. Used for routine structure and anxiety reduction.

APPLICATION Transition warnings, quiet-hour enforcement.

Media Retrieval Library

Stores durable references to approved media, allowing the user to revisit specific messages or photos without scrolling back through a chat history.

APPLICATION "My Favorites" deck.

## 03 Safety & Governance

Safety is implemented as gates and defaults. The runtime experience favors stability over feature-parity with mainstream apps.

Screening Pipeline

  - **Ingest:** Retrieve from permitted channels.
  - **Verify:** Check allowlists and trust tiers.
  - **Screen:** Scan for harm categories; strip links.
  - **Systemize:** Convert to "Postcard" or "Calendar Card."

###  Hard Rules (Invariants)

These categories are blocked regardless of strictness settings.

Block / Quarantine

  - **Exploitation:** Any explicit content or content involving minors.
  - **Predation:** Grooming signals, coercion, doxxing.
  - **Dangerous Instructions:** Phishing, self-harm instructions.

## 04 Caregiver Controls

Controls are explicit policies, not granular settings. The objective is to reduce caregiver burden.

Mode Selector Global

Primary control: **Strict** , **Standard** , or **Relaxed**. Adjusts pacing and review triggers, but never overrides hard blocking rules.

Trust Tiers Per-Sender

Senders can be **Trusted** (Auto-deliver), **Review Required** , or **Limited** (Photos only, no text).

Pacing & Quiet Hours Regulation

Rate limits prevent flooding. Bursts of messages are bundled into a single "New Items" card to prevent cognitive overload.

Link Policy Quarantine

Attachments quarantined by default. Links blocked or routed to caregiver review. Nothing auto-opens.

## 05 Emergency Bypass

Operational Stance

  - **Default:** The world cannot reach the user directly.
  - **Emergency Lane:** A specific list of Guardians can bypass screening.
  - **Escalation:** Repeated urgent messages trigger a simplified "Urgent Card."
  - **Audit:** All bypass events are logged for review.

## 06 Failure Behavior

In edge cases (spoofing, connector failure), the system defaults to conservative behavior: quarantine and simplify.

Failure Modes

  - **Compromised Sender:** Route to review based on anomaly signals (language, link frequency).
  - **Connector Down:** Show "Temporarily Unavailable" card; do not show error codes.
  - **Thread Confusion:** If group context is unclear, disable the thread entirely.
