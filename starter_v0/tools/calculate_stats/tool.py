from __future__ import annotations

from typing import Any

from tools._shared import err


def calculate_stats(numbers: list[float] | None = None, operation: str = "summary") -> dict[str, Any]:
    try:
        if numbers is None or not isinstance(numbers, list) or len(numbers) == 0:
            return {
                "tool": "calculate_stats",
                "error": "ValueError",
                "message": "numbers must be a non-empty list of numeric values",
                "count": 0,
            }

        cleaned = [float(x) for x in numbers]
        n = len(cleaned)
        total = sum(cleaned)
        avg = total / n
        minimum = min(cleaned)
        maximum = max(cleaned)

        if operation == "average":
            return {"tool": "calculate_stats", "operation": "average", "result": avg, "count": n}
        elif operation == "sum":
            return {"tool": "calculate_stats", "operation": "sum", "result": total, "count": n}
        elif operation == "growth_rate":
            if n < 2:
                return {
                    "tool": "calculate_stats",
                    "error": "ValueError",
                    "message": "growth_rate requires at least 2 numbers (initial, final)",
                }
            initial, final = cleaned[0], cleaned[-1]
            if initial == 0:
                growth = float("inf") if final > 0 else float("-inf")
            else:
                growth = ((final - initial) / abs(initial)) * 100.0
            return {
                "tool": "calculate_stats",
                "operation": "growth_rate",
                "initial": initial,
                "final": final,
                "result": round(growth, 2),
                "growth_percentage": f"{round(growth, 2)}%",
            }
        else:  # summary
            return {
                "tool": "calculate_stats",
                "operation": "summary",
                "count": n,
                "sum": total,
                "average": avg,
                "min": minimum,
                "max": maximum,
            }
    except Exception as exc:
        return err("calculate_stats", exc)
