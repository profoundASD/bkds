Experimental Concept

# The Special Education Corpus

A proposal for a **Consortium of Content**. By unifying high-fidelity data sources under a single safe adapter strategy, this project can offer lifelong learners a stable alternative to the open web—bridging the gap between school-based intervention and adult autonomy.

**Proof of Concept Notice:** This document outlines a hypothetical architecture and potential data partners. No official affiliation, licensing agreement, or partnership exists with the organizations listed below. These entities are referenced solely as archetypes for the quality and structure of data required to support this user base.

## 1\. The Vision

The proposed Special Education Corpus is envisioned not merely as a database, but as a **structured consortium of high-fidelity content** —donated by museums, libraries, and educational publishers—specifically architected to bridge the gap between school-based intervention and adult autonomy.

This approach creates a "safe harbor" for lifelong learning. Complex topics—from aerospace history to marine biology—are rendered accessible without the cognitive friction or safety risks of the open web, allowing users to pursue intense interests with dignity and independence long after they have aged out of traditional support services.

## 2\. AI as "Systemizing Engine"

In this architecture, Artificial Intelligence is strictly constrained. It is not used to "invent" facts or write open-ended essays. Instead, it functions as a **Systemizing Engine**.

The Transformation Process

  - **Ingest:** The system accepts raw assets from trusted partners (e.g., a museum collection API).
  - **Sort:** AI organizes the content based on the user's need for order (e.g., "Chronological," "By Color," "By Size").
  - **Format:** Raw text is simplified into "Easy Read" captions; videos are checked for transcripts.
  - **Output:** The result is a predictable **Deck** (Slideshow or Flashcard set), not a chaotic feed.

## 3\. Hypothetical Source Catalog

To function effectively, the Corpus requires data sources that offer **Stable IDs** (so a link today is a link tomorrow) and **Verified Metadata** (so the project knows exactly what is shown). The following are the target archetypes for integration:

### Core Aggregators

Wikipedia / MediaWiki Reference

The backbone of factual knowledge. Its structured API allows for the extraction of specific sections (summaries, infoboxes) without the visual noise of the full site.

**Application:** Building "Fact Decks" and simple stories about historical events or machinery.

NASA Open APIs Science

High-quality, daily-updated imagery of space and earth science. Provides a reliable stream of "safe novelty" for users interested in science and systems.

**Application:** "Picture of the Day" routines; Solar System comparison decks.

### Cultural & Sensory

Museum Collections Heritage

(e.g., Smithsonian Open Access). Digital archives of artifacts with rich metadata. Allows for object rotation, zooming, and classification without travel friction.

**Application:** Classification games (sorting insects, coins, or planes); Virtual tours.

Audio Archives Sensory

(e.g., Xeno-canto, FreeSound). Curated libraries of natural and mechanical sounds. Critical for users who engage primarily through audio or need sensory regulation.

**Application:** Soundboards (Bird calls, Train whistles); Calm listening environments.

## 4\. Dual-Use Potential: School & Home

While designed for the home "service cliff," this architecture offers significant value to the Special Education classroom. It functions as a **Continuity Layer**.

At Home (Leisure)

### Autonomous Engagement

The user engages with an interest-based deck (e.g., "Trains of the 1800s") as a distinct leisure activity. It is safe, predictable, and requires no parental hovering.

At School (Therapy)

### Therapeutic Anchor

A Speech-Language Pathologist activates the _same deck_. Because the content is systemized, they can use it to drive specific language goals ("Which train is _older_?"), anchoring the lesson in what the student already loves.

## 5\. Product Backlog & Source Catalog

The complete technical scope for the Corpus 0.1.0 MVP, including all targeted data integrations and safety logic.

6 Epics

26 User Stories

24 Data Sources

Source Priority Mix

MVP: 2 Core: 7 Later: 15

### Hypothetical Source Catalog

Candidate sources identified for ingestion, subject to licensing and feasibility checks.

ID | Source Name | Category | Priority | Integration Mode
---|---|---|---|---
SRC-WIKIPEDIA | Wikipedia | Core Aggregators |  MVP_CANDIDATE |  provider adapter api
SRC-WIKIMEDIA | Wikimedia Commons | Core Aggregators |  MVP_CANDIDATE |  provider adapter api
SRC-FLICKR | Flickr | Core Aggregators |  CORE |  provider adapter api
SRC-GOOGLE-IMAGE | Google Image | Core Aggregators |  LATER_DISCOVERY |  feasibility only
SRC-BING-IMAGE | Bing Image | Core Aggregators |  LATER_DISCOVERY |  feasibility only
SRC-DONATED-TEXTBOOKS | Textbooks | Core Aggregators |  CORE |  donated corpus pipeline
SRC-GOOGLE-MAPS | Google Maps | Core Aggregators |  LATER_DISCOVERY |  sanitized launchpad intents
SRC-GOOGLE-EARTH | Google Earth | Core Aggregators |  LATER_DISCOVERY |  sanitized launchpad intents
SRC-YOUTUBE | YouTube | Core Aggregators |  CORE |  provider adapter api or sanitized dom
SRC-VIMEO | Vimeo | Core Aggregators |  LATER |  provider adapter api
SRC-MUSEUMS | Museums | Core Aggregators |  LATER_DISCOVERY |  donated corpus pipeline or partner adapter
SRC-FREESOUND | FreeSound.org | Audio & Sensory Environments |  LATER |  provider adapter api
SRC-INTERNET-ARCHIVE |  Internet Archive / LibriVox  | Audio & Sensory Environments |  LATER |  provider adapter api
SRC-XENOCANTO | Xeno-canto | Audio & Sensory Environments |  LATER |  provider adapter api
SRC-INATURALIST | iNaturalist | Nature, Science & Classification |  LATER |  provider adapter api
SRC-NASA | NASA (APIs) | Nature, Science & Classification |  CORE |  provider adapter api
SRC-FLIGHTS |  OpenSky Network / FlightAware  | Nature, Science & Classification |  LATER_DISCOVERY |  feasibility only
SRC-OPENSYMBOLS | OpenSymbols | Visual Symbols & Communication (AAC) |  CORE |  provider adapter api
SRC-NOUNPROJECT | The Noun Project | Visual Symbols & Communication (AAC) |  LATER_DISCOVERY |  feasibility only
SRC-SMITHSONIAN |  Smithsonian Open Access  | Cultural Heritage & 3D Objects |  LATER |  provider adapter api
SRC-EUROPEANA-DPLA | Europeana / DPLA | Cultural Heritage & 3D Objects |  LATER |  provider adapter api
SRC-OPENWEATHER | OpenWeatherMap | Real-Time 'Safe' World Data |  LATER |  provider adapter api
SRC-OSM | OpenStreetMap | Real-Time 'Safe' World Data |  CORE |  provider adapter data
SRC-GUTENBERG | Project Gutenberg | Curated Text & Literacy |  CORE |  provider adapter api or mirror

### Epics & User Stories

E19

### Corpus Strategy, Taxonomy, and Provider Profiles

Define a reusable corpus catalog and provider profiles that map sources to educational use-cases, safety gates, and persona-driven presentation constraints.

US-19.1 MVP

Canonical corpus source catalog schema

**As a** system, **I want** a canonical schema for describing each corpus source (API, donation, DOM-sanitized), **so that** providers can be onboarded consistently with clear safety and licensing expectations.

  - Schema supports: source_id, category, access_method, integration_mode, educational_applications, risk_defaults, licensing_requirements, cache_policy, attribution_fields, and known limitations.
  - Schema supports marking a source as: MVP_CANDIDATE, CORE, LATER, or DISCOVERY_ONLY.
  - Schema is versioned and included in compile artifacts.

US-19.2 MVP

Provider profile template tied to safety gates

**As a** system, **I want** a provider profile template used by adapters and gates, **so that** filters, allowlists, and rights rules are enforced uniformly.

  - Provider profile includes: SafeSearch/filters (when available), blocked terms/themes mapping, risk tier default, required metadata fields, and licensing allowlist requirements.
  - Provider profile explicitly defines whether caching is allowed and under what license constraints.
  - Profile changes are logged and require a new compile/build to take effect on device.

US-19.3 Core

Educational application mapping for sources and packs

**As a** content_designer, **I want** a mapping between sources and educational applications (systemizing, story building, AAC reinforcement, etc.), **so that** the compiler can pick building blocks that match a learner's persona and learning goals.

  - Each source can declare one or more educational applications and recommended layout templates.
  - Compiler can generate a rationale field in build output explaining why a source was selected for a learner profile.

US-19.4 MVP

Feasibility + terms-of-use checklist for discovery-only sources

**As a** product_owner, **I want** a standard feasibility checklist for sources with unclear caching/licensing constraints, **so that** the project avoids accidental non-compliance and avoids implying guaranteed access.

  - Checklist includes: auth model, quotas, allowed caching, required attribution, content restrictions, and API stability.
  - Discovery-only sources cannot be promoted to CORE without an explicit recorded decision.

E20

###  Adapter Library: Common Contract for API, Data, and Donation Sources

Implement a uniform adapter contract so compile-time recipes can be executed safely without runtime web browsing, across heterogeneous sources.

US-20.1 MVP

Provider adapter contract v1 (search, item_get, media_get)

**As a** system, **I want** a standard adapter contract for providers, **so that** retrieval recipes remain structured and runtime never invents new URLs or queries.

  - Contract supports: search(query, filters), item_get(id), media_get(id), plus optional transcript_get/captions_get for video/audio.
  - All adapter calls return a normalized content item object with stable IDs, required metadata, and attribution fields.
  - Adapters enforce provider profile constraints (SafeSearch/filters, allowlists, license rules) before returning candidates.

US-20.2 MVP

Normalized content item schema for corpus ingestion

**As a** system, **I want** a normalized content item schema across sources, **so that** packs, layouts, and safety gates work across text, image, audio, and video.

  - Schema supports: item_id, provider_id, canonical_url, title, description, media_assets, license, attribution, safety_signals, and educational_tags.
  - Schema supports an optional 'source_fingerprint' used for dedupe and retroactive purge.

US-20.3 Core

Adapter test harness and golden fixtures

**As a** system, **I want** a test harness with golden fixtures for each adapter, **so that** provider changes are detected before they disrupt the user experience.

  - Each adapter ships with golden inputs and expected normalized outputs.
  - Build fails if required metadata fields are missing or if filtering rules are not enforced.

US-20.4 Core

API key and quota management for adapters

**As a** caregiver_admin, **I want** safe configuration for API credentials and quotas, **so that** providers can be used without destabilizing builds or leaking secrets.

  - Credentials are stored securely and never emitted in build artifacts.
  - Quota budgets can be configured per provider and per build cycle.
  - When quotas are exceeded, the system degrades to deterministic fallbacks (no retries at runtime).

E21

### Core Aggregator Integrations (Most Coveted Sources)

Deliver a small set of high-leverage sources that can generate broad, interest-driven decks while remaining governable and attributable.

US-21.1 MVP

Wikipedia (MediaWiki) adapter + pack templates

**As a** system, **I want** a Wikipedia adapter that produces structured, leveled cards, **so that** encyclopedic content can become stable decks without runtime browsing.

  - Adapter can fetch page summaries/sections and citations/refs when available.
  - Compiler can generate at least two pack types from Wikipedia: (1) reference deck (facts), (2) simple story (anchored summary).
  - All items include attribution and source links suitable for a read-only info panel.

SRC-WIKIPEDIA

US-21.2 MVP

Wikimedia Commons adapter (images + licensing)

**As a** system, **I want** a Wikimedia adapter that returns images with strong licensing metadata, **so that** media galleries can be built with reliable attribution and cache rules.

  - Adapter returns image renditions plus license + attribution fields required for Gate E compliance.
  - Candidate screening rejects items missing license metadata or required attribution fields.
  - Compiler can build a 'media_gallery' pack that includes only license-allowed cached assets.

SRC-WIKIMEDIA

US-21.3 MVP

Reusable 'Geography starter packs' using OpenStreetMap data

**As a** system, **I want** prebuilt geography reference packs (state/county/city), **so that** common interest scaffolds can be inherited without generating from scratch.

  - Packs are built from normalized OSM data with stable IDs and predictable sorting/grouping.
  - Packs support systemizing layouts (by state, by county) and are compatible with persona-driven verbosity controls.
  - Pack build produces a deterministic list output (no randomness) given the same inputs.

SRC-OSM

US-21.4 Core

NASA adapter for high-quality visual decks (APOD baseline)

**As a** system, **I want** a NASA adapter that yields stable daily/weekly visual items, **so that** the library can include high-quality, safe science content with predictable metadata.

  - Adapter provides image + short description + date metadata and attribution requirements.
  - Compiler can produce a slideshow pack with a fixed window (e.g., last N items) using stamina slicing.

SRC-NASA

US-21.5 Core

YouTube adapter feasibility: transcript-first candidate screening

**As a** product_owner, **I want** a feasibility plan for YouTube integration that centers transcript/captions screening, **so that** video can be governed without exposing algorithmic feeds.

  - Document adapter capabilities needed: channel/playlist ingestion, transcript/captions retrieval, allowlisted deep links.
  - Define minimum viable safety: restrict to allowlisted channels/playlists; no search in MVP unless fully governed; hide 'Up Next' surface.
  - Mark integration as CORE (post-MVP) unless requirements are fully satisfied.

SRC-YOUTUBE

US-21.6 Later

Image search aggregators feasibility (Google/Bing)

**As a** product_owner, **I want** a feasibility plan for general image search APIs, **so that** the product does not imply broad image access without enforceable licensing and safety metadata.

  - Define what metadata is required for caching/display (license, attribution, safe preview rules).
  - If required metadata is not available, constrain to 'non-cached preview only' or keep as discovery-only.

SRC-GOOGLE-IMAGE SRC-BING-IMAGE

E22

###  Donated and Licensed Corpus Onboarding (Hypothetical Partner Track)

Enable a donated/partner corpus path (textbooks, museum packs, curriculum modules) that can be compiled offline with explicit rights and traceability.

US-22.1 Core

Donated corpus ingestion pipeline (ingest → normalize → pack)

**As a** system, **I want** an ingestion pipeline for donated materials, **so that** partners can contribute content that becomes deterministic packs.

  - Pipeline supports: file intake, metadata capture, normalization into content item schema, and pack generation.
  - Each donated asset has a license record, attribution fields, and an explicit caching rule.
  - No donated content can be published to device until Gate E requirements are satisfied.

SRC-DONATED-TEXTBOOKS SRC-MUSEUMS

US-22.2 Core

Rights package and takedown workflow for donated content

**As a** caregiver_admin, **I want** a rights packet model and takedown mechanism, **so that** donated materials remain compliant and reversible.

  - Rights packet includes: permitted uses, caching rules, attribution requirements, and expiration/review date.
  - Takedown can remove content from future builds and trigger purge from cached packs.

US-22.3 Later

Curriculum pack format: routines, vocabulary sets, step supports

**As a** special_educator_or_slp, **I want** a pack format for classroom-style modules, **so that** schools can contribute modules that work in predictable layouts.

  - Pack supports: routine steps, target vocabulary, prompt hierarchy, and generalization examples.
  - Pack supports persona-driven verbosity/pacing controls (e.g., simple sentences vs expanded).

US-22.4 Later

License-preserving accessibility transforms for donated text

**As a** system, **I want** controlled transforms (simplification, chunking) that preserve attribution and boundaries, **so that** materials can be adapted without losing provenance.

  - Transforms store: original excerpt pointers, transform method metadata, and reviewer status.
  - System can display a minimal provenance view: source title, license, and attribution.

E23

###  Specialized Corpus Modules (Audio, Nature, AAC, Heritage, Literacy)

Demonstrate extensibility: multiple vertical sources can be integrated through the same adapter + pack system, producing stable, persona-tuned decks.

US-23.1 Core

AAC symbol overlay pipeline (OpenSymbols baseline)

**As a** slp, **I want** AAC symbols displayed alongside photos and words, **so that** learners can build comprehension and functional communication.

  - System can map common nouns/verbs in a deck to symbol IDs when available.
  - Caregiver can toggle symbol layer on/off per learner profile.
  - Symbol sources follow the same licensing and attribution rules as other media.

SRC-OPENSYMBOLS

US-23.2 Core

Public domain reading packs (Gutenberg baseline)

**As a** caregiver, **I want** public-domain texts converted into predictable reading sessions, **so that** literacy and story engagement can be practiced in a controlled UI.

  - Texts are chunked into stamina-sized segments with stable progress markers in the ledger.
  - Reading level transforms are optional and preserve provenance pointers.
  - No external links are shown to the learner during reading mode.

SRC-GUTENBERG

US-23.3 Later

Cultural heritage decks (Smithsonian/Europeana/DPLA) - adapter blueprint

**As a** product_owner, **I want** an adapter blueprint for cultural heritage aggregators, **so that** future integrations can be implemented without changing core architecture.

  - Blueprint defines required metadata (attribution, rights, stable IDs) and recommended pack templates (timeline, object gallery).
  - Integration remains LATER until rights and caching policies are confirmed for each provider.

SRC-SMITHSONIAN SRC-EUROPEANA-DPLA

US-23.4 Later

Audio sensory packs - adapter blueprint (FreeSound/Archive/Xeno-canto)

**As a** product_owner, **I want** a plan for audio packs with strong sensory controls, **so that** sound exploration is safe and predictable.

  - Define sensory constraints: max volume, no sudden peaks (when metadata allows), duration caps, and caregiver allowlists.
  - Define pack types: soundboard, matching game, and story accompaniment.
  - Integration remains LATER pending feasibility of safety metadata.

SRC-FREESOUND SRC-INTERNET-ARCHIVE SRC-XENOCANTO

E24

###  Corpus Operations: Health Checks, Version Trails, and Controlled Updates

Keep the corpus trustworthy over time: detect breakage, record diffs, and prevent destabilizing changes from reaching the learner mid-session.

US-24.1 Core

Automated corpus health checks (link rot + metadata completeness)

**As a** system, **I want** scheduled health checks across cached packs and provider references, **so that** broken items are detected during maintenance rather than during learner use.

  - Health checks flag: broken URLs, missing attribution/license fields, and invalid media renditions.
  - Failures produce a reason code and are queued for rebuild or quarantine.

US-24.2 Core

Corpus diff report per build (what changed and why)

**As a** caregiver_admin, **I want** a diff report for corpus changes between builds, **so that** updates are reviewable and predictable.

  - Diff includes: added/removed items, changed metadata, and policy/profile version changes.
  - Diff identifies whether a change was provider-driven, policy-driven, or curator-driven.

US-24.3 Core

Quarantine workflow for unstable providers or packs

**As a** caregiver_admin, **I want** to quarantine a provider or pack when behavior changes, **so that** unstable external surfaces do not reach the learner.

  - Quarantine prevents publishing new packs from that provider while keeping existing pinned/approved content per policy.
  - Quarantine emits an audit entry and a rebuild recommendation.

US-24.4 MVP

Deterministic fallback content for missing/removed sources

**As a** system, **I want** fallback packs for common categories when sources are unavailable, **so that** the user experience remains functional even under provider failure.

  - Fallback packs are local and deterministic (no network).
  - Fallback packs respect learner sensory constraints and layout limits.
