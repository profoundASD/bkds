MVP Product Summary

# Forever University Content Platform

An **Augmentative and Assistive Operating System (AAOS)** for adolescents and adults with profound autism. Forever University replaces the chaos of the open web with a "Compile, Then Play" model—delivering safe, interest-driven exploration on an appliance-like device.

The Problem

Mainstream devices assume literacy and tolerance for distraction. For caregivers, "web supervision" becomes a second job, often leading to defensive withdrawal.

The Solution

**Structured Middleware.** Forever University does not browse the live web. It uses an offline pipeline (Ingest → Augment → Systemize) to build a versioned Content Library that is deterministic and stable.

Epic / Story Breakdown

  - Intake & Profiles (9)
  - Content Graph (12)
  - Runtime Safety (8)
  - Care Plan (6)

## 1\. Executive Summary

The Forever University Content Platform is designed for users with profound autism and complex communication needs, and the support teams who assist them. The goal is to make interest-driven learning feasible without requiring caregivers to become full-time device administrators.

**The MVP Approach:** Forever University is structured middleware. It uses a strict offline-to-runtime pipeline to build a versioned _Content Library_. The runtime experience is deterministic: predictable navigation, safe exits, and stable presentation designed to support autonomy without expanding risk.

## 2\. Practical Context: The "Alex" Scenario

Alex is 32 and lives at home. He has profound autism and intense, specific interests—often fixating on photography books or specific DVDs for weeks at a time. While verbal, his complex communication needs and attention deficits make the open web inaccessible; search bars feel paralyzing, and unexpected ads trigger severe anxiety, leading to **defensive withdrawal** where he refuses to use the device again.

His caregivers (parents) want him to continue learning and expanding his vocabulary, but they are exhausted. Curating safe content is a full-time job, and existing apps are often too childish. Without active guidance, Alex falls into **perseverative loops** —watching the same 10-second clip for hours—rather than exploring new topics.

#### Deep Dive Topics

Explore the clinical background on perseverative loops or try a live interactive demo of the "Flashcard Deck" engine.

 Perseveration in Profound Autism

#### Deep Dive Topics

Explore common complex communication needs in Profound Autism

 Complex Communication in Profound Autism

Step 1: The Setup

### Easy Intake

His parents use the natural language intake: _"Alex loves high-speed trains and severe weather. He gets stuck on loops easily. He needs simple text."_

Step 2: The Library

### Offline Compilation

Forever University compiles a "Trains" deck and a "Weather" deck. It specifically inserts a "Forever University" topic connecting _Steam Engines_ to _Industrial History_ to gently guide him out of a loop.

Step 3: The Experience

### Guided Autonomy

Alex explores autonomously. The interface is stable. When he fixates on one video, the **Perseveration Helper** offers a non-coercive choice: _"See specific Engine parts?"_ or _"Take a Break?"_

Step 4: The Outcome

### Respite & Growth

Alex engages for 45 minutes independently. He reads new words. His parents get a respite, knowing the environment is strictly governed and safe.

#### Deep Dive Topics

Chronicles in complex communication

 The Jason Tapes

## See It in Action

The Forever University interface is designed to reduce visual noise while keeping high-fidelity content front and center. Below is a demonstration of the **"Safe Player"** and **"Deck System"** in use.

### Interface Previews

#### Deep Dive Topics

Explore the clinical background on perseverative loops or try a live interactive demo of the "Flashcard Deck" engine.

 About Perseveration   Try Live Decks



## 3\. MVP Non-Negotiables

These are architectural constraints that define the MVP safety boundary. They are hard rules, not features.

Architecture

### Provider-Adapter Model

Runtime executes stored retrieval recipes via adapters (e.g., Wikipedia). It **never** invents new queries, browses arbitrarily, or executes raw web searches.

Safety

### Layered Gates (A–E)

Safety is enforced via multiple gates: compile-time sanitation, risk tiering, runtime screening, and caregiver approvals. Rights/attribution is a hard gate.

Design

### 5 Constrained Layouts

All content renders into one of five predetermined layouts (e.g., Slideshow, Flashcards). No free-form HTML generation.

Reliability

### Predictable Failure

Missing content shows a clean fallback screen with safe exits (Back/Favorites). The system never surfaces raw provider errors or OS dialogs.

Continuity

### Versioned Content Library + Persistent Ledger

An immutable, versioned Content Library ships as a content library file. A separate ledger preserves favorites, continue, and recents across updates.

## 4\. Core MVP Capabilities

### Pillar A — Intelligent Intake & Profiling

Bridge replaces manual configuration with caregiver-led onboarding.

  - **Natural Language Profiling:** Caregivers describe interests and sensitivities in plain language. The AI parses this input into structured configuration (e.g., "Loves vacuum cleaners, avoids loud noises").
  - **Trusted Voice Persona:** Caregivers can define phrasing and pacing so system prompts match the specific language the learner already understands and trusts.
  - **Deferrable Onboarding Wizards:** Optional, step-by-step setup flows capture novelty tolerance, transition difficulty, and perseveration risks without forcing completion in one sitting.
  - **Curated Starter Packs:** Pre-vetted "starter universes" reduce the need to invent the library from scratch.

### Pillar B — Data Pipeline: Ingest & Augment

The platform builds the library from trusted sources, using AI strictly for accessibility.

  - **Ingest:** Content is pulled from approved providers and special-ed corpora (e.g., donated datasets, Wikipedia).
  - **Augment:** AI acts as a translator, not an inventor. It reformats verified content into structured fields (reading level, summaries) that are schema-validated.
  - **Education Modules:** Plug-in activity structures (e.g., sequencing, categorization) are applied to interest content to support skill development.

### Pillar C — User Experience: Systemize & Display

The runtime experience is designed for the "systemizing" mind, aligning with neurodivergent traits such as hyper-fixation and the satisfaction of completing sets.

Organization

### Decks over Feeds

Content is organized into structured sets (e.g., "Air Force Bases by State"), supporting set completion rather than infinite algorithmic feeds.

Support

### Perseveration Helper

Configurable support ranging from minimal prompting to gentle bridges. This manages repetitive loops without coercion, offering safe exits and related topics.

Navigation

### Stable Choice Menu

Repeatable options always appear: “More of This,” “Related,” “Something New,” “Take a Break,” and “Favorites,” ensuring a predictable path forward.

Stability

### Stamina Slicing

Large topics are sliced into manageable sessions (e.g., 10 items) to prevent exhaustion while preserving the sense of progress.

Resilience

### Graceful Fallback Screen

When provider content is missing, a calm fallback screen explains unavailability and offers next steps, avoiding blank states or broken flows.

### Pillar D — Smart Launchpad

Controlled access to high-value external tools (Google Earth, etc.).

  - **Pre-vetted Intents:** Launch actions are defined by canonical data (e.g., coordinates), reducing exposure to UI flows.
  - **Conditional Visibility:** Launch buttons are hidden if data is missing; user never taps a broken control.

### Pillar E — Routine Support (ADL)

Supporting autonomy in routine tasks without becoming an enforcement system.

  - **Care Plan File:** Caregiver-authored routines compiled into deterministic prompt cards.
  - **Dismissible Prompts:** Done / Later / Help / Skip. Prompts never block access to the library.
  - **Routine Support Configuration:** Quiet hours and frequency caps let caregivers tune when and how often routine prompts appear.

## 5\. Backlog Highlights

A curated snapshot of MVP stories anchoring safety and deterministic delivery.

US-1.1 • PROFILE

**Learner Profile:** Content matches comprehension/modality needs.

US-1.2 • SAFETY

**Constraint Definition:** Unsafe/dysregulating content prevented globally.

US-2.4 • COMPILER

**Versioned Library:** Generate immutable content snapshot (World File).

US-3.5 • REVIEW

**Risk Tiering:** Bulk review logic to focus human eyes on "Amber" content only.

US-4.1 • RETRIEVAL

**Blueprint Execution:** Runtime executes recipes; never invents queries.

US-4.3 • FALLBACK

**Safe Failure:** Missing assets trigger "Safe Exit" UI, not OS errors.

US-6.4 • LOGIC

**Perseveration Helper:** Non-coercive intervention policy (Levels 0-5).

US-17.1 • ROUTINE

**Care Plan File:** Compile ADL prompts into deterministic cards.

## 6\. Responsible AI Posture

What AI Does

  - Translates caregiver natural language into structured profile settings.
  - Produces structured fields (summaries, captions) anchored to approved sources.
  - Supports workflows (assembling decks, formatting content) within the governed compile process.

What AI Does Not Do

  - No open-web browsing or unsupervised retrieval at runtime.
  - No clinical diagnosis or treatment guidance.
  - No speculative output presented as fact. Uncertainty defaults to "not available."

## 7\. MVP Scope & Constraints

To avoid implicit promises, the MVP draw-line is described plainly.

Included in MVP | Deferred (Core/Post-MVP)
---|---
Learner profile + Safety constraints | Broader provider adapters (Flickr/YouTube)
Versioned Content Universe Build + Structured Retrieval  | Full Diff Review UI + One-click Rollback
Constrained Layouts (max 5) | Predictive "Horizon" Prefetch
Care Plan Prompts (Non-coercive) | Automated "Golden Set" Regression Testing
Reason Codes for Screening | Expanded Lifecycle Automation

_Bridge is a proposal for making safe, interest-driven digital exploration practical. The MVP is intentionally conservative: prioritizing stability and caregiver usability over breadth of integrations._
