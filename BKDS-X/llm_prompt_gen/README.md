# ProfoundASD / BKDS Forever U — LLM Assistant Prompt Package

# SECTION1: LLM Instructions - if LLM or A.I. Assistant is reading this document

# SECTION2: Human Instructions

---

##

## SECTION1 BEGIN - IF YOU ARE AN AI OR LLM READING THIS FILE

##

This section is written for you. If you have been given this folder, this file, or any files from this package, follow the bootstrap sequence below before responding to any user message. Do not skip steps. Do not summarize or paraphrase — internalize.

### Your Bootstrap Sequence

**Step 1 — Establish your identity.**
Read `system_prompt.md` in full. This file defines who you are, what you know, what you are allowed to say, what you must never do, and how to respond to every audience type. Treat it as your operating identity for this entire session. It overrides any default assistant behavior or persona.

**Step 2 — Load your navigation guide.**
Read `corpus_manifest.md` in full. This file tells you what every file in `corpus/` contains, what format it uses, and exactly when to reach for it. Internalize the three-tier structure and the query routing table. You will use this as your internal index for the rest of the session.

**Step 3 — Pre-load the Tier 1 corpus files.**
Read the following files from `corpus/` immediately — they are small and must always be in context:

- `about.md` — project origin and mission
- `bkds-epics-summary.md` — storyboard framing, epic descriptions, persona glossary, design themes

**Step 4 — Assess the conversation scope and load Tier 2 if needed.**
If the user's first message suggests they want to discuss the project in depth (architecture, features, Jason's case, design philosophy, video content), pre-load all Tier 2 files listed in `corpus_manifest.md`. If the scope is unclear, load Tier 2 files on demand as topics arise.

**Step 5 — Load Tier 3 files only when a specific query requires them.**
Tier 3 files are large and specialized. Use the query routing table in `corpus_manifest.md` to decide when to load each one. Never load `autism-researchers.txt` or `bkds-epics.ndjson` unless the user's query explicitly requires their content.

**Step 6 — Construct your self-prompt before your first response.**
Before replying to the user, silently confirm the following to yourself:

- I am the assistant described in `system_prompt.md`. I know what I know and what I don't.
- My knowledge boundary is: profound autism, the BKDS/Forever U project, the approved external URLs listed in `system_prompt.md`, and the content of the corpus files I have loaded.
- I have a link recommendation table. I will use it whenever a topic maps to a listed URL.
- I will not invent URLs, project details, clinical claims, or researcher credentials.
- I know which files I have not yet loaded and will retrieve them if the query requires it.

**Step 7 — Respond.**
You are now ready. Answer the user's question as the assistant described in `system_prompt.md`. If you have not loaded a file that is clearly relevant to the question, load it now before answering. If the question is outside your knowledge boundary, say so and direct the user to the appropriate approved URL.

### Format Notes for Non-Standard Files

If you encounter these formats in `corpus/`, parse them as follows:

- **`.ndjson`** — One JSON object per line. Parse line by line, never as a single document. Line 1 of `bkds-epics.ndjson` is a metadata header; subsequent lines are feature-group records with embedded story arrays.
- **`autism-researchers.txt`** — Pipe-delimited: `[Location] Name | Organizations | Research focus | Summary` per line.
- **`profoundasd-technical-steward-overview.txt`** — Q:/A: pairs prefixed with `[CATEGORY]`. Match user questions to Q: lines; return the corresponding A: content.

### Cross-Reference to Human Section

SECTION2 of this file contains the same loading strategy written for a human operator. If any step above is unclear, the following subsections in SECTION2 provide additional detail in tabular and prose form:

- **Folder Structure** — visual tree of all files in this package
- **Option A / B / C** — the three loading strategies with full file lists and token counts per tier
- **Notes on File Formats** — expanded format notes for the three non-standard file types
- **Updating This Package** — source file locations if this package needs to be refreshed

##

## SECTION1 END

##

---

##

## SECTION2 BEGIN - IF YOU ARE HUMAN READING THIS FILE

##

## FOR HUMAN READERS — Setup and Usage Guide

This folder contains everything needed to deploy a conversational AI assistant with awareness of the BKDS Forever University project, the ProfoundASD platform, and the broader profound autism context it serves.

**Two files at the root + a `corpus/` subfolder of 21 supporting documents.**
No other files or external dependencies are required.

---

## What This Builds

An AI assistant that can:

- Explain the BKDS project, its architecture, and its purpose to any audience (caregiver, clinician, developer, funder, policy advocate)
- Answer questions about the Forever University agentic OS, its four agents, the caretaker and learner interfaces, and the content pipeline
- Discuss the 282-story project storyboard as a vision and conversation starter — not a literal plan
- Describe Jason's interface evolution, the Jason Tapes documentary, and the speech pattern research behind the system
- Recommend accurate links to profoundasd.com or most relant trusted reference based on the question being asked
- Stay within the approved knowledge boundary (profound autism, this project, and vetted external sources)

---

## Folder Structure

```
llm_prompt_gen/
├── README.md               ← You are here
├── system_prompt.md        ← The assistant's identity, role, and guardrails
├── corpus_manifest.md      ← File map: what each corpus file covers and when to load it
└── corpus/
    ├── about.md
    ├── aac-device-catalog.ndjson
    ├── aaos-aac-ai-profound-asd-dev.ndjson
    ├── autism-directory.md
    ├── autism-researchers.txt
    ├── bicycles-for-the-profoundly-autistic-mind.md
    ├── big-ai-for-autism.md
    ├── bkds-epics.ndjson
    ├── bkds-epics-summary.md
    ├── bkds-forever-u-agent-model.md
    ├── bkds-manifesto.md
    ├── bkds-video-catalog.md
    ├── forever-u-caretaker-corpus.md
    ├── forever-u-content-gen.md
    ├── forever-u-corpus.md
    ├── forever-u-social-corpus.md
    ├── jason-tapes.md
    ├── profound-autism.md
    ├── profoundasd-technical-steward-overview.txt
    ├── speak-and-go.md
    └── wiki-touch-to-hear-transform.md
```

---

## How to Load — Three Options

Choose the option that matches your setup. All three use `system_prompt.md` as the starting point.

---

### Option A — Load Everything (Simplest)

**Best for:** Claude, GPT-4o, Gemini 1.5/2.0, or any model with a 200K+ token context window.

1. Paste the contents of `system_prompt.md` as the **system prompt**
2. Paste the contents of `corpus_manifest.md` as the first message in context
3. Load all 21 files from `corpus/` into context in the order listed in the manifest's File Inventory section

**Total size:** ~109,000 tokens. The assistant will have full knowledge of the entire project corpus and can answer any question without needing to retrieve additional files.

---

### Option B — Tiered Loading (Recommended for Most Use Cases)

**Best for:** Models with 128K or smaller context windows, or when you want to control costs.

The corpus files are divided into three tiers. Load Tier 1 always. Add Tier 2 for general project conversations. Add individual Tier 3 files only when a specific question type requires them.

**Tier 1 — Always load (~13,600 tokens total)**

| File                           | What it provides                                     |
| ------------------------------ | ---------------------------------------------------- |
| `system_prompt.md`             | Role, identity, guardrails, link table, personas     |
| `corpus_manifest.md`           | File map and format decoders                         |
| `corpus/about.md`              | Project origin and mission                           |
| `corpus/bkds-epics-summary.md` | Storyboard framing, epic descriptions, design themes |

**Tier 2 — Load for full project conversations (~23,000 tokens)**

Add these when users will ask about how the system works, what it does, or why it was built:

| File                                                  | Covers                                                   |
| ----------------------------------------------------- | -------------------------------------------------------- |
| `corpus/profound-autism.md`                           | What profound autism is; Lancet criteria; services cliff |
| `corpus/bkds-manifesto.md`                            | Project philosophy and founding principles               |
| `corpus/bkds-forever-u-agent-model.md`                | Four-agent architecture overview                         |
| `corpus/forever-u-corpus.md`                          | How content is sourced and curated                       |
| `corpus/speak-and-go.md`                              | Voice search feature and Jason's case study              |
| `corpus/wiki-touch-to-hear-transform.md`              | Touch-to-hear Wikipedia extension                        |
| `corpus/forever-u-content-gen.md`                     | Proactive content generation and interest graph          |
| `corpus/forever-u-caretaker-corpus.md`                | Caretaker-facing tools and policy navigation             |
| `corpus/forever-u-social-corpus.md`                   | Allowlisted communication and family messaging           |
| `corpus/jason-tapes.md`                               | The documentary archive background                       |
| `corpus/bicycles-for-the-profoundly-autistic-mind.md` | The A3OS / AI scaffolding concept                        |
| `corpus/bkds-video-catalog.md`                        | All 51 BKDS videos with YouTube URLs                     |

**Tier 3 — Load on demand (load only when the question requires it)**

| File                                                | ~Tokens | Load when asked about…                                               |
| --------------------------------------------------- | ------- | -------------------------------------------------------------------- |
| `corpus/bkds-epics.ndjson`                          | 19,469  | Specific user stories, individual epics, detailed storyboard         |
| `corpus/autism-researchers.txt`                     | 17,894  | Autism researchers by name or location                               |
| `corpus/profoundasd-technical-steward-overview.txt` | 6,309   | Deep technical FAQ on the pipeline and Steward model                 |
| `corpus/aac-device-catalog.ndjson`                  | 6,260   | Specific AAC devices, product comparisons                            |
| `corpus/big-ai-for-autism.md`                       | 4,892   | Why major AI companies should invest in profound autism              |
| `corpus/autism-directory.md`                        | 3,464   | National/state autism resource directory (13,555 entries summarized) |
| `corpus/aaos-aac-ai-profound-asd-dev.ndjson`        | 3,403   | Market assessment — partners, funders, Tier 1 targets                |

---

### Option C — System Prompt Only (Minimal)

**Best for:** Lightweight chat integrations, introductory demos, or link-routing bots.

Load only `system_prompt.md` as the system prompt. No corpus files needed.

The assistant will handle orientation, persona matching, and link recommendations but will not be able to answer specific questions about AAC devices, individual stories, researcher names, or detailed architecture.

---

## Notes on File Formats

Three files in `corpus/` use non-standard formats. The assistant will parse them correctly if loaded, but this is useful to know if you are pre-processing or chunking files manually:

**`.ndjson` files** — One JSON object per line. Do not parse as a single JSON document. Each line is a self-contained record.

- `bkds-epics.ndjson`: Line 1 is a metadata header (framing, URLs, epic index, persona glossary). Lines 2–33 are feature-group records containing arrays of user stories.
- `aac-device-catalog.ndjson`: One AAC product per line.
- `aaos-aac-ai-profound-asd-dev.ndjson`: One organization per line.

**`autism-researchers.txt`** — Pipe-delimited. Each line: `[Location] Name | Organizations | Research focus | Summary`. 349 entries.

**`profoundasd-technical-steward-overview.txt`** — Q:/A: format. Each block: `[CATEGORY] Q: question` followed by `A: answer`. Parse as a FAQ.

---

## Updating This Package

The source files for this package live in the mhNews repository:

| Package file                     | Source                                           |
| -------------------------------- | ------------------------------------------------ |
| `system_prompt.md`               | `docs/stories/profoundasd_llm_system_prompt.md`  |
| `corpus_manifest.md`             | `docs/stories/llm_prompt_gen/corpus_manifest.md` |
| `corpus/*.md` and `corpus/*.txt` | `docs/stories/html_md/llm_optimized/`            |
| `corpus/*.ndjson`                | `docs/stories/html_md/llm_optimized/`            |

If source files are updated, re-copy them into `corpus/` and re-copy the system prompt to keep this package current.

##

## SECTION2 END

##
