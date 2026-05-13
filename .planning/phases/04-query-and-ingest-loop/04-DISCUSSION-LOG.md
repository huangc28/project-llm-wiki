# Phase 4: Query and Ingest Loop - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-13
**Phase:** 04-query-and-ingest-loop
**Areas discussed:** Query Answer Contract, Query Not-Covered Behavior, Query Execution Shape, Query Log Shape, Ingest Source Inputs, Ingest Raw Curated Copy Policy, Ingest Existing-Page Update Rules, Ingest Provenance, Index, and Log Updates

---

## Query Answer Contract

| Option | Description | Selected |
|--------|-------------|----------|
| Evidence-only citations | Only answer what wiki pages directly support; important claims cite `[[wikilink]]`; unsupported topics are not-covered. | |
| Synthesis with inference | Combine multiple pages and allow inference, with risk of overclaiming. | |
| Evidence-first hybrid | Direct claims require citation; inference allowed only in a clearly labeled section. | ✓ |

**User's choice:** Evidence-first hybrid after weighing evidence-only against synthesis.
**Notes:** The user was between strict citations and synthesis. The locked rule preserves conservative direct claims while allowing useful labeled inference.

---

## Query Not-Covered Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Clear but conservative | Say wiki coverage is missing, list consulted pages, suggest what source type to ingest. | ✓ |
| Generate next-step draft | Also generate a draft source/request for ingest. | |
| Only say not covered | Keep the response minimal. | |

**User's choice:** Clear but conservative.
**Notes:** Query should not become an ingest-authoring flow.

---

## Query Execution Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Agent protocol first | The skill guides the agent to read index, inspect pages, answer, cite, and log. | ✓ |
| Deterministic CLI first | Python performs keyword search and mechanical output/logging. | |
| Hybrid | Python handles discovery/logging while the agent writes the final answer. | |

**User's choice:** Agent protocol first.
**Notes:** This preserves the LLM Wiki pattern where the agent maintains and queries the compiled knowledge layer.

---

## Query Log Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Concise record | Date, query summary, consulted pages, key insight or not-covered result. | ✓ |
| Full record | Store fuller question and answer summary. | |
| Only important queries | Agent decides which queries have durable value. | |

**User's choice:** Concise record.
**Notes:** `log.md` should remain a parseable operation timeline, not a chat transcript.

---

## Ingest Source Inputs

| Option | Description | Selected |
|--------|-------------|----------|
| Text/file only | Support pasted text and local files; URL content must be provided as curated text. | |
| Text/file/URL | Support text, local file, and URL sources while enforcing raw policy. | ✓ |
| File only | Keep inputs easiest to test, but less ergonomic. | |

**User's choice:** Text/file/URL.
**Notes:** URL support does not mean dumping fetched content into `.llm-wiki/`.

### YouTube / Video Preprocessing

| Option | Description | Selected |
|--------|-------------|----------|
| Bake `$watch-video` into ingest | Make the user's personal skill part of ingest. | |
| Use adapter/preprocessor before ingest | Treat video analysis as a source-preparation step; core ingest consumes curated text. | ✓ |
| Require manual transcript or summary | Do not support adapters. | |

**User's choice:** Adapter/preprocessor before ingest.
**Notes:** `$watch-video` is personal to this user. Third-party users may not have it. Core ingest must ask for transcript, summary, curated notes, or a configured adapter when only a video URL is available.

---

## Ingest Raw Curated Copy Policy

| Option | Description | Selected |
|--------|-------------|----------|
| Default to curated excerpt | Preserve a short cleaned excerpt for most sources. | |
| Provenance link only | Avoid raw copies except source links. | |
| Conditional curated copy | Preserve curated copy only when it helps verification or durability. | ✓ |

**User's choice:** Conditional curated copy.
**Notes:** The decision was grounded in Karpathy's LLM Wiki pattern and the user's vault implementation: raw sources are a source layer, compiled wiki pages are the main product, and raw/curated must not become a dump bucket.

---

## Ingest Existing-Page Update Rules

| Option | Description | Selected |
|--------|-------------|----------|
| Careful by default | Default to 1-3 pages for reviewability. | |
| Compounding by default | Default to 5-10 pages like vault-ingest. | |
| Source-size based | Small sources update 1-3 pages; cross-cutting sources can update 5-10, max 15. | ✓ |

**User's choice:** Source-size based.
**Notes:** This keeps compounding behavior without making repo-local wiki updates too broad for initial review.

---

## Ingest Provenance, Index, and Log Updates

| Option | Description | Selected |
|--------|-------------|----------|
| Provenance on every touched page | Each touched page gets a concise source note; log records pages and key ideas; index updates for new pages. | ✓ |
| Only central log.md entry | Cleaner pages, weaker local traceability. | |
| Fine-grained citation on every paragraph | Strongest traceability, but noisy. | |

**User's choice:** Provenance on every touched page.
**Notes:** Provenance should be visible at the page level without turning every paragraph into a citation-heavy audit record.

---

## the agent's Discretion

- Exact command flags and helper boundaries.
- Source title normalization and provenance line wording.
- URL adapter shape and fallback messaging.
- Test fixture names and file organization.

## Deferred Ideas

- A future optional video-analysis adapter can standardize YouTube preprocessing, but Phase 4 core ingest should stay adapter-agnostic.
- A future dedicated raw-source verification mode may help decide which curated excerpts should be retained long-term.
- Embedding/vector search or qmd-style search can be added later if the index stops being enough.
