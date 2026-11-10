from __future__ import annotations

import re
from typing import Any

from tools._shared import err


def text_metrics(text: str = "") -> dict[str, Any]:
    try:
        raw_text = (text or "").strip()
        if not raw_text:
            return {
                "tool": "text_metrics",
                "char_count": 0,
                "word_count": 0,
                "sentence_count": 0,
                "reading_time_minutes": 0.0,
                "top_words": [],
            }

        char_count = len(raw_text)
        words = re.findall(r"\b\w+\b", raw_text.lower())
        word_count = len(words)

        # Estimate sentences by punctuation
        sentences = [s for s in re.split(r"[.!?]+", raw_text) if s.strip()]
        sentence_count = len(sentences) or 1

        # Reading speed: ~200 words per minute
        reading_time = round(word_count / 200.0, 2)

        # Word frequency (excluding short stop words)
        stop_words = {"the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of", "with", "is", "la", "va", "cua", "cac", "nhung", "trong"}
        freq: dict[str, int] = {}
        for w in words:
            if len(w) > 2 and w not in stop_words:
                freq[w] = freq.get(w, 0) + 1

        top_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]
        top_words_list = [{"word": w, "count": c} for w, c in top_words]

        return {
            "tool": "text_metrics",
            "char_count": char_count,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "reading_time_minutes": reading_time,
            "top_words": top_words_list,
        }
    except Exception as exc:
        return err("text_metrics", exc)
