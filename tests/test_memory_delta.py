"""MemoryDelta coercion — LLM sometimes emits the string 'null' for lists."""

from app.schemas import MemoryDelta


def test_memory_delta_pain_null_string():
    d = MemoryDelta.model_validate({"pain": "null"})
    assert d.pain == []


def test_memory_delta_pain_none_and_empty():
    assert MemoryDelta.model_validate({"pain": None}).pain == []
    assert MemoryDelta.model_validate({}).pain == []


def test_memory_delta_optional_null_strings():
    d = MemoryDelta.model_validate(
        {
            "profile_patch": "null",
            "readiness": "null",
            "workout": "none",
            "pain": "[]",
        }
    )
    assert d.profile_patch is None
    assert d.readiness is None
    assert d.workout is None
    assert d.pain == []


def test_memory_delta_pain_event_ok():
    d = MemoryDelta.model_validate(
        {"pain": [{"region": "knee", "severity": 4, "context": "squat"}]}
    )
    assert len(d.pain) == 1
    assert d.pain[0].region == "knee"
