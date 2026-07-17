"""Curated starting-point templates by goal. Static and instant — the athlete
browses these, then asks Coach K to personalize (which runs the full grounded
programming pipeline). Exercise names are canonical so form visuals resolve."""

TEMPLATES = [
    {
        "id": "strength-3day",
        "name": "Strength Foundation — 3-Day",
        "goal": "strength",
        "days_per_week": 3,
        "summary": "Squat/bench/deadlift focus at 70-85% 1RM, 2x/week frequency per lift. "
                   "The volume-to-intensity structure follows Prilepin-zone loading.",
        "based_on": "Zatsiorsky's intensity zones · Helms' frequency minimums",
        "days": [
            {"label": "Day 1 — Squat + Bench", "exercises": [
                {"name": "Back Squat", "sets": 4, "reps": "5", "intensity": "@77.5%"},
                {"name": "Bench Press", "sets": 4, "reps": "5", "intensity": "@77.5%"},
                {"name": "Barbell Row", "sets": 3, "reps": "8-10", "intensity": "RPE 8"},
                {"name": "Standing Calf Raise", "sets": 3, "reps": "10-12", "intensity": "1 RIR"},
            ]},
            {"label": "Day 2 — Deadlift + Press", "exercises": [
                {"name": "Deadlift", "sets": 4, "reps": "3-5", "intensity": "@80%"},
                {"name": "Overhead Press", "sets": 4, "reps": "6-8", "intensity": "RPE 8"},
                {"name": "Weighted Pull Up", "sets": 3, "reps": "6-8", "intensity": "RPE 8"},
                {"name": "Hanging Leg Raise", "sets": 3, "reps": "10-15", "intensity": "1 RIR"},
            ]},
            {"label": "Day 3 — Heavy Squat + Bench Volume", "exercises": [
                {"name": "Back Squat", "sets": 3, "reps": "3", "intensity": "@85%"},
                {"name": "Bench Press", "sets": 4, "reps": "8", "intensity": "@70%"},
                {"name": "Romanian Deadlift", "sets": 3, "reps": "8-10", "intensity": "RPE 8"},
                {"name": "Barbell Row", "sets": 3, "reps": "8-10", "intensity": "RPE 8"},
            ]},
        ],
    },
    {
        "id": "hypertrophy-4day",
        "name": "Hypertrophy Builder — 4-Day Upper/Lower",
        "goal": "hypertrophy",
        "days_per_week": 4,
        "summary": "12-18 weekly hard sets per muscle in the 6-12 rep zone, most work "
                   "0-3 RIR — the MEV→MAV progression from the volume-landmark model.",
        "based_on": "Schoenfeld's hypertrophy mechanisms · Helms' volume landmarks",
        "days": [
            {"label": "Upper A", "exercises": [
                {"name": "Bench Press", "sets": 4, "reps": "6-8", "intensity": "2 RIR"},
                {"name": "Barbell Row", "sets": 4, "reps": "8-10", "intensity": "2 RIR"},
                {"name": "Dumbbell Shoulder Press", "sets": 3, "reps": "8-12", "intensity": "2 RIR"},
                {"name": "Lat Pulldown", "sets": 3, "reps": "10-12", "intensity": "1 RIR"},
                {"name": "EZ-Bar Curl", "sets": 3, "reps": "10-12", "intensity": "1 RIR"},
            ]},
            {"label": "Lower A", "exercises": [
                {"name": "Back Squat", "sets": 4, "reps": "6-8", "intensity": "2 RIR"},
                {"name": "Romanian Deadlift", "sets": 3, "reps": "8-10", "intensity": "2 RIR"},
                {"name": "Leg Press", "sets": 3, "reps": "10-12", "intensity": "1 RIR"},
                {"name": "Standing Calf Raise", "sets": 4, "reps": "10-15", "intensity": "1 RIR"},
            ]},
            {"label": "Upper B", "exercises": [
                {"name": "Overhead Press", "sets": 4, "reps": "6-8", "intensity": "2 RIR"},
                {"name": "Weighted Pull Up", "sets": 4, "reps": "6-10", "intensity": "2 RIR"},
                {"name": "Incline Bench Press", "sets": 3, "reps": "8-12", "intensity": "2 RIR"},
                {"name": "Chest-Supported Row", "sets": 3, "reps": "10-12", "intensity": "1 RIR"},
                {"name": "Lying Triceps Extension", "sets": 3, "reps": "10-12", "intensity": "1 RIR"},
            ]},
            {"label": "Lower B", "exercises": [
                {"name": "Deadlift", "sets": 3, "reps": "5-6", "intensity": "2 RIR"},
                {"name": "Bulgarian Split Squat", "sets": 3, "reps": "8-10/leg", "intensity": "2 RIR"},
                {"name": "Leg Extension", "sets": 3, "reps": "12-15", "intensity": "1 RIR"},
                {"name": "Seated Calf Raise", "sets": 4, "reps": "12-15", "intensity": "1 RIR"},
            ]},
        ],
    },
    {
        "id": "explosive-3day",
        "name": "Explosive Athlete — 3-Day",
        "goal": "athleticism",
        "days_per_week": 3,
        "summary": "Rate-of-force development: Olympic lift derivatives, jumps, and heavy "
                   "basic strength — power work fresh and first, strength behind it.",
        "based_on": "Everett's Olympic lift progressions · Grover's Jump Attack · Zatsiorsky's RFD",
        "days": [
            {"label": "Day 1 — Power + Squat", "exercises": [
                {"name": "Power Clean", "sets": 5, "reps": "3", "intensity": "@70-75%"},
                {"name": "Back Squat", "sets": 4, "reps": "5", "intensity": "@75%"},
                {"name": "Romanian Deadlift", "sets": 3, "reps": "8", "intensity": "RPE 7"},
                {"name": "Hanging Leg Raise", "sets": 3, "reps": "10-15", "intensity": "1 RIR"},
            ]},
            {"label": "Day 2 — Jump + Press", "exercises": [
                {"name": "Box Squat", "sets": 5, "reps": "3", "intensity": "explosive @60%"},
                {"name": "Bench Press", "sets": 4, "reps": "5", "intensity": "@75%"},
                {"name": "Weighted Pull Up", "sets": 3, "reps": "6-8", "intensity": "RPE 8"},
                {"name": "Standing Calf Raise", "sets": 4, "reps": "8-10", "intensity": "explosive"},
            ]},
            {"label": "Day 3 — Pull + Unilateral", "exercises": [
                {"name": "Deadlift", "sets": 4, "reps": "3", "intensity": "@80%"},
                {"name": "Bulgarian Split Squat", "sets": 3, "reps": "6-8/leg", "intensity": "RPE 8"},
                {"name": "Overhead Press", "sets": 3, "reps": "6-8", "intensity": "RPE 8"},
                {"name": "Barbell Row", "sets": 3, "reps": "8-10", "intensity": "RPE 8"},
            ]},
        ],
    },
    {
        "id": "general-3day",
        "name": "General Fitness — 3-Day Full Body",
        "goal": "general",
        "days_per_week": 3,
        "summary": "Balanced push/pull/legs each session, moderate loads, honest effort. "
                   "The minimum effective dose that still moves every big lever.",
        "based_on": "Helms' frequency + effort guidelines · Tactical Barbell's sustainability model",
        "days": [
            {"label": "Day 1", "exercises": [
                {"name": "Back Squat", "sets": 3, "reps": "5-8", "intensity": "RPE 7"},
                {"name": "Bench Press", "sets": 3, "reps": "6-10", "intensity": "RPE 7"},
                {"name": "Barbell Row", "sets": 3, "reps": "8-12", "intensity": "RPE 7"},
            ]},
            {"label": "Day 2", "exercises": [
                {"name": "Deadlift", "sets": 3, "reps": "5", "intensity": "RPE 7"},
                {"name": "Overhead Press", "sets": 3, "reps": "6-10", "intensity": "RPE 7"},
                {"name": "Lat Pulldown", "sets": 3, "reps": "8-12", "intensity": "RPE 7"},
            ]},
            {"label": "Day 3", "exercises": [
                {"name": "Front Squat", "sets": 3, "reps": "6-8", "intensity": "RPE 7"},
                {"name": "Incline Bench Press", "sets": 3, "reps": "8-10", "intensity": "RPE 7"},
                {"name": "Romanian Deadlift", "sets": 3, "reps": "8-10", "intensity": "RPE 7"},
            ]},
        ],
    },
]
