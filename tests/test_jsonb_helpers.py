"""JSONB decode helpers — keep in sync with app.agent.tools._as_dict / _as_list."""

import json


def _as_dict(val):
    if val is None:
        return {}
    if isinstance(val, memoryview):
        val = val.tobytes().decode()
    if isinstance(val, bytes):
        val = val.decode()
    if isinstance(val, str):
        val = json.loads(val)
    if isinstance(val, str):
        val = json.loads(val)
    return dict(val) if isinstance(val, dict) else {}


def test_as_dict_object_and_encoded_string():
    obj = {"weekly_split": [{"day_label": "A"}], "program_name": "Strength"}
    assert _as_dict(obj)["program_name"] == "Strength"
    assert _as_dict(json.dumps(obj))["weekly_split"][0]["day_label"] == "A"
    # Legacy double-encoded scalar
    assert _as_dict(json.dumps(json.dumps(obj)))["program_name"] == "Strength"


def test_as_dict_empty():
    assert _as_dict(None) == {}
    assert _as_dict("{}") == {}
