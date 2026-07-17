"""Match the coach's free-text exercise names to free-exercise-db entries.

"DB Overhead Press" → "Dumbbell Shoulder Press" etc. Three tiers:
1. Canonical map for the big lifts (exact, hand-verified).
2. Scored fuzzy match: query-coverage weighted, candidate add-ons penalized
   ("Car Deadlift", "Box Squat with Bands" must not beat plain lifts).
3. Similarity floor — a bad match renders as no image, never the wrong lift.
"""

import difflib
import json
import re
from functools import lru_cache
from pathlib import Path

MEDIA_DIR = Path(__file__).parent.parent.parent / "exercise_media"

# Gym shorthand → catalog vocabulary (applied to the query only)
_ALIASES = {
    "db": "dumbbell",
    "bb": "barbell",
    "ohp": "overhead press",
    "rdl": "romanian deadlift",
    "kb": "kettlebell",
    "chinup": "chin up",
    "pullup": "pull up",
}

# The staples, normalized query → exact catalog name (verified at import).
_CANONICAL = {
    "squat": "Barbell Squat",
    "back squat": "Barbell Squat",
    "barbell squat": "Barbell Squat",
    "front squat": "Front Barbell Squat",
    "deadlift": "Barbell Deadlift",
    "barbell deadlift": "Barbell Deadlift",
    "sumo deadlift": "Sumo Deadlift",
    "romanian deadlift": "Romanian Deadlift",
    "stiff leg deadlift": "Stiff-Legged Barbell Deadlift",
    "bench press": "Barbell Bench Press - Medium Grip",
    "barbell bench press": "Barbell Bench Press - Medium Grip",
    "incline bench press": "Barbell Incline Bench Press - Medium Grip",
    "close grip bench press": "Close-Grip Barbell Bench Press",
    "overhead press": "Barbell Shoulder Press",
    "overhead press barbell": "Barbell Shoulder Press",
    "barbell overhead press": "Barbell Shoulder Press",
    "military press": "Barbell Shoulder Press",
    "dumbbell overhead press": "Dumbbell Shoulder Press",
    "dumbbell shoulder press": "Dumbbell Shoulder Press",
    "standing calf raise": "Standing Calf Raises",
    "seated calf raise": "Seated Calf Raise",
    "hip thrust": "Barbell Hip Thrust",
    "barbell hip thrust": "Barbell Hip Thrust",
    "pull up": "Pullups",
    "weighted pull up": "Weighted Pull Ups",
    "chin up": "Chin-Up",
    "weighted chin up": "Chin-Up",
    "lat pulldown": "Wide-Grip Lat Pulldown",
    "barbell row": "Bent Over Barbell Row",
    "bent over row": "Bent Over Barbell Row",
    "pendlay row": "Bent Over Barbell Row",
    "chest supported row": "Dumbbell Incline Row",
    "bulgarian split squat": "Split Squat with Dumbbells",
    "hanging leg raise": "Hanging Leg Raise",
    "hip adduction": "Thigh Adductor",
    "leg press": "Leg Press",
    "leg extension": "Leg Extensions",
    "power clean": "Power Clean",
    "clean and jerk": "Clean and Jerk",
    "snatch": "Snatch",
}

# Candidate tokens that signal a specialty variant — heavily penalized when
# the athlete didn't ask for them.
_VARIANT_FLAGS = {
    "hack", "car", "box", "chair", "smith", "bands", "chains", "machine",
    "suspended", "sled", "zercher", "jefferson", "leverage", "axle",
    "deficit", "guillotine", "isometric", "one", "single",
    "rear", "reverse", "behind", "decline",
}

# Tempo/style modifiers that don't change which lift it is — dropped from query
_QUERY_NOISE = {"paused", "pause", "tempo", "competition", "comp", "touch", "go", "heavy", "light"}


def _norm(s: str) -> str:
    s = re.sub(r"\(.*?\)", " ", s.lower())          # drop parentheticals
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    words = [(_ALIASES.get(w, w)) for w in s.split() if w not in _QUERY_NOISE]
    return " ".join(words).strip()


@lru_cache(maxsize=1)
def _catalog() -> list[dict]:
    return json.loads((MEDIA_DIR / "exercises.json").read_text())


@lru_cache(maxsize=1)
def _by_name() -> dict[str, dict]:
    return {e["name"]: e for e in _catalog()}


@lru_cache(maxsize=512)
def resolve(name: str) -> dict | None:
    """Return the best catalog entry for an exercise name, or None."""
    q = _norm(name)
    if not q:
        return None

    # Tier 1: canonical staples
    if q in _CANONICAL:
        return _by_name().get(_CANONICAL[q])

    q_tokens = set(q.split())

    # Tier 2: scored fuzzy
    best, best_score = None, 0.0
    for ex in _catalog():
        c = _norm(ex["name"])
        c_tokens = set(c.split())
        if not (q_tokens & c_tokens):
            continue
        coverage = len(q_tokens & c_tokens) / len(q_tokens)       # query covered
        extras = c_tokens - q_tokens
        extra_pen = 0.08 * len(extras) + 0.25 * len(extras & _VARIANT_FLAGS)
        ratio = difflib.SequenceMatcher(None, q, c).ratio()
        score = 0.65 * coverage + 0.35 * ratio - extra_pen
        # Barbell-vs-dumbbell mixups are the worst failure mode — hard veto.
        for impl in ("barbell", "dumbbell", "cable", "kettlebell"):
            if (impl in q_tokens) != (impl in c_tokens):
                score -= 0.2
        if score > best_score:
            best, best_score = ex, score

    return best if best and best_score >= 0.55 else None


def media_for(name: str) -> dict | None:
    """{matched, image_paths, image_urls, instructions} for the UI/PDF, or None."""
    ex = resolve(name)
    if not ex:
        return None
    imgs = [MEDIA_DIR / "images" / p for p in ex["images"]]
    if not all(p.exists() for p in imgs):
        return None
    return {
        "matched": ex["name"],
        "image_paths": [str(p) for p in imgs],
        "image_urls": [f"/api/exercise-images/{p}" for p in ex["images"]],
        "instructions": ex.get("instructions", []),
        "primary_muscles": ex.get("primaryMuscles", []),
    }
