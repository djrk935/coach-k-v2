"""Auto warm-up ramps from a working-set target weight.

Classic strength practice: empty-ish → ~60% → ~75% → ~85–90% opener,
rounded to practical plate jumps (5 lb default, 2.5 when light).
"""

from __future__ import annotations

from typing import Any


_COMPOUND_HINTS = (
    "squat", "deadlift", "bench", "press", "row", "clean", "snatch",
    "front squat", "rdl", "romanian", "pull up", "pull-up", "chin",
)


def _is_compound(exercise: str) -> bool:
    name = exercise.lower()
    return any(h in name for h in _COMPOUND_HINTS)


def _round_load(lbs: float, increment: float = 5.0) -> float:
    if lbs <= 0:
        return 0.0
    return round(lbs / increment) * increment


def warmup_ramp(
    working_lbs: float | None,
    *,
    exercise: str = "",
    set_type: str = "straight",
    bar_lbs: float = 45.0,
) -> list[dict[str, Any]]:
    """Return warm-up prescriptions for a working set at `working_lbs`.

    Skips finishers, existing warmup rows, and lifts without a usable load.
    """
    st = (set_type or "straight").lower()
    if st in ("warmup", "finisher"):
        return []
    if working_lbs is None or working_lbs < 65:
        # Bodyweight / light accessories: movement priming only
        if _is_compound(exercise) and (working_lbs is None or working_lbs < 45):
            return [
                {"weight_lbs": None, "reps": 8, "pct": None, "label": "Bodyweight / empty pattern × 8"},
                {"weight_lbs": None, "reps": 5, "pct": None, "label": "Closer to working effort × 5"},
            ]
        return []

    w = float(working_lbs)
    # Lighter DBs / accessories: shorter ramp, 2.5 lb jumps when under 100
    increment = 2.5 if w < 100 else 5.0
    compound = _is_compound(exercise)

    if not compound and w < 120:
        steps = [(0.5, 8), (0.7, 5), (0.85, 3)]
    elif w < 135:
        steps = [(0.4, 8), (0.6, 5), (0.75, 3), (0.9, 1)]
    else:
        # Full compound ramp
        steps = [(0.4, 5), (0.6, 3), (0.75, 2), (0.85, 1)]

    out: list[dict[str, Any]] = []
    seen: set[float] = set()
    for pct, reps in steps:
        raw = max(bar_lbs if compound and w >= 95 else increment * 2, w * pct)
        load = _round_load(raw, increment)
        # Never meet or exceed working weight on a warm-up
        if load >= w:
            load = _round_load(w - increment, increment)
        if load <= 0 or load in seen:
            continue
        if load >= w:
            continue
        seen.add(load)
        out.append({
            "weight_lbs": load,
            "reps": reps,
            "pct": round(100 * load / w),
            "label": f"{load:g} × {reps} (~{round(100 * load / w)}%)",
        })

    # Ensure bar/empty opener exists for heavy barbell work
    if compound and w >= 135 and bar_lbs not in seen and bar_lbs < w:
        out.insert(0, {
            "weight_lbs": bar_lbs,
            "reps": 8,
            "pct": round(100 * bar_lbs / w),
            "label": f"{bar_lbs:g} × 8 (bar)",
        })
        # de-dupe if first ramp step ≈ bar
        cleaned: list[dict[str, Any]] = []
        seen2: set[float] = set()
        for step in out:
            wl = step["weight_lbs"]
            if wl in seen2:
                continue
            seen2.add(wl)
            cleaned.append(step)
        out = cleaned

    return out[:5]
