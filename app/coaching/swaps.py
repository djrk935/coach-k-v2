"""Pain-region exercise swaps + short form cues for common lifts."""

from __future__ import annotations

# region keyword → preferred alternatives (canonical names for media resolver)
PAIN_SWAPS: dict[str, list[str]] = {
    "knee": [
        "Leg Press", "Romanian Deadlift", "Seated Leg Curl", "Hip Thrust",
        "Box Squat", "Glute Bridge",
    ],
    "ankle": [
        "Leg Press", "Seated Leg Curl", "Hip Thrust", "Machine Hack Squat",
    ],
    "shoulder": [
        "Neutral Grip Pull Up", "Chest-Supported Row", "Lat Pulldown",
        "Push Up", "Dumbbell Floor Press", "Face Pull",
    ],
    "elbow": [
        "Dumbbell Row", "Chest-Supported Row", "Lat Pulldown",
        "Dumbbell Shoulder Press", "Push Up",
    ],
    "low back": [
        "Goblet Squat", "Leg Press", "Hip Thrust", "Chest-Supported Row",
        "Lat Pulldown", "Bulgarian Split Squat",
    ],
    "back": [
        "Goblet Squat", "Leg Press", "Hip Thrust", "Chest-Supported Row",
        "Lat Pulldown",
    ],
    "wrist": [
        "Neutral Grip Pull Up", "Dumbbell Row", "Push Up", "Dumbbell Floor Press",
    ],
    "hip": [
        "Leg Press", "Seated Leg Curl", "Chest-Supported Row", "Lat Pulldown",
        "Seated Calf Raise",
    ],
}

FORM_CUES: dict[str, str] = {
    "back squat": "Brace hard, knees track toes, sit between the hips — bar path vertical.",
    "front squat": "Elbows high, torso tall, sit between the heels.",
    "box squat": "Sit back to the box under control, explode up — don't rock.",
    "bench press": "Plant feet, pull shoulder blades together, bar to lower chest.",
    "incline bench press": "Slight arch OK; touch upper chest, lock out without shrugging.",
    "overhead press": "Ribs down, press slightly back to lockout over mid-foot.",
    "deadlift": "Bar over mid-foot, push the floor away, lock hips and knees together.",
    "romanian deadlift": "Soft knees, hinge until hamstrings stretch, bar close to legs.",
    "barbell row": "Hinge stable, pull to lower ribs, control the eccentric.",
    "weighted pull up": "Full hang → chest to bar; no kipping on strength work.",
    "pull up": "Full hang → chest to bar; own the negative.",
    "lat pulldown": "Lean slightly back, pull to collarbone, squeeze lats — don't yank.",
    "bulgarian split squat": "Tall torso, front shin mostly vertical, drive through mid-foot.",
    "power clean": "Explosive extension, elbows whip through fast — catch athletic.",
    "hip thrust": "Chin tucked, ribs down, pause at lockout with glutes — not lumbar.",
    "leg press": "Full foot contact, don't let low back round at the bottom.",
    "dumbbell shoulder press": "Wrists stacked, press up and slightly in, soft lockout.",
}


def normalize_region(region: str) -> str | None:
    r = region.lower().strip()
    aliases = {
        "knees": "knee", "patella": "knee", "quad": "knee",
        "ankles": "ankle",
        "shoulders": "shoulder", "rotator": "shoulder",
        "elbows": "elbow",
        "lower back": "low back", "lumbar": "low back", "lumbago": "low back",
        "wrists": "wrist",
        "hips": "hip", "groin": "hip",
    }
    if r in PAIN_SWAPS:
        return r
    return aliases.get(r)


def swaps_for_regions(regions: list[str], limit: int = 4) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for raw in regions:
        key = normalize_region(raw)
        if key and key in PAIN_SWAPS:
            out[key] = PAIN_SWAPS[key][:limit]
    return out


def suggest_swap(exercise: str, regions: list[str]) -> str | None:
    """Pick first swap that isn't the same exercise."""
    name = exercise.lower()
    for raw in regions:
        key = normalize_region(raw)
        if not key:
            continue
        for alt in PAIN_SWAPS.get(key, []):
            if alt.lower() != name:
                return alt
    return None


def form_cue_for(exercise: str) -> str | None:
    name = exercise.lower().strip()
    if name in FORM_CUES:
        return FORM_CUES[name]
    for key, cue in FORM_CUES.items():
        if key in name or name in key:
            return cue
    return None
