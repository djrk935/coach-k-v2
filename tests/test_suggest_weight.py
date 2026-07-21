"""Weight suggestion helpers must tolerate stringy 1RMs from profiles."""

from app.agent.tools import _suggest_weight


def test_suggest_weight_int_1rm():
    assert _suggest_weight("Back Squat", "@80%", {"squat": 225}, None) == 180


def test_suggest_weight_string_1rm():
    assert _suggest_weight("Back Squat", "@80%", {"squat": "225"}, None) == 180


def test_suggest_weight_falls_back_to_last():
    assert _suggest_weight("Curl", "RPE 8", {}, 40) == 40.0
