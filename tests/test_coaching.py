"""Unit tests for deterministic coaching helpers (no DB / LLM)."""

from app.coaching.adapt import adaptation_for, apply_volume_scale, readiness_score_from_entry
from app.coaching.injury import (
    build_injury_protocols,
    merge_pain_regions,
    quick_region_options,
    regions_from_profile_injuries,
)
from app.coaching.swaps import form_cue_for, normalize_region, suggest_swap, swaps_for_regions
from app.coaching.warmup import warmup_ramp


def test_normalize_region_aliases():
    assert normalize_region("Knees") == "knee"
    assert normalize_region("lower back") == "low back"
    assert normalize_region("rotator") == "shoulder"
    assert normalize_region("mystery") is None


def test_suggest_swap_skips_same_lift():
    alt = suggest_swap("Leg Press", ["knee"])
    assert alt is not None
    assert alt.lower() != "leg press"


def test_swaps_for_regions():
    out = swaps_for_regions(["knee", "shoulder"], limit=2)
    assert "knee" in out and len(out["knee"]) == 2
    assert "shoulder" in out


def test_form_cue_for_known_lift():
    cue = form_cue_for("Back Squat")
    assert cue and "brace" in cue.lower()


def test_merge_pain_and_profile_injuries():
    regions = merge_pain_regions(
        ["knees"],
        regions_from_profile_injuries(["low back", {"region": "Shoulder"}]),
    )
    labels = {r.lower() for r in regions}
    assert "knee" in labels or "Knee" in regions
    assert any("back" in r.lower() for r in regions)
    assert any("shoulder" in r.lower() for r in regions)


def test_build_injury_protocols():
    cards = build_injury_protocols(["knee", "shoulder"])
    assert len(cards) == 2
    assert cards[0]["region_key"] == "knee"
    assert cards[0]["steps"]
    assert cards[0]["alternatives"]
    assert quick_region_options()


def test_adaptation_pain_forces_soft_day():
    adapt = adaptation_for(
        {"sleep_h": 8, "soreness_0_10": 2, "stress_0_10": 2, "motivation_0_10": 8},
        {"acwr": 1.0},
        ["knee"],
    )
    assert adapt["soft_day"] is True
    assert adapt["volume_scale"] <= 0.7
    assert any("pain" in r.lower() for r in adapt["reasons"])


def test_adaptation_acwr_spike():
    adapt = adaptation_for(None, {"acwr": 1.6}, None)
    assert adapt["soft_day"] is True
    assert adapt["volume_scale"] <= 0.6


def test_readiness_score_from_fields():
    score, status = readiness_score_from_entry(
        {"sleep_h": 8, "soreness_0_10": 2, "stress_0_10": 2, "motivation_0_10": 9}
    )
    assert score is not None and score >= 65
    assert status in ("primed", "ready", "moderate", "compromised")


def test_apply_volume_scale_keeps_warmup():
    exs = [
        {"exercise": "Squat", "sets": 4, "set_type": "straight"},
        {"exercise": "Squat", "sets": 2, "set_type": "warmup"},
    ]
    out = apply_volume_scale(exs, 0.5)
    assert out[0]["sets"] == 2
    assert out[0].get("adapted") is True
    assert out[1]["sets"] == 2
    assert out[1].get("adapted") is not True


def test_warmup_ramp_compound():
    sets = warmup_ramp(225, exercise="Back Squat")
    assert len(sets) >= 2
    assert all(s["weight_lbs"] < 225 for s in sets if s["weight_lbs"] is not None)


def test_warmup_ramp_skips_finisher():
    assert warmup_ramp(100, exercise="Curl", set_type="finisher") == []
