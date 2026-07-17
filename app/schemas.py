"""Pydantic contracts: the agent emits these; DB + PDF renderer consume them."""

from typing import Any

from pydantic import BaseModel, Field


# ===== Program artifact (agent → DB → PDF) =====

class Citation(BaseModel):
    chunk_id: str = Field(..., description="chunk id from the retrieved context block")
    book: str
    page: int | None = None
    principle: str = Field(
        ..., description="The principle applied, e.g. 'Prilepin: 70-80% → 12-24 optimal reps'"
    )


class SetPrescription(BaseModel):
    exercise: str
    sets: int
    reps: str = Field(..., description="'5', '8-10', or 'AMRAP'")
    intensity: str = Field(..., description="'@75% 1RM', 'RPE 8', or '2 RIR'")
    tempo: str | None = None
    rest_s: int | None = None
    set_type: str = Field(
        "straight", description="'warmup' | 'straight' | 'superset' | 'finisher'"
    )
    superset_group: str | None = Field(
        None, description="Exercises sharing a letter (e.g. 'A') are performed back-to-back"
    )
    notes: str | None = None


class TrainingDay(BaseModel):
    day_label: str = Field(..., description="e.g. 'Day 1 — Lower (Strength)'")
    focus: str
    exercises: list[SetPrescription]


class NutritionTargets(BaseModel):
    """Daily targets to support the training goal. Coach's estimate off the
    profile — labeled as guidance, not a meal plan."""

    calories: int
    protein_g: int
    carbs_g: int
    fat_g: int
    guidance: str = Field(..., description="1-3 sentences: timing, protein spread, hydration")


class WorkoutPlan(BaseModel):
    """The agent MUST emit this shape; the PDF renderer consumes it verbatim."""

    program_name: str
    goal: str = Field(..., description="hypertrophy | strength | peaking")
    mesocycle_weeks: int
    periodization_model: str = Field(..., description="'Block' | 'DUP' | 'Linear'")
    weekly_split: list[TrainingDay]
    progression_scheme: str
    deload_protocol: str
    nutrition: NutritionTargets | None = Field(
        None, description="Include when profile has enough info (bodyweight helps)"
    )
    scientific_rationale: str = Field(..., description="Prose grounded ONLY in retrieved sources")
    citations: list[Citation]


# ===== Physique photo analysis =====

class PhysiqueAssessment(BaseModel):
    """Honest, constructive read of physique photos. Ranges, never precision."""

    overall: str = Field(..., description="2-3 sentence honest overall read, coach's voice")
    estimated_bodyfat_range: str = Field(
        ..., description="A RANGE with a hedge, e.g. 'roughly 15-18% (photo-based estimate)'"
    )
    strong_points: list[str] = Field(..., description="Muscle groups / traits that stand out")
    lagging_points: list[str] = Field(..., description="What to prioritize, said constructively")
    posture_notes: str | None = Field(None, description="Only if clearly visible")
    vs_previous: str | None = Field(
        None, description="Comparison to prior assessments when provided, else null"
    )
    training_implications: str = Field(
        ..., description="How this shapes programming: volume allocation, exercise emphasis"
    )


# ===== Evolving memory (extracted from conversation) =====

class ReadinessEntry(BaseModel):
    sleep_h: float | None = None
    soreness_0_10: int | None = None
    stress_0_10: int | None = None
    motivation_0_10: int | None = None
    bodyweight_kg: float | None = None
    notes: str | None = None


class LoggedSet(BaseModel):
    exercise: str
    weight_kg: float | None = None
    reps: int | None = None
    rir: float | None = None


class WorkoutLog(BaseModel):
    session_rpe: float | None = None
    notes: str | None = None
    sets: list[LoggedSet] = []


class PainEvent(BaseModel):
    region: str
    severity: int = Field(..., ge=0, le=10)
    context: str | None = None


class MemoryDelta(BaseModel):
    """What this turn taught us that should persist. All fields optional."""

    profile_patch: dict[str, Any] | None = Field(
        None,
        description=(
            "JSON merge patch for the athlete profile: goals, 1RMs, equipment, "
            "schedule, injuries, preferences. Only include keys that changed."
        ),
    )
    readiness: ReadinessEntry | None = Field(
        None, description="Today's readiness signals, if any were mentioned"
    )
    workout: WorkoutLog | None = Field(
        None, description="A completed workout being reported, if any"
    )
    pain: list[PainEvent] = Field(default_factory=list)
