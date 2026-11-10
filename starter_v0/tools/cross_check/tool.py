from __future__ import annotations

import re
from typing import Any

from tools._shared import err


def cross_check(source_a: str = "", source_b: str = "") -> dict[str, Any]:
    try:
        a_text = (source_a or "").strip()
        b_text = (source_b or "").strip()

        if not a_text or not b_text:
            return {
                "tool": "cross_check",
                "error": "ValueError",
                "message": "Both source_a and source_b are required for cross-checking",
            }

        stop_words = {"the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of", "with", "is", "la", "va", "cua", "cac", "nhung", "trong", "co"}
        words_a = set(w for w in re.findall(r"\b\w+\b", a_text.lower()) if len(w) > 2 and w not in stop_words)
        words_b = set(w for w in re.findall(r"\b\w+\b", b_text.lower()) if len(w) > 2 and w not in stop_words)

        common = sorted(words_a & words_b)
        union = words_a | words_b
        similarity = round(len(common) / len(union), 4) if union else 0.0

        verdict = "high_alignment" if similarity >= 0.4 else ("moderate_alignment" if similarity >= 0.15 else "low_alignment")

        return {
            "tool": "cross_check",
            "verdict": verdict,
            "jaccard_similarity": similarity,
            "shared_keywords": common,
            "unique_to_a_count": len(words_a - words_b),
            "unique_to_b_count": len(words_b - words_a),
        }
    except Exception as exc:
        return err("cross_check", exc)
