"""Double-progression style load bumps from recent logged sets."""

from __future__ import annotations

import re
from typing import Any


def _parse_rep_target(reps: str) -> int | None:
    if not reps:
        return None
    nums = [int(x) for x in re.findall(r"\d+", reps)]
    return max(nums) if nums else None


def progression_delta_lbs(
    exercise: str,
    intensity: str,
    logged_sets: list[dict],
    target_sets: int,
    target_reps: str,
) -> dict[str, Any] | None:
    """If the athlete cleared top-of-range reps on all working sets, bump load.

    Returns {delta_lbs, reason} or None if hold.
    """
    if not logged_sets:
        return None
    top = _parse_rep_target(target_reps)
    if not top:
        return None
    complete = [s for s in logged_sets if s.get("reps") is not None]
    if len(complete) < max(1, target_sets):
        return None
    # Use the last N sets matching target_sets
    recent = complete[-target_sets:]
    if any((s.get("reps") or 0) < top for s in recent):
        return None
    # RIR gate: if they reported high RIR leftover, still bump; if RIR 0 and barely made it, smaller bump
    rirs = [s["rir"] for s in recent if isinstance(s.get("rir"), (int, float))]
    avg_rir = sum(rirs) / len(rirs) if rirs else 2.0

    name = exercise.lower()
    compound = any(k in name for k in ("squat", "deadlift", "bench", "press", "row", "clean"))
    if avg_rir <= 0.5:
        delta = 2.5 if not compound else 5
        reason = f"Hit {top}s across sets near failure — small bump (+{delta} lbs)."
    else:
        delta = 5 if not compound else 10
        reason = f"Cleared {top}s with room — progress +{delta} lbs next time."

    return {
        "delta_lbs": delta,
        "reason": reason,
        "update_hint": "%" in (intensity or ""),
    }


def apply_progression_to_suggestion(
    base: float | None, progression: dict | None
) -> float | None:
    if base is None or not progression:
        return base
    return round((base + progression["delta_lbs"]) / 5) * 5
