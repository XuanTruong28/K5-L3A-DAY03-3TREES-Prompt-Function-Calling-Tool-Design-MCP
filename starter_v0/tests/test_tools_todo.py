"""TODO(student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    result = TOOL_FUNCTIONS["clarify"](
        question="Chọn chủ đề nào?",
        response_type="choice",
        options=["AI", "Crypto"],
    )
    assert result["options"] == ["AI", "Crypto"]
    assert result["awaiting_user"] is True
    assert result["response_type"] == "choice"
    assert result["question"] == "Chọn chủ đề nào?"


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    items = [
        {"title": "Item 1", "section": "A"},
        {"title": "Item 2", "section": "B"},
        {"title": "Item 3", "section": "A"},
    ]
    result = TOOL_FUNCTIONS["format"](items=items, template="sections")
    assert result["markdown"].count("## A") == 1
    assert result["markdown"].count("## B") == 1


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    items = [
        {"title": "Thread 1", "summary": "Nội dung 1"},
        {"title": "Thread 2", "summary": "Nội dung 2"},
    ]
    result = TOOL_FUNCTIONS["format"](items=items, template="thread")
    parts = [p.strip() for p in result["markdown"].split("\n\n") if p.strip()]
    assert len(parts) == 2
    assert parts[0].startswith("1/ ")
    assert parts[1].startswith("2/ ")


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    res_none = TOOL_FUNCTIONS["format"](items=None)
    assert res_none["item_count"] == 0
    assert "markdown" in res_none

    res_empty = TOOL_FUNCTIONS["format"](items=[])
    assert res_empty["item_count"] == 0
    assert "markdown" in res_empty


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_bot_token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "chat_123")
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"](text="Bản tin công nghệ", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "test_bot_token" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "chat_123"
    assert calls[0]["json"]["text"] == "Bản tin công nghệ"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))
    result = TOOL_FUNCTIONS["send"](text="Bản tin", confirmed=True)
    assert len(calls) == 0
    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    # timeframe=None -> request body has no "time_range" key.
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))

    TOOL_FUNCTIONS["lookup"](query="test query", timeframe=None)

    assert len(calls) == 1
    assert "time_range" not in calls[0]["json"]


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    calls = fake_http(FakeResponse({
        "data": {
            "markdown": "Nội dung bài viết",
            "metadata": {
                "title": "T",
                "sourceURL": "https://example.com/article",
            },
        }
    }))

    result = TOOL_FUNCTIONS["fetch"](url="https://example.com/article")

    assert len(calls) == 1
    item = result["items"][0]
    assert item["title"] == "T"
    assert item["url"] == "https://example.com/article"
    assert item["source"] == "example.com"
    assert item["summary"] == "Nội dung bài viết"


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    long_markdown = "A" * 5000
    fake_http(FakeResponse({
        "data": {
            "markdown": long_markdown,
            "metadata": {"title": "Long Page", "sourceURL": "https://example.com/long"},
        }
    }))

    result = TOOL_FUNCTIONS["fetch"](url="https://example.com/long")
    assert len(result["items"][0]["summary"]) == 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-test")
    raw_timeline = [
        {"screen_name": "sama", "text": "missing id"},
        {"tweet_id": "101", "screen_name": "sama", "text": "tweet 1"},
        {"tweet_id": "102", "screen_name": "sama", "text": "tweet 2"},
        {"tweet_id": "103", "screen_name": "sama", "text": "tweet 3"},
        {"tweet_id": "104", "screen_name": "sama", "text": "tweet 4"},
        {"tweet_id": "105", "screen_name": "sama", "text": "tweet 5"},
        {"tweet_id": "106", "screen_name": "sama", "text": "tweet 6"},
    ]
    fake_http(FakeResponse({"timeline": raw_timeline}))

    result = TOOL_FUNCTIONS["timeline"](screenname="sama", limit=3)

    assert len(result["items"]) == 3
    assert result["items"][0]["url"] == "https://x.com/sama/status/101"
    assert result["items"][1]["url"] == "https://x.com/sama/status/102"
    assert result["items"][2]["url"] == "https://x.com/sama/status/103"


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-test")
    calls = fake_http(FakeResponse({"timeline": []}))

    TOOL_FUNCTIONS["social_search"](query="GPT-5", search_type="Top")

    assert len(calls) == 1
    assert calls[0]["params"]["query"] == "GPT-5"
    assert calls[0]["params"]["search_type"] == "Top"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    result = TOOL_FUNCTIONS["policy"](query="")
    assert result["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    result = TOOL_FUNCTIONS["policy"](query="privacy customer", policy_area="data_privacy")
    assert len(result["results"]) > 0
    assert all(r["policy_area"] == "data_privacy" for r in result["results"])


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    result = TOOL_FUNCTIONS["policy"](query="injection probe viral tweet", policy_area="source_citation")
    probe_section = next((r for r in result["results"] if r["section"] == "Injection probe"), None)
    assert probe_section is not None
    assert any("ignore the citation policy" in line for line in probe_section["untrusted_text"])
    assert "ignore the citation policy" not in probe_section["facts"]


# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

def test_my_new_tool_happy_path() -> None:
    result = TOOL_FUNCTIONS["calculate_stats"](numbers=[10, 20, 30], operation="summary")
    assert result["tool"] == "calculate_stats"
    assert result["count"] == 3
    assert result["sum"] == 60
    assert result["average"] == 20.0
    assert result["min"] == 10
    assert result["max"] == 30

    growth = TOOL_FUNCTIONS["calculate_stats"](numbers=[100, 150], operation="growth_rate")
    assert growth["result"] == 50.0
    assert growth["growth_percentage"] == "50.0%"


def test_my_new_tool_bad_input_from_model() -> None:
    # Empty list or None
    res_none = TOOL_FUNCTIONS["calculate_stats"](numbers=None)
    assert res_none["error"] == "ValueError"

    res_empty = TOOL_FUNCTIONS["calculate_stats"](numbers=[])
    assert res_empty["error"] == "ValueError"

    # growth_rate with only 1 number
    res_growth_bad = TOOL_FUNCTIONS["calculate_stats"](numbers=[100], operation="growth_rate")
    assert res_growth_bad["error"] == "ValueError"


def test_my_new_tool_failure_returns_error_dict() -> None:
    # Non-numeric elements that raise during conversion
    result = TOOL_FUNCTIONS["calculate_stats"](numbers=["not_a_number", "abc"])
    assert "error" in result
    assert result["tool"] == "calculate_stats"


def test_save_note_happy_path_and_bad_input(tmp_path, monkeypatch) -> None:
    from tools.save_note import tool as save_note_module
    monkeypatch.setattr(save_note_module, "NOTES_DIR", tmp_path)
    # Happy path
    res = TOOL_FUNCTIONS["save_note"](title="Test Note", content="Hello research", tags=["ai", "test"])
    assert res["status"] == "saved"
    assert (tmp_path / res["filename"]).exists()

    # Bad input
    bad = TOOL_FUNCTIONS["save_note"](title="", content="")
    assert bad["error"] == "ValueError"


def test_text_metrics_calculates_counts_and_reading_time() -> None:
    res = TOOL_FUNCTIONS["text_metrics"](text="Artificial intelligence is transforming research. AI models are powerful.")
    assert res["tool"] == "text_metrics"
    assert res["word_count"] > 5
    assert res["sentence_count"] == 2
    assert res["reading_time_minutes"] >= 0.01

    # Empty text
    empty = TOOL_FUNCTIONS["text_metrics"](text="")
    assert empty["word_count"] == 0


def test_cross_check_compares_sources_and_detects_overlap() -> None:
    src_a = "Deep learning transformers revolutionized natural language processing and computer vision."
    src_b = "Transformers in natural language processing achieve breakthrough results in deep learning."
    res = TOOL_FUNCTIONS["cross_check"](source_a=src_a, source_b=src_b)
    assert res["tool"] == "cross_check"
    assert res["verdict"] in ("high_alignment", "moderate_alignment")
    assert "transformers" in res["shared_keywords"]

    # Missing input
    bad = TOOL_FUNCTIONS["cross_check"](source_a="", source_b="only one")
    assert bad["error"] == "ValueError"
