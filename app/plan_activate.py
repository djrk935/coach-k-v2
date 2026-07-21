"""Convert curated TEMPLATES into executable WorkoutPlan dicts."""

from __future__ import annotations

from app.plan_templates import TEMPLATES
from app.schemas import (
    Citation,
    NutritionTargets,
    SetPrescription,
    TrainingDay,
    WorkoutPlan,
)


def get_template(template_id: str) -> dict | None:
    for t in TEMPLATES:
        if t["id"] == template_id:
            return t
    return None


def template_to_workout_plan(t: dict, athlete_name: str | None = None) -> WorkoutPlan:
    """Map a gallery template into the agent WorkoutPlan contract."""
    days: list[TrainingDay] = []
    for d in t["days"]:
        exercises = [
            SetPrescription(
                exercise=ex["name"],
                sets=int(ex["sets"]),
                reps=str(ex["reps"]),
                intensity=str(ex["intensity"]),
                set_type="straight",
                notes=None,
            )
            for ex in d["exercises"]
        ]
        days.append(
            TrainingDay(
                day_label=d["label"],
                focus=t.get("summary", t["goal"])[:120],
                exercises=exercises,
            )
        )

    who = f" for {athlete_name}" if athlete_name else ""
    return WorkoutPlan(
        program_name=t["name"],
        goal=t["goal"],
        mesocycle_weeks=6,
        periodization_model="Linear" if t["goal"] == "strength" else "Block",
        weekly_split=days,
        progression_scheme=(
            "Double progression on compounds: add load when you clear the top of the rep range "
            "across all prescribed sets. Hold accessories at 1–2 RIR."
        ),
        deload_protocol=(
            "Every 5–6 weeks (or when ACWR > 1.5 / readiness stays compromised): "
            "cut volume ~40–50%, keep technique intensity, prioritize sleep."
        ),
        nutrition=None,
        scientific_rationale=(
            f"Starter block{who} adapted from: {t.get('based_on', 'coach library')}. "
            f"{t.get('summary', '')} Coach K can personalize loads, swaps, and nutrition next."
        ),
        citations=[
            Citation(
                chunk_id="template",
                book=t.get("based_on", "Coach K plan library"),
                page=None,
                principle="Curated starter template — personalize with library RAG as needed",
            )
        ],
    )


def suggest_nutrition(bodyweight_lbs: float | None, goal: str) -> NutritionTargets | None:
    if not bodyweight_lbs:
        return None
    bw = float(bodyweight_lbs)
    protein = round(bw * 0.9)
    if goal in ("hypertrophy", "recomposition", "athleticism"):
        cals = round(bw * 14)
    elif goal == "strength":
        cals = round(bw * 15)
    else:
        cals = round(bw * 13)
    fat = round(bw * 0.35)
    carbs = max(100, round((cals - protein * 4 - fat * 9) / 4))
    return NutritionTargets(
        calories=cals,
        protein_g=protein,
        carbs_g=carbs,
        fat_g=fat,
        guidance=(
            "Estimate only — spread protein across 3–4 meals, drink water through the day, "
            "and adjust calories ±200 after two weeks of bodyweight trend."
        ),
    )
