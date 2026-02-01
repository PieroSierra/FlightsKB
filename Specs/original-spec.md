This is enough to write an agent spec — but I’d add a few **non-negotiables** that will save you pain later: (1) a manifest + IDs, (2) deterministic rebuilds, (3) provenance + licensing flags, (4) evaluation hooks (even lightweight), and (5) a dead-simple deployment shape.

Below is a **ready-to-hand spec** you can paste to your agent.

---

## Flights KB Playground — Agent Spec (build plan)

### 0) Goal

Build a lightweight “Flights KB Playground” that:

- stores flight-related knowledge as **human-editable Markdown** in a folder structure,

- generates a **derived vector index** for semantic retrieval,

- exposes a **console** for ingestion, inspection, querying, rebuilds, and stats,

- is **cloud-hosted** for internal PM prototype access (not production-grade).

Non-goals:

- scale, rigorous correctness, high security, enterprise auth, uptime guarantees.

---

## 1) High-level architecture

### 1.1 Canonical Knowledge Store (Git-backed)

- Repository folder: `knowledge/` (Markdown is source of truth)

- Each `.md` file:
  
  - YAML frontmatter (document-level metadata)
  
  - “cards” (each `##` section = chunk boundary)

### 1.2 Derived Retrieval Index (Vector DB)

- Choose any vector DB (default acceptable: Chroma).

- Embeddings model is agent-chosen.

- Vector index is **rebuildable** from the Markdown store at any time.

- Store for each chunk:
  
  - chunk_id, text, metadata, source references

### 1.3 Playground API (optional but recommended)

- A minimal HTTP API to support PM prototypes:
  
  - `/query` (text, k, filters) → chunks + scores
  
  - `/stats`
  
  - `/rebuild` (protected by simple shared secret or local-only)

- Console can call the API or operate directly on local index.

---

## 2) Repository layout

Create this structure:

```
flights-kb/
  knowledge/
    airlines/
    loyalty/
    hacks/
    airports/
    lounges/
    reviews/
    pricing-curves/
    inbox/
  templates/
  tools/
    chunker/
    console/
  index/
    manifests/
    snapshots/
  server/                 # optional
  README.md
```

Rules:

- Categories are folder-based and extensible.

- Prefer entity-first subfolders when obvious (airlines by IATA code, airports by IATA code).

---

## 3) Markdown schema (document-level)

### 3.1 Required YAML frontmatter

Each file must begin with:

```yaml
---
kb_id: <globally-unique-stable-id>
type: <string>               # e.g. airline_premium_fare, hack, lounge_tip
title: <string>
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: draft|reviewed|deprecated
source:
  kind: internal|ugc|marketing|press|blog|forum|other
  name: <string>
  url: <string|null>
  retrieved: YYYY-MM-DD|null
confidence: low|medium|high
---
```

### 3.2 Optional YAML fields (supported)

```yaml
tags: [ ... ]
entities:
  airline: BA
  alliance: oneworld
  airports: [LHR, JFK]
  routes: ["LHR-JFK"]
  cabins: [premium_economy, business]
  aircraft: ["A350-1000"]
  flight_numbers: ["BA117"]
temporal:
  effective_from: YYYY-MM-DD|null
  effective_to: YYYY-MM-DD|null
geo:
  regions: [EU, US]
audience: pm|traveler|ops|mixed
license:
  reuse: ok|restricted|unknown
  notes: <string|null>
```

**Important:** `kb_id` must be stable across rebuilds; it should not depend on chunk ordering.

---

## 4) “Card” schema (chunk-level)

### 4.1 Chunk boundaries

- Each `## <heading>` section is one chunk (“card”).

- If a card is too large, split by `###` subheadings.

- Preserve a minimal header in every chunk:
  
  - title/heading
  
  - Claim type
  
  - Applies to
  
  - Summary

### 4.2 Recommended card format

Within each `##` section, support:

- `**Claim type:** fact|evaluation|tactic|rule_of_thumb|warning|comparison`

- `**Applies to:**` a simple selector DSL

- `**Summary:**` (required)

- Optional: `Details`, `Traveler impact`, `Caveats`, `Evidence`, `Confidence`

Example:

```md
## Rule of thumb: LHR→JFK best booking window
**Claim type:** rule_of_thumb
**Applies to:** routes=LHR-JFK
**Summary:** Best booking window tends to be ~20–30 days before departure.
**Details:** ...
**Caveats:** ...
**Evidence:** internal ML curve model; aggregated historical pricing
**Confidence:** high
```

### 4.3 Applies-to DSL parsing

Parse these keys when present:

- `airline=BA`

- `airports=LHR,JFK`

- `routes=LHR-JFK`

- `cabin=business`

- `aircraft=A350-1000`

- `flight=JL207`

- `alliance=oneworld`

- `region=EU`

Normalize into lists in metadata.

### 4.4 Optional structured payload

If a card contains a fenced JSON block, attach it to chunk metadata as `structured_blob` and keep the chunk text intact.

---

## 5) Chunker requirements (tooling)

Implement a deterministic chunker that outputs a list of chunk records:

Each record must include:

- `chunk_id` = `${kb_id}#${slug(heading)}`

- `doc_id` = `kb_id`

- `title` = section heading

- `text` = card markdown (including key fields)

- `metadata` = merged doc-level + card-level selectors

- `source` = doc-level `source` + evidence line if present

- `hash` = content hash for incremental rebuilds

Determinism:

- Running chunker twice on same repo yields identical chunk_id and identical chunk text.

Incremental indexing (nice-to-have):

- Only re-embed / reindex chunks with changed `hash`.

---

## 6) Vector index requirements

Store:

- embeddings per chunk

- chunk text + metadata

- similarity score on retrieval

- filters on metadata (if supported by DB)

Query function:

- Input: `query_text`, `k`, optional `filters` dict

- Output: top-k results with:
  
  - `chunk_id`, `kb_id`, `title`, `text`, `metadata`, `score`

---

## 7) Console requirements

Provide a CLI or simple web console with commands:

### 7.1 Query / inspect

- `query --k 3 --text "business class" [--filters airline=BA,cabin=business]`

- Print:
  
  - scores
  
  - chunk titles
  
  - chunk text excerpt
  
  - metadata
  
  - chunk_id + file path back-link

### 7.2 Ingest new knowledge

Support ingestion sources:

- raw pasted text

- local file: `.txt`, `.md`, `.pdf`, `.html/.htm`

- optional: URL ingestion (recommended **only** if you store URL + retrieved date + license/reuse flags)

Ingestion outputs:

- Create Markdown file(s) under `knowledge/inbox/`:
  
  - 1 document with frontmatter
  
  - multiple `##` cards extracted by heuristic chunking

- Do not directly index raw scraped content without recording provenance.

### 7.3 Rebuild index

- `rebuild` rebuilds vector index from `knowledge/` (optionally incremental).

### 7.4 Stats

- total documents, total chunks

- chunks by type/category

- chunks by confidence/status

- last rebuild time, embedding model name, vector DB type

- optional: duplicates heuristic (near-identical chunks)

---

## 8) Hosting & access (playground-grade)

Choose a simple approach:

- Host the API on a small cloud runtime (Render/Fly.io/Railway/Vercel/serverless/etc.)

- Persist vector DB storage in a mounted volume or managed storage (or just rebuild on deploy).

Security:

- Minimal: shared secret token in header for write operations (ingest/rebuild).

- Query endpoint may be open or lightly protected (your call).

- Add a clear warning in README: “playground only.”

---

## 9) Provenance, licensing, and safety rails (important)

Every ingested doc must record:

- source kind + name + URL (if applicable) + retrieved date

- `license.reuse` flag: `ok|restricted|unknown`

Policy:

- Default `license.reuse=unknown` for web content unless explicitly safe.

- Avoid storing large verbatim copies of copyrighted articles; store **summaries + quotes** where needed and keep quotes short.

---

## 10) Minimal evaluation hooks (to avoid “it feels good”)

Include a tiny `eval/` capability:

- a YAML file of ~20 test queries with expected target kb_ids or topics

- console command: `eval` → report recall@k and show misses  
  This keeps you honest as the KB grows.

---

## 11) Deliverables

1. Repo scaffold with folders + templates

2. Chunker implementation + tests for deterministic IDs

3. Console (CLI) with query/ingest/rebuild/stats

4. Vector DB integration

5. (Optional) hosted query API + basic auth token

6. README explaining workflow for PMs

---

## A note on URL ingestion

Yes, it can make sense — **if** you:

- store URL + retrieved date,

- extract + chunk,

- and save *summarized cards* (not entire scraped pages),

- track `license.reuse`.

Otherwise: “export to PDF and ingest” is fine for a playground.

---

Final note:  let's also generate **two templates** in `/templates/`:

- `airline_premium_fare_template.md`

- `hack_template.md`

So PMs don’t invent their own formats on day 1.
