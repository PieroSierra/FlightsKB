# Quickstart: Flights KB Playground

**Branch**: `001-flights-kb-playground`
**Created**: 2026-02-01

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd flights-kb

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Quick Setup

```bash
# Initialize the knowledge directory structure
flightskb init

# This creates:
# knowledge/
#   airlines/
#   airports/
#   loyalty/
#   hacks/
#   lounges/
#   reviews/
#   pricing-curves/
#   inbox/
# templates/
# eval/
```

## CLI Commands

### Query the Knowledge Base

Search for relevant knowledge using natural language:

```bash
# Basic query
flightskb query "business class tips for LHR to JFK"

# Specify number of results
flightskb query --k 10 "best airline lounges"

# Filter by metadata
flightskb query --filters "airline=BA,cabin=business" "premium economy tips"

# Output as JSON
flightskb query --json "booking window advice"
```

**Example output:**
```
Query: "business class tips for LHR to JFK"
Results: 3

[1] Score: 0.92
    Title: Rule of thumb: LHR→JFK best booking window
    File: airlines/BA/premium-economy.md
    ID: ba-premium-economy-2024#booking-window-tips
    ---
    Best booking window tends to be ~20–30 days before departure.
    **Evidence:** internal ML curve model

[2] Score: 0.87
    Title: BA Business Class Seat Selection Hack
    ...
```

### Ingest New Knowledge

Add content to the knowledge base:

```bash
# From raw text (opens editor or reads from stdin)
flightskb ingest --text "Paste your content here"

# From a local file
flightskb ingest --file ./my-notes.txt
flightskb ingest --file ./article.pdf
flightskb ingest --file ./webpage.html

# From URL (stores provenance)
flightskb ingest --url "https://example.com/article"

# Specify source metadata
flightskb ingest --file ./notes.md --source-kind internal --source-name "PM Research"
```

**What happens:**
1. Content is parsed and chunked
2. YAML frontmatter is generated with provenance
3. File saved to `knowledge/inbox/` for review
4. Run `rebuild` to index the new content

### Rebuild the Index

Regenerate the vector index from knowledge files:

```bash
# Full rebuild
flightskb rebuild

# Verbose output
flightskb rebuild --verbose
```

**Example output:**
```
Rebuilding index...
Processing: knowledge/airlines/BA/premium-economy.md
Processing: knowledge/hacks/booking-windows.md
...

Rebuild complete:
  Documents: 42
  Chunks: 156
  Duration: 12.5s
  Model: all-MiniLM-L6-v2
```

### View Statistics

Get an overview of the knowledge base:

```bash
# Summary stats
flightskb stats

# Detailed breakdown
flightskb stats --detailed

# JSON output
flightskb stats --json
```

**Example output:**
```
Flights KB Statistics
=====================

Documents: 42
Chunks: 156

By Type:
  hack: 45
  airline_premium_fare: 32
  lounge_tip: 28

By Confidence:
  high: 89
  medium: 52
  low: 15

Index Info:
  Last rebuild: 2026-02-01 14:30:00
  Model: all-MiniLM-L6-v2
  Vector DB: chromadb
```

### Evaluate Retrieval Quality

Run evaluation against test queries:

```bash
# Run evaluation
flightskb eval

# Specify test file
flightskb eval --queries eval/test_queries.yaml

# Verbose with details
flightskb eval --verbose
```

**Example output:**
```
Running evaluation: 20 test queries

Results:
  Recall@3: 0.90 (18/20 queries found expected results)

Misses:
  Query: "alliance upgrade rules"
    Expected: oneworld-upgrade-2024
    Got: star-alliance-upgrade, skyteam-upgrade

Overall: PASS (>= 0.90 threshold)
```

## Creating Knowledge Documents

### Document Template

Create a new document in `knowledge/{category}/`:

```markdown
---
kb_id: unique-document-id-2024
type: hack
title: "Your Document Title"
created: 2026-02-01
updated: 2026-02-01
status: draft
source:
  kind: internal
  name: "Your Name"
  url: null
  retrieved: null
confidence: medium
tags: [booking, tips]
entities:
  airline: BA
  airports: [LHR, JFK]
  cabins: [business]
---

## First Card Title
**Claim type:** rule_of_thumb
**Applies to:** airline=BA, cabin=business
**Summary:** Brief summary of this knowledge card.

Details go here...

## Second Card Title
**Claim type:** fact
**Summary:** Another piece of knowledge.

More details...
```

### Using Templates

Copy from existing templates:

```bash
# List available templates
ls templates/

# Copy a template
cp templates/hack_template.md knowledge/hacks/my-new-hack.md
```

## HTTP API (Optional)

Start the API server for remote access:

```bash
# Start server
flightskb serve

# With custom port
flightskb serve --port 8080

# With API key for protected endpoints
export FLIGHTSKB_API_KEY="your-secret-key"
flightskb serve
```

**Endpoints:**
- `POST /query` - Search knowledge base
- `GET /stats` - Get statistics
- `POST /rebuild` - Rebuild index (requires API key)
- `GET /health` - Health check

**Example API usage:**
```bash
# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"text": "business class tips", "k": 5}'

# Stats
curl http://localhost:8000/stats

# Rebuild (with auth)
curl -X POST http://localhost:8000/rebuild \
  -H "X-API-Key: your-secret-key"
```

## Common Workflows

### Adding New Knowledge

1. Ingest content: `flightskb ingest --file article.pdf`
2. Review in `knowledge/inbox/`
3. Edit frontmatter and move to appropriate category
4. Rebuild index: `flightskb rebuild`
5. Verify with query: `flightskb query "your topic"`

### Updating Existing Content

1. Edit the markdown file directly
2. Update the `updated` date in frontmatter
3. Rebuild index: `flightskb rebuild`

### Quality Check

1. Run stats: `flightskb stats`
2. Check for low-confidence items
3. Run evaluation: `flightskb eval`
4. Address any missed queries

## Troubleshooting

### "Index not found"
Run `flightskb rebuild` to create the initial index.

### "Invalid frontmatter"
Check YAML syntax in the document. Common issues:
- Missing required fields (kb_id, type, title, etc.)
- Invalid date format (use YYYY-MM-DD)
- Unclosed quotes in strings

### "Duplicate kb_id"
Each document must have a unique `kb_id`. Check for duplicates:
```bash
grep -r "^kb_id:" knowledge/ | sort | uniq -d
```

### Slow queries
- Reduce `k` parameter
- Add metadata filters to narrow scope
- Consider upgrading embedding model
