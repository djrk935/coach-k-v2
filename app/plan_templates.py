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


# Additional book / source–inspired starting points (canonical exercise names).
TEMPLATES += [
    {
        "id": "starting-strength-novice",
        "name": "Novice Linear — A/B",
        "goal": "strength",
        "days_per_week": 3,
        "summary": "Classic novice linear progression: squat every session, alternate "
                   "bench/press and deadlift/power clean emphasis. Add weight when you hit reps.",
        "based_on": "Starting Strength linear progression model (Rippetoe) · practical novice loading",
        "source_type": "book",
        "days": [
            {"label": "Workout A", "exercises": [
                {"name": "Back Squat", "sets": 3, "reps": "5", "intensity": "across @ working weight"},
                {"name": "Bench Press", "sets": 3, "reps": "5", "intensity": "across @ working weight"},
                {"name": "Deadlift", "sets": 1, "reps": "5", "intensity": "across @ working weight"},
            ]},
            {"label": "Workout B", "exercises": [
                {"name": "Back Squat", "sets": 3, "reps": "5", "intensity": "across @ working weight"},
                {"name": "Overhead Press", "sets": 3, "reps": "5", "intensity": "across @ working weight"},
                {"name": "Power Clean", "sets": 5, "reps": "3", "intensity": "across @ working weight"},
            ]},
            {"label": "Workout A (repeat)", "exercises": [
                {"name": "Back Squat", "sets": 3, "reps": "5", "intensity": "add 5 lbs if last A cleared"},
                {"name": "Bench Press", "sets": 3, "reps": "5", "intensity": "add 2.5–5 lbs if cleared"},
                {"name": "Deadlift", "sets": 1, "reps": "5", "intensity": "add 10 lbs if cleared"},
            ]},
        ],
    },
    {
        "id": "5x5-stronglifts-style",
        "name": "Five Sets of Five — Strength",
        "goal": "strength",
        "days_per_week": 3,
        "summary": "Simple 5×5 strength template with squat frequency and alternating "
                   "pressing. Ideal when you want measurable weekly load jumps.",
        "based_on": "5×5 strength templates (popularized StrongLifts / Madcow lineage)",
        "source_type": "book",
        "days": [
            {"label": "Day A", "exercises": [
                {"name": "Back Squat", "sets": 5, "reps": "5", "intensity": "@~80% or working 5RM"},
                {"name": "Bench Press", "sets": 5, "reps": "5", "intensity": "@~80%"},
                {"name": "Barbell Row", "sets": 5, "reps": "5", "intensity": "RPE 8"},
            ]},
            {"label": "Day B", "exercises": [
                {"name": "Back Squat", "sets": 5, "reps": "5", "intensity": "@~80%"},
                {"name": "Overhead Press", "sets": 5, "reps": "5", "intensity": "@~80%"},
                {"name": "Deadlift", "sets": 1, "reps": "5", "intensity": "@~85%"},
            ]},
            {"label": "Day A2", "exercises": [
                {"name": "Back Squat", "sets": 5, "reps": "5", "intensity": "progress if cleared"},
                {"name": "Bench Press", "sets": 5, "reps": "5", "intensity": "progress if cleared"},
                {"name": "Barbell Row", "sets": 5, "reps": "5", "intensity": "RPE 8"},
            ]},
        ],
    },
    {
        "id": "prilepin-power",
        "name": "Prilepin Power Block — 4-Day",
        "goal": "strength",
        "days_per_week": 4,
        "summary": "Intensity zones mapped to Prilepin’s chart: heavy singles/doubles, "
                   "volume at 70–80%, and speed work under 70% for RFD.",
        "based_on": "Prilepin’s table · Zatsiorsky Science and Practice of Strength Training",
        "source_type": "book",
        "days": [
            {"label": "Day 1 — Squat Heavy", "exercises": [
                {"name": "Back Squat", "sets": 6, "reps": "2", "intensity": "@85–90%"},
                {"name": "Romanian Deadlift", "sets": 3, "reps": "6", "intensity": "RPE 7"},
                {"name": "Hanging Leg Raise", "sets": 3, "reps": "10-15", "intensity": "1 RIR"},
            ]},
            {"label": "Day 2 — Bench Volume", "exercises": [
                {"name": "Bench Press", "sets": 5, "reps": "5", "intensity": "@75%"},
                {"name": "Barbell Row", "sets": 4, "reps": "6-8", "intensity": "RPE 8"},
                {"name": "Dumbbell Shoulder Press", "sets": 3, "reps": "8-10", "intensity": "2 RIR"},
            ]},
            {"label": "Day 3 — Deadlift + Speed", "exercises": [
                {"name": "Deadlift", "sets": 5, "reps": "3", "intensity": "@80–85%"},
                {"name": "Box Squat", "sets": 8, "reps": "2", "intensity": "explosive @60%"},
                {"name": "Pull Up", "sets": 3, "reps": "6-10", "intensity": "RPE 8"},
            ]},
            {"label": "Day 4 — Press + Pull", "exercises": [
                {"name": "Overhead Press", "sets": 5, "reps": "3", "intensity": "@80%"},
                {"name": "Incline Bench Press", "sets": 3, "reps": "6-8", "intensity": "RPE 8"},
                {"name": "Chest-Supported Row", "sets": 4, "reps": "8-10", "intensity": "1 RIR"},
            ]},
        ],
    },
    {
        "id": "helms-hypertrophy-volume",
        "name": "Volume Landmarks — Hypertrophy",
        "goal": "hypertrophy",
        "days_per_week": 4,
        "summary": "MEV→MAV style weekly volumes with 0–3 RIR on most working sets. "
                   "Upper/lower with clear progression on compounds.",
        "based_on": "Renaissance Periodization volume landmarks (Helms / Israetel tradition)",
        "source_type": "book",
        "days": [
            {"label": "Upper A", "exercises": [
                {"name": "Bench Press", "sets": 4, "reps": "6-8", "intensity": "2 RIR"},
                {"name": "Weighted Pull Up", "sets": 4, "reps": "6-8", "intensity": "2 RIR"},
                {"name": "Dumbbell Shoulder Press", "sets": 3, "reps": "8-12", "intensity": "2 RIR"},
                {"name": "Barbell Row", "sets": 3, "reps": "8-10", "intensity": "2 RIR"},
                {"name": "EZ-Bar Curl", "sets": 3, "reps": "10-12", "intensity": "1 RIR"},
                {"name": "Lying Triceps Extension", "sets": 3, "reps": "10-12", "intensity": "1 RIR"},
            ]},
            {"label": "Lower A", "exercises": [
                {"name": "Back Squat", "sets": 4, "reps": "6-8", "intensity": "2 RIR"},
                {"name": "Romanian Deadlift", "sets": 3, "reps": "8-10", "intensity": "2 RIR"},
                {"name": "Bulgarian Split Squat", "sets": 3, "reps": "8-10/leg", "intensity": "2 RIR"},
                {"name": "Standing Calf Raise", "sets": 4, "reps": "10-15", "intensity": "1 RIR"},
            ]},
            {"label": "Upper B", "exercises": [
                {"name": "Overhead Press", "sets": 4, "reps": "6-8", "intensity": "2 RIR"},
                {"name": "Lat Pulldown", "sets": 4, "reps": "8-12", "intensity": "1 RIR"},
                {"name": "Incline Bench Press", "sets": 3, "reps": "8-12", "intensity": "2 RIR"},
                {"name": "Chest-Supported Row", "sets": 3, "reps": "10-12", "intensity": "1 RIR"},
                {"name": "Lateral Raise", "sets": 3, "reps": "12-15", "intensity": "1 RIR"},
            ]},
            {"label": "Lower B", "exercises": [
                {"name": "Deadlift", "sets": 3, "reps": "5", "intensity": "2 RIR"},
                {"name": "Leg Press", "sets": 3, "reps": "10-15", "intensity": "1 RIR"},
                {"name": "Leg Curl", "sets": 3, "reps": "10-15", "intensity": "1 RIR"},
                {"name": "Seated Calf Raise", "sets": 4, "reps": "12-15", "intensity": "1 RIR"},
            ]},
        ],
    },
    {
        "id": "schoenfeld-frequency",
        "name": "Frequency Hypertrophy — Full Body 3",
        "goal": "hypertrophy",
        "days_per_week": 3,
        "summary": "Hit each major muscle ~3×/week with moderate per-session volume — "
                   "the frequency advantage for hypertrophy when recovery allows.",
        "based_on": "Schoenfeld frequency / hypertrophy research synthesis",
        "source_type": "book",
        "days": [
            {"label": "Full Body 1", "exercises": [
                {"name": "Back Squat", "sets": 3, "reps": "6-8", "intensity": "2 RIR"},
                {"name": "Bench Press", "sets": 3, "reps": "6-8", "intensity": "2 RIR"},
                {"name": "Barbell Row", "sets": 3, "reps": "8-10", "intensity": "2 RIR"},
                {"name": "Dumbbell Shoulder Press", "sets": 2, "reps": "10-12", "intensity": "2 RIR"},
                {"name": "EZ-Bar Curl", "sets": 2, "reps": "10-12", "intensity": "1 RIR"},
            ]},
            {"label": "Full Body 2", "exercises": [
                {"name": "Romanian Deadlift", "sets": 3, "reps": "6-8", "intensity": "2 RIR"},
                {"name": "Overhead Press", "sets": 3, "reps": "6-8", "intensity": "2 RIR"},
                {"name": "Lat Pulldown", "sets": 3, "reps": "8-12", "intensity": "1 RIR"},
                {"name": "Bulgarian Split Squat", "sets": 2, "reps": "8-10/leg", "intensity": "2 RIR"},
                {"name": "Lying Triceps Extension", "sets": 2, "reps": "10-12", "intensity": "1 RIR"},
            ]},
            {"label": "Full Body 3", "exercises": [
                {"name": "Front Squat", "sets": 3, "reps": "6-8", "intensity": "2 RIR"},
                {"name": "Incline Bench Press", "sets": 3, "reps": "8-10", "intensity": "2 RIR"},
                {"name": "Chest-Supported Row", "sets": 3, "reps": "8-12", "intensity": "1 RIR"},
                {"name": "Hip Thrust", "sets": 3, "reps": "8-12", "intensity": "2 RIR"},
                {"name": "Standing Calf Raise", "sets": 3, "reps": "10-15", "intensity": "1 RIR"},
            ]},
        ],
    },
    {
        "id": "tactical-barbell-operator",
        "name": "Operator Strength — 3-Day",
        "goal": "strength",
        "days_per_week": 3,
        "summary": "Sustainable operator-style strength: main lifts heavy, limited "
                   "accessories, built for people who also run, practice, or work long days.",
        "based_on": "Tactical Barbell Operator template (Kavanaugh) — adapted",
        "source_type": "book",
        "days": [
            {"label": "Day 1 — Squats", "exercises": [
                {"name": "Back Squat", "sets": 5, "reps": "5", "intensity": "@75–85% rotating"},
                {"name": "Barbell Row", "sets": 3, "reps": "6-8", "intensity": "RPE 8"},
                {"name": "Hanging Leg Raise", "sets": 3, "reps": "10-15", "intensity": "1 RIR"},
            ]},
            {"label": "Day 2 — Bench", "exercises": [
                {"name": "Bench Press", "sets": 5, "reps": "5", "intensity": "@75–85% rotating"},
                {"name": "Weighted Pull Up", "sets": 4, "reps": "5-8", "intensity": "RPE 8"},
                {"name": "Dumbbell Shoulder Press", "sets": 3, "reps": "8-10", "intensity": "2 RIR"},
            ]},
            {"label": "Day 3 — Deadlift", "exercises": [
                {"name": "Deadlift", "sets": 5, "reps": "5", "intensity": "@75–85% rotating"},
                {"name": "Front Squat", "sets": 3, "reps": "5", "intensity": "RPE 7"},
                {"name": "Face Pull", "sets": 3, "reps": "15", "intensity": "1 RIR"},
            ]},
        ],
    },
    {
        "id": "jump-attack-athleticism",
        "name": "Vertical Focus — Athlete 3-Day",
        "goal": "athleticism",
        "days_per_week": 3,
        "summary": "Built for dunkers and jumpers: power first while fresh, strength "
                   "second, unilateral work and calves for spring. Ideal for basketball athletes.",
        "based_on": "Jump Attack principles (Tim Grover) · RFD practices (Zatsiorsky)",
        "source_type": "book",
        "days": [
            {"label": "Day 1 — Power + Squat", "exercises": [
                {"name": "Power Clean", "sets": 5, "reps": "3", "intensity": "@70% explosive"},
                {"name": "Back Squat", "sets": 4, "reps": "5", "intensity": "@75%"},
                {"name": "Bulgarian Split Squat", "sets": 3, "reps": "6/leg", "intensity": "RPE 8"},
                {"name": "Standing Calf Raise", "sets": 4, "reps": "8", "intensity": "explosive"},
            ]},
            {"label": "Day 2 — Upper Power", "exercises": [
                {"name": "Bench Press", "sets": 4, "reps": "5", "intensity": "@75%"},
                {"name": "Weighted Pull Up", "sets": 4, "reps": "5-6", "intensity": "RPE 8"},
                {"name": "Overhead Press", "sets": 3, "reps": "6", "intensity": "RPE 8"},
                {"name": "Face Pull", "sets": 3, "reps": "15", "intensity": "1 RIR"},
            ]},
            {"label": "Day 3 — Posterior + Jump Prep", "exercises": [
                {"name": "Deadlift", "sets": 4, "reps": "3", "intensity": "@80%"},
                {"name": "Box Squat", "sets": 5, "reps": "3", "intensity": "explosive @60%"},
                {"name": "Romanian Deadlift", "sets": 3, "reps": "6", "intensity": "RPE 7"},
                {"name": "Hanging Leg Raise", "sets": 3, "reps": "10-15", "intensity": "1 RIR"},
            ]},
        ],
    },
    {
        "id": "olympic-foundations",
        "name": "Olympic Lift Foundations",
        "goal": "athleticism",
        "days_per_week": 3,
        "summary": "Clean-focused power development with supporting squat and pull strength. "
                   "Keep reps low and quality high on the Olympic derivatives.",
        "based_on": "Olympic Weightlifting (Everett) progressions · coaching common practice",
        "source_type": "book",
        "days": [
            {"label": "Day 1 — Clean + Squat", "exercises": [
                {"name": "Power Clean", "sets": 6, "reps": "2", "intensity": "@70–75%"},
                {"name": "Front Squat", "sets": 4, "reps": "3", "intensity": "@75–80%"},
                {"name": "Pull Up", "sets": 3, "reps": "6-8", "intensity": "RPE 8"},
            ]},
            {"label": "Day 2 — Pull + Press", "exercises": [
                {"name": "Deadlift", "sets": 4, "reps": "3", "intensity": "@80%"},
                {"name": "Overhead Press", "sets": 4, "reps": "5", "intensity": "RPE 8"},
                {"name": "Barbell Row", "sets": 3, "reps": "6-8", "intensity": "RPE 8"},
            ]},
            {"label": "Day 3 — Speed + Back Squat", "exercises": [
                {"name": "Power Clean", "sets": 5, "reps": "3", "intensity": "@65–70% speed"},
                {"name": "Back Squat", "sets": 4, "reps": "5", "intensity": "@75%"},
                {"name": "Romanian Deadlift", "sets": 3, "reps": "6", "intensity": "RPE 7"},
            ]},
        ],
    },
    {
        "id": "push-pull-legs-classic",
        "name": "Push Pull Legs — Classic 6",
        "goal": "hypertrophy",
        "days_per_week": 6,
        "summary": "High-frequency bodybuilding split: push, pull, legs twice per week. "
                   "Best when recovery, sleep, and protein are dialed.",
        "based_on": "Classic PPL bodybuilding programming · Helms effort guidelines",
        "source_type": "community",
        "days": [
            {"label": "Push A", "exercises": [
                {"name": "Bench Press", "sets": 4, "reps": "6-8", "intensity": "2 RIR"},
                {"name": "Overhead Press", "sets": 3, "reps": "8-10", "intensity": "2 RIR"},
                {"name": "Incline Bench Press", "sets": 3, "reps": "8-12", "intensity": "2 RIR"},
                {"name": "Lateral Raise", "sets": 3, "reps": "12-15", "intensity": "1 RIR"},
                {"name": "Lying Triceps Extension", "sets": 3, "reps": "10-12", "intensity": "1 RIR"},
            ]},
            {"label": "Pull A", "exercises": [
                {"name": "Deadlift", "sets": 3, "reps": "5", "intensity": "2 RIR"},
                {"name": "Weighted Pull Up", "sets": 3, "reps": "6-8", "intensity": "2 RIR"},
                {"name": "Barbell Row", "sets": 3, "reps": "8-10", "intensity": "2 RIR"},
                {"name": "Face Pull", "sets": 3, "reps": "15", "intensity": "1 RIR"},
                {"name": "EZ-Bar Curl", "sets": 3, "reps": "10-12", "intensity": "1 RIR"},
            ]},
            {"label": "Legs A", "exercises": [
                {"name": "Back Squat", "sets": 4, "reps": "6-8", "intensity": "2 RIR"},
                {"name": "Romanian Deadlift", "sets": 3, "reps": "8-10", "intensity": "2 RIR"},
                {"name": "Leg Press", "sets": 3, "reps": "10-12", "intensity": "1 RIR"},
                {"name": "Standing Calf Raise", "sets": 4, "reps": "10-15", "intensity": "1 RIR"},
            ]},
            {"label": "Push B", "exercises": [
                {"name": "Overhead Press", "sets": 4, "reps": "6-8", "intensity": "2 RIR"},
                {"name": "Bench Press", "sets": 3, "reps": "8-10", "intensity": "2 RIR"},
                {"name": "Dumbbell Shoulder Press", "sets": 3, "reps": "10-12", "intensity": "2 RIR"},
                {"name": "Lateral Raise", "sets": 3, "reps": "12-15", "intensity": "1 RIR"},
                {"name": "Lying Triceps Extension", "sets": 3, "reps": "10-12", "intensity": "1 RIR"},
            ]},
            {"label": "Pull B", "exercises": [
                {"name": "Barbell Row", "sets": 4, "reps": "6-8", "intensity": "2 RIR"},
                {"name": "Lat Pulldown", "sets": 3, "reps": "8-12", "intensity": "1 RIR"},
                {"name": "Chest-Supported Row", "sets": 3, "reps": "10-12", "intensity": "1 RIR"},
                {"name": "Face Pull", "sets": 3, "reps": "15", "intensity": "1 RIR"},
                {"name": "EZ-Bar Curl", "sets": 3, "reps": "10-12", "intensity": "1 RIR"},
            ]},
            {"label": "Legs B", "exercises": [
                {"name": "Front Squat", "sets": 4, "reps": "6-8", "intensity": "2 RIR"},
                {"name": "Bulgarian Split Squat", "sets": 3, "reps": "8-10/leg", "intensity": "2 RIR"},
                {"name": "Leg Curl", "sets": 3, "reps": "10-15", "intensity": "1 RIR"},
                {"name": "Seated Calf Raise", "sets": 4, "reps": "12-15", "intensity": "1 RIR"},
            ]},
        ],
    },
    {
        "id": "minimalist-2day",
        "name": "Busy Schedule — 2-Day Full Body",
        "goal": "general",
        "days_per_week": 2,
        "summary": "Minimum effective dose for crowded weeks: two full-body sessions "
                   "covering squat, hinge, push, pull. Perfect travel companion.",
        "based_on": "Helms minimum effective dose · practical coaching constraints",
        "source_type": "coach",
        "days": [
            {"label": "Day 1", "exercises": [
                {"name": "Back Squat", "sets": 3, "reps": "5-8", "intensity": "RPE 7-8"},
                {"name": "Bench Press", "sets": 3, "reps": "5-8", "intensity": "RPE 7-8"},
                {"name": "Barbell Row", "sets": 3, "reps": "6-10", "intensity": "RPE 7-8"},
                {"name": "Romanian Deadlift", "sets": 2, "reps": "6-10", "intensity": "RPE 7"},
            ]},
            {"label": "Day 2", "exercises": [
                {"name": "Deadlift", "sets": 3, "reps": "3-5", "intensity": "RPE 7-8"},
                {"name": "Overhead Press", "sets": 3, "reps": "5-8", "intensity": "RPE 7-8"},
                {"name": "Pull Up", "sets": 3, "reps": "5-10", "intensity": "RPE 8"},
                {"name": "Bulgarian Split Squat", "sets": 2, "reps": "8/leg", "intensity": "RPE 7"},
            ]},
        ],
    },
    {
        "id": "recomp-4day",
        "name": "Recomposition — 4-Day",
        "goal": "hypertrophy",
        "days_per_week": 4,
        "summary": "Strength on compounds + hypertrophy accessories. Pair with a small "
                   "calorie deficit or maintenance and high protein for visible recomp.",
        "based_on": "Helms Muscle & Strength Pyramids · practical recomp coaching",
        "source_type": "book",
        "days": [
            {"label": "Upper Strength", "exercises": [
                {"name": "Bench Press", "sets": 4, "reps": "4-6", "intensity": "2 RIR"},
                {"name": "Weighted Pull Up", "sets": 4, "reps": "4-6", "intensity": "2 RIR"},
                {"name": "Overhead Press", "sets": 3, "reps": "6-8", "intensity": "2 RIR"},
                {"name": "Face Pull", "sets": 3, "reps": "15", "intensity": "1 RIR"},
            ]},
            {"label": "Lower Strength", "exercises": [
                {"name": "Back Squat", "sets": 4, "reps": "4-6", "intensity": "2 RIR"},
                {"name": "Romanian Deadlift", "sets": 3, "reps": "6-8", "intensity": "2 RIR"},
                {"name": "Walking Lunge", "sets": 2, "reps": "10/leg", "intensity": "2 RIR"},
                {"name": "Standing Calf Raise", "sets": 3, "reps": "10-15", "intensity": "1 RIR"},
            ]},
            {"label": "Upper Pump", "exercises": [
                {"name": "Incline Bench Press", "sets": 3, "reps": "8-12", "intensity": "2 RIR"},
                {"name": "Lat Pulldown", "sets": 3, "reps": "10-12", "intensity": "1 RIR"},
                {"name": "Dumbbell Shoulder Press", "sets": 3, "reps": "10-12", "intensity": "2 RIR"},
                {"name": "EZ-Bar Curl", "sets": 2, "reps": "10-12", "intensity": "1 RIR"},
                {"name": "Lying Triceps Extension", "sets": 2, "reps": "10-12", "intensity": "1 RIR"},
            ]},
            {"label": "Lower Pump", "exercises": [
                {"name": "Leg Press", "sets": 3, "reps": "10-15", "intensity": "1 RIR"},
                {"name": "Hip Thrust", "sets": 3, "reps": "8-12", "intensity": "2 RIR"},
                {"name": "Leg Curl", "sets": 3, "reps": "10-15", "intensity": "1 RIR"},
                {"name": "Seated Calf Raise", "sets": 3, "reps": "12-15", "intensity": "1 RIR"},
            ]},
        ],
    },
]
