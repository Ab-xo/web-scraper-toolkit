"""
Property-based and unit tests for ai_query_engine.run_query().

Feature: ai-query-engine, Property 3: AI-powered results are a subset of the document
Feature: ai-query-engine, Property 4: Missing API key always produces fallback response
Feature: ai-query-engine, Property 5: Non-empty results always include a summary
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from hypothesis import given, settings as h_settings, strategies as st
from bs4 import BeautifulSoup

from app.services.ai_query_engine import run_query, _extract_structured

# ── helpers ───────────────────────────────────────────────────────────────────

def simple_html(n_headings=3, n_paragraphs=2) -> str:
    headings = "".join(f"<h2>Heading {i}</h2>" for i in range(n_headings))
    paragraphs = "".join(f"<p>Paragraph {i}</p>" for i in range(n_paragraphs))
    return f"<html><body>{headings}{paragraphs}</body></html>"


def mock_plan(container="h2", fields=None, follow_url=None, summary="Found items."):
    """Return a dict matching the new ask_groq return format."""
    return {
        "container":  container,
        "fields":     fields or {"text": "self"},
        "follow_url": follow_url,
        "summary":    summary,
    }


# ── Property 4: missing API key → always fallback ────────────────────────────
# Feature: ai-query-engine, Property 4: Missing API key always produces fallback response
# Validates: Requirements 3.4, 1.4

@given(
    intent=st.text(min_size=1, max_size=100,
                   alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Zs"))),
    n=st.integers(min_value=1, max_value=5),
)
@h_settings(max_examples=100)
def test_no_api_key_always_fallback(intent, n):
    html = simple_html(n_headings=n)
    with patch("app.services.ai_query_engine.settings") as mock_settings:
        mock_settings.groq_api_key = ""
        result = asyncio.run(run_query(html, intent.strip() or "headings"))
    assert result["fallback"] is True
    assert result["ai_powered"] is False


# ── Property 3: AI results are a subset of the document ──────────────────────
# Feature: ai-query-engine, Property 3: AI-powered results are a subset of the document
# Validates: Requirements 1.1, 1.2

@given(n=st.integers(min_value=1, max_value=10))
@h_settings(max_examples=100)
def test_results_are_subset_of_document(n):
    html = simple_html(n_headings=n, n_paragraphs=n)

    with patch("app.services.ai_query_engine.settings") as mock_settings, \
         patch("app.services.ai_query_engine.ask_groq",
               new=AsyncMock(return_value=mock_plan("h2", {"text": "self"}))):
        mock_settings.groq_api_key = "test-key"
        mock_settings.ai_model = "test"
        mock_settings.ai_base_url = "http://test"
        result = asyncio.run(run_query(html, "find headings"))

    soup = BeautifulSoup(html, "lxml")
    all_text = {t.get_text(strip=True) for t in soup.find_all()}
    for item in result["results"]:
        # Each formatted result line "Field: value" — check value is in doc
        for line in item.split("\n"):
            if ": " in line:
                val = line.split(": ", 1)[1]
                assert val in all_text or val == "", f"Value '{val}' not found in document"


# ── Property 5: non-empty results always have a summary ──────────────────────
# Feature: ai-query-engine, Property 5: Non-empty results always include a summary
# Validates: Requirements 2.1

@given(n=st.integers(min_value=1, max_value=10))
@h_settings(max_examples=100)
def test_nonempty_results_have_summary(n):
    html = simple_html(n_headings=n)

    with patch("app.services.ai_query_engine.settings") as mock_settings, \
         patch("app.services.ai_query_engine.ask_groq",
               new=AsyncMock(return_value=mock_plan("h2", {"text": "self"},
                                                     summary="Found headings."))):
        mock_settings.groq_api_key = "test-key"
        mock_settings.ai_model = "test"
        mock_settings.ai_base_url = "http://test"
        result = asyncio.run(run_query(html, "headings"))

    if result["count"] > 0 and result["ai_powered"]:
        assert result["summary"], "summary must be non-empty when results exist"
        assert isinstance(result["summary"], str)


# ── Unit: fallback on empty container ────────────────────────────────────────

@pytest.mark.asyncio
async def test_fallback_on_empty_container():
    html = simple_html()
    with patch("app.services.ai_query_engine.settings") as mock_settings, \
         patch("app.services.ai_query_engine.ask_groq",
               new=AsyncMock(return_value=mock_plan("", summary="nothing"))):
        mock_settings.groq_api_key = "key"
        mock_settings.ai_model = "m"
        mock_settings.ai_base_url = "http://x"
        result = await run_query(html, "test")
    assert result["fallback"] is True


# ── Unit: fallback on groq exception ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_fallback_on_groq_exception():
    html = simple_html()
    with patch("app.services.ai_query_engine.settings") as mock_settings, \
         patch("app.services.ai_query_engine.ask_groq",
               new=AsyncMock(side_effect=Exception("network error"))):
        mock_settings.groq_api_key = "key"
        mock_settings.ai_model = "m"
        mock_settings.ai_base_url = "http://x"
        result = await run_query(html, "headings")
    assert result["fallback"] is True
    assert result["ai_powered"] is False


# ── Unit: zero-results edge case ─────────────────────────────────────────────

def test_zero_result_fallback_has_summary():
    html = "<html><body><p>hello</p></body></html>"
    with patch("app.services.ai_query_engine.settings") as mock_settings, \
         patch("app.services.ai_query_engine.ask_groq",
               new=AsyncMock(return_value=mock_plan("h99", summary="Nothing found."))):
        mock_settings.groq_api_key = "key"
        mock_settings.ai_model = "m"
        mock_settings.ai_base_url = "http://x"
        result = asyncio.run(run_query(html, "find h99"))
    assert result["fallback"] is True
    assert result["summary"] is not None
