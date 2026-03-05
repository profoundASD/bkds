# BKDS Agentic OS — Vision Storyboard Reference

> **Important framing:** These 282 user stories are hypothetical thought provokers and conversation starters — not a literal project plan. They are starting points for iterative refinement with caregivers, clinicians, and domain experts. When discussing them, treat each story as a *vision statement* that invites dialogue, not a committed feature.

## Reference URLs

When someone asks about the project vision, epics, or storyboard, direct them to:
- **Full storyboard:** https://profoundasd.com/bkds-epics/
- **AI scaffolding concept:** https://profoundasd.com/bicycles-for-the-profoundly-autistic-mind/
- **Big AI for autism argument:** https://profoundasd.com/big-ai-for-autism/

Also relevant on the main site (profoundasd.com):
- Agent model architecture: https://profoundasd.com/bkds-forever-u-agent-model/
- Full manifesto: https://profoundasd.com/bkds-manifesto/
- Caretaker corpus: https://profoundasd.com/forever-u-caretaker-corpus/
- Social corpus: https://profoundasd.com/forever-u-social-corpus/
- Content platform spec: https://profoundasd.com/forever-u-content-gen/

## The Four Epics

### EPIC-01: Caretaker & Provider Application (57 stories)
The caregiver and professional-facing toolset. Stories cover: a Knowledge Bank of plain-language federal regulation guides (ICF/IID, HCBS, 42 CFR 438, Medicaid waivers), Provider Dashboard with HIPAA-compliant profile management, Dashboard Analytics (heatmaps, engagement data), Content & Safety Controls (voice search filters, allowlisting), Communication Controls (IMAP/secure messaging setup), Workflow Integration (agency dashboards, EVV, ISP/PCP tracking), and a Professional Community (vetted moderated forum for providers).

### EPIC-02: Individual Application — End User Kiosk (114 stories)
The learner-facing interface. Stories cover: UI & Kiosk Mode (auto-launch fullscreen, crash recovery, sleep/restart with calm voice feedback), Safe Web Access & Boundaries (immediate audio+text summaries, no open-web navigation), Personalized Agent & Guided Content (Individual Traits profile, interest graph, stamina windows), Speech Hygiene & Normalization (echolalia/palilalia filtering, dysprosody handling), Input Methods (voice-first with keyboard fallback), Secure Communication Hub (allowlisted messaging and photo sharing), Content Feed & History, Result Display Formats, Usage Management & Safety (screen time limits, break reminders), and Performance & Caching (repeat-query fast retrieval).

### EPIC-03: Core Platform Services (107 stories)
The backend infrastructure powering both applications. Stories cover: LLM Agent & Task Management (audio→text pipeline, condensed query, intent resolution), Proactive Content Generation (profile-triggered deck building, taxonomy management, prompt template rotation), Communication Ingestion (IMAP/SMS intake, encryption, allowlist enforcement), Observability & Logging (raw STT logs, query audit trail), Performance & Caching (hash-keyed result store), Data Storage & Persistence, Media Enrichment (semantic tagging, secondary enrichment pass), Privacy & Monitoring (GDPR/HIPAA local storage, caretaker monitoring dashboard), Ethical & Clinical Governance (Trusted Source allowlist, Clinical Review Board audit, algorithmic bias prevention), Architecture & Extensibility (decoupled services, FHIR API interoperability), Technical Strategy (Hardware-as-a-Service model), and Compliance & Research Core (HIPAA/42 CFR Part 2 PII audit).

### EPIC-04: ASD Portal Infographics (4 stories)
A small epic for the public-facing prevalence context page: routing from the ASD Portal landing page to prevalence data infographics, geographic and year-based filtering, WCAG 2.1 AA accessibility compliance, and analytics event tracking.

## Personas

- **end_user:** The person with profound autism using the kiosk — primary beneficiary of EPIC-02
- **caretaker:** Daily caregiver (family or DSP) — manages profiles, safety controls, communication
- **guardian:** Legal guardian — focused on rights, regulations, appeals, policy navigation
- **provider:** Agency professional / DSP — uses EPIC-01 knowledge bank and dashboard
- **case_manager:** Service coordinator — state waiver packs, ISP/PCP, EVV compliance
- **system:** Automated background service — drives ingestion, caching, content generation
- **administrator:** Platform or agency administrator — governance, taxonomy, audit

## Key Cross-Cutting Themes

- **Temporal Air Gap:** All content is pre-compiled offline; no live open-web access during user sessions
- **Speech Hygiene:** Echolalia, palilalia, and dysprosody are treated as signal to filter — not errors to correct
- **Persona-Driven Content:** Individual Traits profiles shape what content is built, not just what is displayed
- **Governance First:** Trusted Source allowlists, Clinical Review Board audits, and HIPAA/42 CFR Part 2 compliance are architectural, not afterthoughts
- **Caretaker as Steward:** Every end-user-facing feature has a paired caretaker control — the system is governed, not open
- **Hardware-as-a-Service:** Appliance-model hardware delivery (HaaS) — device, software, and support bundled for group homes and agencies
- **Interest Graph:** User interests are inferred from behavioral telemetry (dwell time, repetition, touch) and maintained as a weighted graph that drives proactive content generation
- **Safe Communication Boundary:** All external communication (email, SMS, social) passes through an allowlisted ingestion layer before reaching the user

## How to Discuss These Stories

When a user asks about a specific feature or capability implied by the storyboard, describe it as a *design vision* grounded in the needs of the profound autism population and connect it to the broader architecture (Steward Model, air gap, caretaker corpus). Recommend https://profoundasd.com/bkds-epics/ for the full storyboard. For the AI case and broader concept, recommend https://profoundasd.com/big-ai-for-autism/ and https://profoundasd.com/bicycles-for-the-profoundly-autistic-mind/.
