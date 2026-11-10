from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any

from tools._shared import ROOT, err


NOTES_DIR = ROOT / "artifacts" / "notes"


def save_note(title: str = "", content: str = "", tags: list[str] | None = None) -> dict[str, Any]:
    try:
        if not title.strip() and not content.strip():
            return {
                "tool": "save_note",
                "error": "ValueError",
                "message": "Title and content cannot both be empty",
            }

        NOTES_DIR.mkdir(parents=True, exist_ok=True)
        safe_title = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in (title or "untitled")).strip("_")[:50]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{safe_title}.md"
        file_path = NOTES_DIR / filename

        tags_str = ", ".join(tags) if tags else "none"
        body = f"# {title or 'Research Note'}\n\n- Created: {datetime.now().isoformat()}\n- Tags: {tags_str}\n\n## Content\n\n{content}\n"
        file_path.write_text(body, encoding="utf-8")

        return {
            "tool": "save_note",
            "status": "saved",
            "filename": filename,
            "path": str(file_path),
            "title": title,
            "tags": tags or [],
            "bytes_written": len(body.encode("utf-8")),
        }
    except Exception as exc:
        return err("save_note", exc)
