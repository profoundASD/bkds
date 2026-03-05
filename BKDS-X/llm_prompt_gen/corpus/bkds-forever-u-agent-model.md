System Architecture v0.6.0

# The Steward Model

An agentic orchestration model where AI serves as a governed manufacturer of stable content, not an improv artist. The system splits into two secured loops: **"Forever University"** for the learner and **"The Navigator"** for the caregiver.

Wikipedia / NASA APIs Caregiver Constraints "Speak and Go" Voice Clinical/Legal Docs

## The Steward

Orchestration & State Manager

Semantic Routing • Enforce Air Gap • Audit

Agent A

The Librarian

Corpus Ingest

Connects to raw data sources (Wikipedia, Flickr, Donated Textbooks) and normalizes them into a safe schema.

  - Normalize JSON Schema
  - License Check
  - SafeSearch Filter

Agent B

The Builder

Forever U Compiler

Assembles "Content Packs" tailored to the Learner Profile. Pre-compiles logic so runtime is deterministic.

  - Systemizing Layouts
  - Interest Graphing
  - Stamina Slicing

Agent C

The Navigator

Hybrid RAG + Tools

A restricted assistant for caregivers. Uses Tool Use for visualization and Multi-Index RAG for citations.

  - The Vault (Stats/Data)
  - The Library (Science)
  - Visual Code Interpreter

Agent D

The Companion

Runtime Player

The user-facing engine. Handles "Speak and Go" voice search and executes the **Care Plan** routines.

  - Resolve Voice Intent
  - Loop Breaking
  - Routine Ledger

## Two Distinct Use-Cases

The platform architecture recognizes that the **Learner** and the **Caregiver** require fundamentally different AI behaviors. The Steward ensures these personas never cross-contaminate (e.g., medical data never leaks to the student; unverified web results never reach the caregiver).

1\. Forever University

Target: The End User (Student)

For the student, the system acts as a **Deterministic Manufacturer**. We do not use "Generative AI" at runtime. Instead, "The Builder" pre-compiles safe interest stacks (Decks) from Wikipedia/NASA data based on the user's profile.

  - **Compile-Then-Play:** Content is generated, reviewed by the caregiver, and locked into a "World Version" before the student sees it.
  - **Speak & Go:** Voice input maps strictly to the pre-compiled library. If a user asks for "Trains," they get the approved Train Deck, not a Google Search.
  - **Loop Breaking:** "The Companion" monitors for perseveration and offers gentle "bridges" to related topics.

2\. The Navigator

Target: The Caregiver

For the caregiver, the system acts as a **Hybrid RAG Analyst**. It combines "Code Interpreter" tools for data visualization with strict RAG for documents.

  - **Strict Partitioning:** Knowledge is scoped to trusted domains (DSM-5, IDEA, ADA.gov). Off-topic queries (fashion, pop culture) are rejected by the Steward.
  - **Tool Use, Not Hallucination:** Visualizations are retrieved or generated via code from verified ADDM/IDEA datasets, never drawn by the LLM.
  - **Liability Gates:** Hard-coded prompts append "Not Medical/Legal Advice" disclaimers to sensitive outputs.

#### The "Temporal Air Gap"

In profound autism, unexpected changes can be dysregulating. The Steward Model enforces a **Temporal Air Gap** between data ingestion and user presentation.

_"The Builder"_ generates content offline (Compile Time). _"The Steward"_ validates it against safety gates. Only then does _"The Companion"_ serve it to the user (Run Time). This ensures that no prompt injection, hallucination, or broken link ever occurs during a live session.
