"""Shared pytest fixtures for Flights KB tests."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def knowledge_dir(temp_dir):
    """Create a temporary knowledge directory."""
    kdir = temp_dir / "knowledge"
    kdir.mkdir()
    # Create subdirectories
    for subdir in ["airlines", "hacks", "inbox"]:
        (kdir / subdir).mkdir()
    return kdir


@pytest.fixture
def index_dir(temp_dir):
    """Create a temporary index directory."""
    idir = temp_dir / "index"
    idir.mkdir()
    (idir / "manifests").mkdir()
    return idir


@pytest.fixture
def sample_document_content():
    """Sample document markdown with frontmatter."""
    return '''---
kb_id: test-doc-001
type: hack
title: "Test Document"
created: 2024-01-01
updated: 2024-01-01
status: draft
source:
  kind: internal
  name: Test Author
  url: null
  retrieved: null
confidence: medium
---

## First Section

**Claim type:** fact
**Applies to:** airline=BA
**Summary:** This is a test summary.

Some content here.

## Second Section

**Summary:** Another section.

More content.
'''


@pytest.fixture
def sample_document_file(knowledge_dir, sample_document_content):
    """Create a sample document file."""
    file_path = knowledge_dir / "hacks" / "test-doc.md"
    file_path.write_text(sample_document_content)
    return file_path
