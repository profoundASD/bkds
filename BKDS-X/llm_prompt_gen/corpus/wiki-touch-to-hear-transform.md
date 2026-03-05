Assistive Technology Architecture

#  The Architecture of Access

OpenAI Sora visualizes Koala using BKDS touch-to-hear wiki transformed page.

How two complementary browser extensions dismantle Wikipedia's density to build a voice-first experience.

The Historical Context

##  Evolution of Complexity

The project began when Wikipedia was visually dense. In 2022, Wikipedia rolled out a cleaner "Vector" design. While it reduced visual noise, the design **does not simplify enough for the accessibility needs of the user.**

2010 — 2022

### Legacy Vector

The "busy" layout. Sidebars, dense text, and small typography created immediate sensory overload for neurodivergent users.

HIGH VISUAL NOISE

2022 — Present

### Modern Vector

The current default. It introduced whitespace and sticky headers. Better for general users, but the **cognitive load** (reading level, navigation) remains unchanged.

HIGH COGNITIVE LOAD

The ProfoundASD Approach

###  The Transformed Experience

Stripping away both the visual noise _and_ the navigational abstraction. The extension survives the 2022 redesign because it solves a different problem: **Interaction.**

  - › **Linear Focus:** No sidebars, no sticky headers, just the story.
  - › **Touch-First:** Mouse interactions are replaced by large-target touch zones.
  - › **Sentence Isolation:** Break the "wall of text" that persists even in the 2022 layout.

Reader UI & Search Controls

System Design

##  Two Extensions, One Mission

Split the problem into two distinct phases: **Transformation** and **Interaction**. By decoupling the heavy page processing from the user interaction layer, the solution achieved reliable performance and stability.

A

### The Architect

extWikiReader

A heavyweight content transformer that intercepts the page load. It suppresses the default UI, parses the text into semantic chunks, and builds a dedicated overlay.

  - ✓ Locks Scroll & Hides Chrome
  - ✓ Parses NLP-Lite Sentences
  - ✓ Injects `touch-to-hear` markers

Logic Inspection

###  Anatomy of a Transformation

The parser doesn't just split text; it rebuilds the page. It must differentiate between a period that ends a sentence and a period inside an abbreviation (like "U.S." or "Jan.").

1

Raw Input

"The C-130 entered service with the U.S. in 1956."

2

Abbreviation Shielding

Regex identifies `U.S.` as a protected token, preventing a false sentence break.

3

DOM Injection

The sentence is wrapped in a span with a sequential ID.

RENDERED HTML

<span touch-to-hear id="chunk-42">

The C-130 entered service with the U.S. in 1956.

</span>

This ID allows `scrollIntoView()` to auto-center the reading experience.

B

### The Enabler

extTouchToHear

A lightweight interaction layer. It doesn't need to understand the page structure—it simply looks for the markers left by the Architect.

  - ✓ Zero DOM Processing Load
  - ✓ Responds to Click/Touch
  - ✓ Uses Web Speech API

###  Markup Transformation Details

Fig A. DOM Injection

Fig B. Chunkified & Tagged

##  The "NLP-Lite" Engine

The core features is the `splitTextIntoSpans` function. It transforms a wall of text into a database of speakable chunks. It handles common abbreviations (Mr., Dr., U.S.) to avoid false sentence breaks, ensuring the audio flow is natural.


    // Simplified chunking logic
    function splitTextIntoSpans(text) {
      // 1. Sanitize abbreviations
      // 2. Split by Regex sentence boundaries

      return sentences.map((s, i) =>
        `<span touch-to-hear id="chunk-${i}">
           ${s}
         </span>`
      ).join(" ");
    }

*Actual implementation includes robust regex for 40+ abbreviation cases.

###  Processing Pipeline

User Experience

## The Interaction Bridge

Because `extWikiReader` has already done the heavy lifting of marking every sentence, the `extTouchToHear` extension can be incredibly fast. It essentially asks one question upon every click:

"Does this element have the **touch-to-hear** attribute?"

If yes, it speaks. If no, it ignores. This creates a "safe" browsing environment where errant clicks on whitespace or images don't trigger confusing audio feedback.

##  Architecture Comparison

Feature |  Standard Screen Reader  |  The Architecture
---|---|---
Visual Context | Linear (reads everything) | Curated (Article Text + Image Gallery only)
Sentence Awareness | Limited / DOM-based | High / Regex-processed chunking
Interaction | Keyboard nav / Swipe | Touch-to-Hear (Random Access)
Focus Management | Outline border | Auto-scroll & Highlight (#F9D8A7)

The Ecosystem

## Beyond the Wiki Reader

This extension is just one output mechanism. Explore the underlying engines that power the broader content ecosystem.

 System 01  Systemizing Content Generator  The logic engine that powers the transformation. See how we automate the creation of systemized, high-clarity views from raw input data.    System 02  The Forever U Corpus  The broader library concept. A curated, safe universe of interest-based content designed for the specialized needs of the user.

Live Demo

## System Demonstration

Real-world usage of the transformation engine and touch interactions in the customized library environment.

Wiki Reader / Touch-To-Hear Demo

Wiki Reader Demo - Part 2

Touch-to-Hear: Learning New Words

UI Overview & Search Navigation
