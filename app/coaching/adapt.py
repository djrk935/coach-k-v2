"""Pre-session readiness → volume/intensity modulation for today's plan."""

from __future__ import annotations

from typing import Any


def readiness_score_from_entry(entry: dict | None) -> tuple[int | None, str]:
    """Derive a 0-100 score + status from subjective and/or HealthKit fields."""
    if not entry:
        return None, "unknown"

    if isinstance(entry.get("readiness_score"), (int, float)):
        score = int(entry["readiness_score"])
        return score, entry.get("readiness_status") or _status(score)

    parts: list[float] = []
    sleep = entry.get("sleep_h")
    if isinstance(sleep, (int, float)):
        parts.append(max(0.0, min(1.0, (float(sleep) - 4) / 4)) * 100)
    for key, invert in (("soreness_0_10", True), ("stress_0_10", True), ("motivation_0_10", False)):
        v = entry.get(key)
        if isinstance(v, (int, float)):
            n = float(v) / 10.0
            parts.append((1 - n) * 100 if invert else n * 100)
    if not parts:
        return None, "unknown"
    score = int(round(sum(parts) / len(parts)))
    return score, _status(score)


def _status(score: int) -> str:
    if score >= 80:
        return "primed"
    if score >= 65:
        return "ready"
    if score >= 50:
        return "moderate"
    return "compromised"


def adaptation_for(
    readiness_entry: dict | None,
    load: dict | None,
    pain_regions: list[str] | None = None,
) -> dict[str, Any]:
    """Return today's coaching adaptation knobs.

    volume_scale: multiply working sets (0.5–1.0)
    intensity_note: human cue for load selection
    soft_day: bool — treat as recovery-biased session
    reasons: list of strings the UI/coach can show
    """
    score, status = readiness_score_from_entry(readiness_entry)
    reasons: list[str] = []
    volume_scale = 1.0
    soft_day = False
    intensity_note = "Hit prescribed intensities; leave 1–2 RIR on accessories."
    positive_reason = ""

    acwr = (load or {}).get("acwr")
    if isinstance(acwr, (int, float)) and acwr > 1.5:
        soft_day = True
        volume_scale = min(volume_scale, 0.6)
        reasons.append(f"ACWR spiked ({acwr}) — backing off volume.")
        intensity_note = "Cap primary lifts ~5–10% under plan; stop at RPE 7."
    elif isinstance(acwr, (int, float)) and acwr > 1.3:
        volume_scale = min(volume_scale, 0.85)
        reasons.append(f"ACWR elevated ({acwr}) — trimming accessory volume.")

    if status == "compromised":
        soft_day = True
        volume_scale = min(volume_scale, 0.55)
        reasons.append("Readiness compromised — recovery-biased session.")
        intensity_note = "Cut intensity; technique and blood flow only if joints complain."
    elif status == "moderate":
        volume_scale = min(volume_scale, 0.8)
        reasons.append("Readiness moderate — keep primaries, shorten accessories.")
        intensity_note = "Hold loads; stop a rep earlier than usual on accessories."
    elif status == "primed":
        positive_reason = "Readiness primed — green light for planned intensities."
        intensity_note = "Earn the top sets. Still leave 1 RIR on isolation work."
    elif status == "ready":
        positive_reason = "Readiness solid — run the plan as written."
    elif score is None:
        reasons.append("No readiness logged yet — check in before you train.")

    if pain_regions:
        soft_day = True
        volume_scale = min(volume_scale, 0.7)
        # Lead with the operative reason so copy never reads "primed" + "soft day".
        reasons.insert(
            0,
            "Easing off for " + ", ".join(pain_regions) + " — lower load, prefer swaps.",
        )
        intensity_note = "Flagged pain: reduce load, use swaps, stop on sharp pain."

    # Only show the green-light line when we're actually running the plan hot.
    if positive_reason and not soft_day:
        reasons.insert(0, positive_reason)

    return {
        "score": score,
        "status": status,
        "volume_scale": round(volume_scale, 2),
        "soft_day": soft_day,
        "intensity_note": intensity_note,
        "reasons": reasons,
        "needs_checkin": score is None,
    }


def apply_volume_scale(exercises: list[dict], scale: float) -> list[dict]:
    """Scale working-set counts; keep at least 1 set; mark adapted."""
    if scale >= 0.99:
        return exercises
    out = []
    for ex in exercises:
        row = dict(ex)
        sets = int(ex.get("sets") or 1)
        set_type = (ex.get("set_type") or "straight").lower()
        if set_type == "warmup":
            out.append(row)
            continue
        new_sets = max(1, round(sets * scale))
        if new_sets != sets:
            row["sets"] = new_sets
            row["adapted"] = True
            note = row.get("notes") or ""
            tag = f"volume adapted ×{scale}"
            row["notes"] = f"{note} · {tag}".strip(" ·") if note else tag
        out.append(row)
    return out
