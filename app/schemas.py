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
    notes: str | None = None


class TrainingDay(BaseModel):
    day_label: str = Field(..., description="e.g. 'Day 1 — Lower (Strength)'")
    focus: str
    exercises: list[SetPrescription]


class WorkoutPlan(BaseModel):
    """The agent MUST emit this shape; the PDF renderer consumes it verbatim."""

    program_name: str
    goal: str = Field(..., description="hypertrophy | strength | peaking")
    mesocycle_weeks: int
    periodization_model: str = Field(..., description="'Block' | 'DUP' | 'Linear'")
    weekly_split: list[TrainingDay]
    progression_scheme: str
    deload_protocol: str
    scientific_rationale: str = Field(..., description="Prose grounded ONLY in retrieved sources")
    citations: list[Citation]


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
