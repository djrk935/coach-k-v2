"""Travel / limited-equipment day generator."""

from __future__ import annotations

from typing import Any

TRAVEL_DAYS: dict[str, dict[str, Any]] = {
    "hotel": {
        "day_label": "Travel Day — Hotel / Minimal",
        "focus": "Full-body density with bodyweight + backpack load options",
        "exercises": [
            {"exercise": "Push Up", "sets": 4, "reps": "8-15", "intensity": "2 RIR",
             "set_type": "straight", "notes": "Elevate feet if too easy; backpack for load"},
            {"exercise": "Bulgarian Split Squat", "sets": 3, "reps": "8-12/leg", "intensity": "2 RIR",
             "set_type": "straight", "notes": "Rear foot on bed/chair"},
            {"exercise": "Inverted Row", "sets": 3, "reps": "8-12", "intensity": "2 RIR",
             "set_type": "straight", "notes": "Table edge or towel door-row if needed"},
            {"exercise": "Hip Thrust", "sets": 3, "reps": "12-15", "intensity": "1 RIR",
             "set_type": "straight", "notes": "Shoulders on bed edge; pack on hips"},
            {"exercise": "Plank", "sets": 3, "reps": "30-45s", "intensity": "braced",
             "set_type": "finisher", "notes": "Ribs down, glutes on"},
        ],
    },
    "dumbbells": {
        "day_label": "Travel Day — DBs Only",
        "focus": "Strength stimulus with a pair of dumbbells",
        "exercises": [
            {"exercise": "Goblet Squat", "sets": 4, "reps": "8-12", "intensity": "2 RIR",
             "set_type": "straight", "notes": None},
            {"exercise": "Romanian Deadlift", "sets": 3, "reps": "8-12", "intensity": "2 RIR",
             "set_type": "straight", "notes": "DBs or suitcase style"},
            {"exercise": "Dumbbell Shoulder Press", "sets": 3, "reps": "8-12", "intensity": "2 RIR",
             "set_type": "straight", "notes": None},
            {"exercise": "Dumbbell Row", "sets": 3, "reps": "10-12/arm", "intensity": "1 RIR",
             "set_type": "straight", "notes": None},
            {"exercise": "Push Up", "sets": 3, "reps": "AMRAP", "intensity": "1 RIR",
             "set_type": "finisher", "notes": None},
        ],
    },
    "band": {
        "day_label": "Travel Day — Bands",
        "focus": "Joint-friendly full body with resistance bands",
        "exercises": [
            {"exercise": "Squat", "sets": 4, "reps": "12-15", "intensity": "2 RIR",
             "set_type": "straight", "notes": "Band under feet / around shoulders"},
            {"exercise": "Push Up", "sets": 3, "reps": "10-15", "intensity": "2 RIR",
             "set_type": "straight", "notes": "Band across back for overload if available"},
            {"exercise": "Face Pull", "sets": 3, "reps": "15-20", "intensity": "1 RIR",
             "set_type": "straight", "notes": "Anchor at face height"},
            {"exercise": "Romanian Deadlift", "sets": 3, "reps": "12-15", "intensity": "2 RIR",
             "set_type": "straight", "notes": "Stand on band, hinge"},
            {"exercise": "Pallof Press", "sets": 3, "reps": "10/side", "intensity": "braced",
             "set_type": "finisher", "notes": "Anti-rotation; own the pause"},
        ],
    },
}


def travel_day(mode: str = "hotel") -> dict[str, Any]:
    key = mode.lower().strip()
    if key not in TRAVEL_DAYS:
        key = "hotel"
    day = TRAVEL_DAYS[key]
    return {
        "mode": key,
        "active": True,
        "program_id": f"travel:{key}",
        "program_name": "Travel / Limited Equipment",
        "day_index": 0,
        "cycle_count": 0,
        "day_label": day["day_label"],
        "focus": day["focus"],
        "exercises": [
            {
                **ex,
                "tempo": None,
                "rest_s": 90,
                "superset_group": None,
                "suggested_weight_lbs": None,
                "logged_sets": [],
                "image_urls": [],
                "form_cue": None,
                "swap_suggestion": None,
            }
            for ex in day["exercises"]
        ],
        "travel": True,
    }
