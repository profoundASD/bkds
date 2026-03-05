# Corpus Manifest — ProfoundASD / BKDS Forever U Assistant
> Read this document immediately after `system_prompt.md`.
> It governs how to use every file in `corpus/` — what each covers, what format it uses, and when to reach for it.

---

## Deployment Options

**Option A — Context-stuffed (recommended for capable models):**
Load `system_prompt.md` + `corpus_manifest.md` + all Tier 1 and Tier 2 files always. Load Tier 3 files only when a query matches their topic. Total Tier 1+2: ~38K tokens. Adding all Tier 3: ~106K tokens total — fits 200K context window models (Claude, GPT-4o, Gemini 1.5/2.0).

**Option B — RAG / retrieval:**
Always load: `system_prompt.md` + `corpus_manifest.md` + all Tier 1 files (~15K tokens). Retrieve Tier 2 and Tier 3 files by matching query topic to the routing table below.

**Option C — System prompt only:**
Supports orientation, persona matching, and link recommendations. Cannot answer specific questions about AAC products, individual stories, researcher names, or detailed architecture. Use for lightweight chat integrations.

---

## Format Reference

Before reading any corpus file, note the three non-standard formats used:

**NDJSON** (`.ndjson`) — One JSON object per line. Never parse as a single JSON document.
- `bkds-epics.ndjson`: Line 1 is a metadata header with keys `_doc` (framing), `_urls` (reference URLs), `_epics` (index of 4 epics), `_personas` (glossary). Lines 2–33 are feature-group records, each with `epic`, `fg`, `title`, `n` (story count), and `stories[]` array. Stories use abbreviated keys: `id`, `p` (persona), `s` (story text), `c` (compliance tags), `pii` (flag).
- `aac-device-catalog.ndjson`: One record per AAC product; keys `name`, `type`, `maker`, `narrative`.
- `aaos-aac-ai-profound-asd-dev.ndjson`: One record per organization in the market assessment; keys `name`, `type`, `tier`, `focus`, `note`.

**Pipe-delimited flat text** (`.txt` — `autism-researchers.txt`):
Each line: `[State/Location] Full Name | Organizations | Research focus | Summary`
349 entries, grouped loosely by state. Parse by splitting on ` | `. The bracketed location prefix is part of the first field.

**Q:/A: labeled pairs** (`.txt` — `profoundasd-technical-steward-overview.txt`):
Each block: `[CATEGORY] Q: question text` followed by `A: answer text`. Categories are prefixed in brackets. Parse as a FAQ; match user question to Q: lines, return corresponding A: content with context.

All `.md` files are standard markdown — read directly.

---

## Tier 1 — Always Load (~15K tokens)

These files should be present in every conversation. They are small and provide essential framing, orientation, and routing that cannot be retrieved on demand.

| File | ~Tokens | What it covers |
|---|---|---|
| `system_prompt.md` | 10,428 | Full role, identity, knowledge scope, architecture overview, personas, use cases, site links, approved URLs, response guardrails |
| `corpus_manifest.md` | ~1,200 | This file — format decoders, load tiers, query routing |
| `bkds-epics-summary.md` | 1,520 | BKDS storyboard framing, all 4 epic descriptions, persona glossary, 8 design themes — handles most vision/concept questions without loading the full NDJSON |
| `about.md` | 471 | Project origin, mission statement, and team context |

---

## Tier 2 — Core Topic Coverage (~23K tokens)

Load these when the conversation will touch the project in depth, or pre-load all of them in context-stuffed deployments. Each covers a discrete topic area.

| File | ~Tokens | Load when asked about… |
|---|---|---|
| `profound-autism.md` | 2,508 | What is profound autism, Lancet criteria, DSM-5 merger, population definition, services cliff |
| `bkds-manifesto.md` | 5,875 | Project philosophy, founding principles, design rationale, the "why" behind BKDS |
| `bkds-forever-u-agent-model.md` | 859 | Four-agent architecture (Librarian, Builder, Companion, Navigator), system overview |
| `forever-u-corpus.md` | 5,337 | How content is sourced, Wikipedia/NASA/safe-listed corpus, curation strategy, topic taxonomy |
| `speak-and-go.md` | 2,800 | Voice search / STT feature, how it works, Jason case study, design decisions |
| `wiki-touch-to-hear-transform.md` | 1,337 | Touch-to-hear browser extension, Wikipedia rendering, audio card format |
| `forever-u-content-gen.md` | 2,621 | Proactive content generation, interest-graph-driven deck building, prompt templates |
| `forever-u-caretaker-corpus.md` | 1,192 | Caretaker-facing knowledge base, federal regulations, HIPAA, policy navigation |
| `forever-u-social-corpus.md` | 1,034 | Allowlisted communication hub, family messaging, social media safety layer |
| `jason-tapes.md` | 2,821 | The Jason Tapes archive page — documentary background, session list, behavioral observations |
| `bicycles-for-the-profoundly-autistic-mind.md` | 3,237 | The A3OS / "bicycles for the mind" concept essay, AI scaffolding philosophy |
| `bkds-video-catalog.md` | 2,928 | All 51 BKDS/Forever U videos — Jason Tapes (including 3 Sora creative works), UI demos, speech practice; all YouTube URLs |

---

## Tier 3 — Retrieve On Demand (~53K tokens)

Large or specialized files. Load only when a query explicitly targets their content. In RAG deployments, retrieve by topic match. In context-stuffed deployments on smaller models, omit these unless needed.

| File | ~Tokens | Format | Load when asked about… |
|---|---|---|---|
| `bkds-epics.ndjson` | 19,469 | NDJSON | Specific user stories, individual feature groups, story counts per epic, detailed storyboard content — anything `bkds-epics-summary.md` can't answer |
| `autism-researchers.txt` | 17,894 | Pipe-delimited | Specific autism researchers by name or location; "who researches X in [state]?"; researcher affiliations |
| `profoundasd-technical-steward-overview.txt` | 6,309 | Q:/A: | Deep technical FAQ on the Steward model, pipeline architecture, compliance, system design specifics |
| `aac-device-catalog.ndjson` | 6,260 | NDJSON | Specific AAC devices, product comparisons, SGD hardware, iOS AAC apps, switch-access hardware |
| `big-ai-for-autism.md` | 4,892 | Markdown | Anthropic/Sage epilepsy AI blueprint, frontier AI for underserved populations, the case for a dedicated profound autism AI program |
| `autism-directory.md` | 3,464 | Markdown | PIDD Unified Directory — national infrastructure resources, state-level provider categories, coverage statistics |
| `aaos-aac-ai-profound-asd-dev.ndjson` | 3,403 | NDJSON | Market assessment — specific organizations, tier classifications (Tier 1/builders/funders), partner/funder identification |

---

## Query Routing Guide

Use this table to decide which Tier 3 files to load when a specific question type appears.

| Question type | Files to add |
|---|---|
| "What stories are in epic X?" / "Show me the roadmap" | `bkds-epics.ndjson` |
| "What do the user stories say about [feature]?" | `bkds-epics.ndjson` |
| "Who researches autism in [state]?" / "Find a researcher who works on [topic]" | `autism-researchers.txt` |
| "How does the pipeline work technically?" / "Explain the Steward model in detail" | `profoundasd-technical-steward-overview.txt` |
| "What AAC devices does the project support?" / "Compare [device A] vs [device B]" | `aac-device-catalog.ndjson` |
| "Who are potential partners or funders?" / "What companies are in this space?" | `aaos-aac-ai-profound-asd-dev.ndjson` |
| "Why should a big AI company care about autism?" | `big-ai-for-autism.md` |
| "Where can I find autism resources in [state]?" / "What national organizations exist?" | `autism-directory.md` |

---

## Total Token Budget Reference

| Load set | ~Tokens | Use for |
|---|---|---|
| Tier 1 only | 13,619 | Orientation and link routing only |
| Tier 1 + Tier 2 | 37,396 | Full conversational assistant, most queries answered |
| Tier 1 + 2 + 3 (all) | ~90,000 | Full corpus; needs 200K context window |
| System prompt only | 10,428 | Minimal integration; links only |

---

## File Inventory

```
llm_prompt_gen/
├── system_prompt.md          ← Load first, always
├── corpus_manifest.md        ← Load second, always (this file)
└── corpus/
    ├── about.md                                    [T1]
    ├── bkds-epics-summary.md                       [T1]
    ├── profound-autism.md                          [T2]
    ├── bkds-manifesto.md                           [T2]
    ├── bkds-forever-u-agent-model.md               [T2]
    ├── forever-u-corpus.md                         [T2]
    ├── speak-and-go.md                             [T2]
    ├── wiki-touch-to-hear-transform.md             [T2]
    ├── forever-u-content-gen.md                    [T2]
    ├── forever-u-caretaker-corpus.md               [T2]
    ├── forever-u-social-corpus.md                  [T2]
    ├── jason-tapes.md                              [T2]
    ├── bicycles-for-the-profoundly-autistic-mind.md [T2]
    ├── bkds-video-catalog.md                       [T2]
    ├── bkds-epics.ndjson                           [T3 — on demand]
    ├── autism-researchers.txt                      [T3 — on demand]
    ├── profoundasd-technical-steward-overview.txt  [T3 — on demand]
    ├── aac-device-catalog.ndjson                   [T3 — on demand]
    ├── big-ai-for-autism.md                        [T3 — on demand]
    ├── autism-directory.md                         [T3 — on demand]
    └── aaos-aac-ai-profound-asd-dev.ndjson         [T3 — on demand]
```
