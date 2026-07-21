"""Injury protocol cards — region-level guidance for Today when pain is active.

Deterministic coaching copy + alternatives from PAIN_SWAPS. Sharp joint pain
always stops the set; these cards steer load and exercise choice, not diagnosis.
"""

from __future__ import annotations

from typing import Any

from app.coaching.swaps import PAIN_SWAPS, normalize_region, swaps_for_regions

REGION_LABELS: dict[str, str] = {
    "knee": "Knee",
    "ankle": "Ankle",
    "shoulder": "Shoulder",
    "elbow": "Elbow",
    "low back": "Low back",
    "back": "Back",
    "wrist": "Wrist",
    "hip": "Hip",
}

# Short, actionable steps per region (one job: keep training without aggravating).
_PROTOCOL_STEPS: dict[str, list[str]] = {
    "knee": [
        "Skip deep loaded knee flexion if it pinches — box squat or leg press range you own.",
        "Cut working sets ~30% and leave 2+ RIR on anything that loads the knee.",
        "Stop immediately on sharp joint pain (not normal muscle burn).",
        "Prefer hinge / posterior-chain swaps listed below.",
    ],
    "ankle": [
        "Keep the foot flat and stable — avoid aggressive dorsiflexion under load.",
        "Trim calf and deep squat volume; use machine or seated options.",
        "Stop on sharp joint pain; dull stiffness can stay light and controlled.",
        "Swap to leg press / hip hinge patterns that don't force the ankle.",
    ],
    "shoulder": [
        "Avoid end-range overhead and wide-grip pressing if it catches.",
        "Pull more than you push today; keep elbows closer on presses.",
        "Stop on sharp joint pain or radiating symptoms.",
        "Use neutral-grip and supported-row swaps below.",
    ],
    "elbow": [
        "Reduce grip-heavy or locked-elbow isolation; soft elbows on presses/rows.",
        "Drop volume on curls/extensions; keep compounds lighter.",
        "Stop on sharp joint pain at the elbow crease or outer elbow.",
        "Prefer dumbbell / neutral-grip alternatives listed below.",
    ],
    "low back": [
        "Brace hard, shorten range, and skip max-effort hinges if the spine complains.",
        "Prefer supported rows, goblet patterns, and hip thrusts over axial load.",
        "Stop on sharp lumbar pain or pain that travels into a leg.",
        "Use the swaps below and keep intensity to technique / blood-flow.",
    ],
    "back": [
        "Reduce axial loading; keep the torso braced and ranges honest.",
        "Favor machines and chest-supported work over free-bar maxes.",
        "Stop on sharp spinal pain — not ordinary muscle fatigue.",
        "Apply the alternatives below for today's slots.",
    ],
    "wrist": [
        "Use neutral grips and floor presses; avoid extreme extension under load.",
        "Wrap or switch to dumbbells if the bar angle aggravates.",
        "Stop on sharp wrist joint pain.",
        "Pick neutral-grip swaps listed below.",
    ],
    "hip": [
        "Avoid end-range pinches in deep flexion or aggressive adducted positions.",
        "Shorten squat/lunge depth; keep hips stacked and controlled.",
        "Stop on sharp joint pain in the front or side of the hip.",
        "Use leg press / upper-body bias swaps below when needed.",
    ],
}

_GENERIC_STEPS = [
    "Reduce load and volume on anything that aggravates the region.",
    "Prefer the listed alternatives over pushing through the planned lift.",
    "Stop immediately on sharp joint pain — muscle burn is fine; joint pain is not.",
    "Keep moving with blood-flow work if you skip a primary.",
]


def regions_from_profile_injuries(injuries: list | None) -> list[str]:
    """Extract display/raw region strings from profile.injuries entries."""
    out: list[str] = []
    for item in injuries or []:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
        elif isinstance(item, dict):
            region = item.get("region") or item.get("area") or item.get("name")
            if region:
                out.append(str(region).strip())
    return out


def merge_pain_regions(*sources: list[str]) -> list[str]:
    """Dedupe by normalized key; keep a stable display order."""
    seen: dict[str, str] = {}
    for src in sources:
        for raw in src or []:
            key = normalize_region(raw) or raw.lower().strip()
            if not key:
                continue
            if key not in seen:
                seen[key] = REGION_LABELS.get(key, raw.strip().title() if raw else key)
    # Prefer known protocol regions first, then any unknowns
    known = [k for k in PAIN_SWAPS if k in seen]
    unknown = [k for k in seen if k not in PAIN_SWAPS]
    ordered = known + sorted(unknown)
    return [seen[k] for k in ordered]


def build_injury_protocols(
    regions: list[str],
    *,
    intensity_note: str | None = None,
    alt_limit: int = 4,
) -> list[dict[str, Any]]:
    """Build Today cards: one protocol per normalized region we can coach."""
    alts = swaps_for_regions(regions, limit=alt_limit)
    cards: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in regions:
        key = normalize_region(raw)
        if not key or key in seen:
            continue
        seen.add(key)
        cards.append({
            "region": REGION_LABELS.get(key, key.title()),
            "region_key": key,
            "steps": list(_PROTOCOL_STEPS.get(key, _GENERIC_STEPS)),
            "alternatives": list(alts.get(key, PAIN_SWAPS.get(key, [])[:alt_limit])),
            "volume_hint": intensity_note
            or "Pain regions: reduce load, use swaps, stop if sharp pain.",
        })
    return cards


def quick_region_options() -> list[dict[str, str]]:
    """UI chips for logging pain without opening chat."""
    return [{"key": k, "label": REGION_LABELS.get(k, k.title())} for k in PAIN_SWAPS]
