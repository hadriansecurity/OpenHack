"""Layer 1: JSON Schema golden tests.

For each durable-artifact schema we keep a minimum-valid baseline and a
table of single-field mutations that should fail validation. The assertions
check both that the validator raises and that the error message points at
the right JSON path — that way a schema change that silently loosens a rule
still trips the test.
"""

from __future__ import annotations

import copy
from typing import Any, Callable

import pytest

from openhack.schemas import (
    validate_finding,
    validate_finding_candidate,
    validate_finding_triage,
    validate_result,
    validate_scenario,
)

SHA256 = "a" * 64


# ---------------------------------------------------------------------------
# Baselines
# ---------------------------------------------------------------------------


def _scenario() -> dict[str, Any]:
    return {
        "id": "S001",
        "recon_item_id": "R001",
        "expert": "injection",
        "target_path": "app/Http/Foo.php",
        "proof_question": "Is the user-supplied id concatenated into a raw SQL query?",
        "evidence_required": ["sink call", "lack of binding"],
    }


def _scenario_result() -> dict[str, Any]:
    return {
        "scenario_id": "S001",
        "review_mode": "per-scenario-subagent",
        "subagent_id": "agent-1",
        "scenario_prompt_sha256": SHA256,
        "reviewed_files": ["app/Http/Foo.php"],
        "status": "verified",
        "expert": "injection",
        "summary": "Confirmed raw SQL concatenation.",
        "evidence": [
            {
                "path": "app/Http/Foo.php",
                "line": 42,
                "snippet": "$db->raw($_GET['id'])",
                "note": "user input flows directly into raw()",
            }
        ],
    }


def _finding() -> dict[str, Any]:
    return {
        "title": "SQL injection in Foo.php",
        "severity": "high",
        "target_path": "app/Http/Foo.php",
        "attacker_role": "unauthenticated user",
        "preconditions": "Endpoint reachable without auth.",
        "non_technical_summary": "An attacker can read the database.",
        "summary": "Raw SQL built from user input.",
        "attack_chain": "GET /foo?id=' OR 1=1 -- → raw() executes attacker SQL",
        "example_attack": "curl 'http://host/foo?id=1%20OR%201=1--'",
        "evidence": "See app/Http/Foo.php:42",
        "impact": "Full database read.",
        "impact_analysis": "User table and secrets exposed.",
        "attacker_use": "Exfiltrate PII.",
        "recommended_fix": "Use parameter binding.",
        "validation_notes": "Reproduced locally on commit abc123.",
    }


def _finding_candidate() -> dict[str, Any]:
    return {
        "candidate_id": "S001-F001",
        "scenario_id": "S001",
        "source_result": "scenarios/finished/S001.json",
        "expert": "injection",
        "status": "pending_triage",
        "finding": _finding(),
    }


def _finding_triage() -> dict[str, Any]:
    return {
        "candidate_id": "S001-F001",
        "review_mode": "per-finding-triage-agent",
        "triage_agent_id": "triage-1",
        "triage_prompt_sha256": SHA256,
        "reviewed_files": ["app/Http/Foo.php"],
        "decision": "accepted",
        "summary": "Confirmed vulnerable.",
        "final_severity": "high",
        "severity_rationale": "Direct DB read by unauth user.",
        "confidence": "high",
        "evidence_assessment": "Evidence is sufficient.",
        "evidence_gaps": [],
        "required_changes": [],
    }


# ---------------------------------------------------------------------------
# Mutation helpers
# ---------------------------------------------------------------------------


def _drop(key: str) -> Callable[[dict[str, Any]], None]:
    def mutate(value: dict[str, Any]) -> None:
        value.pop(key, None)

    return mutate


def _set(path: list[str | int], new_value: Any) -> Callable[[dict[str, Any]], None]:
    def mutate(value: dict[str, Any]) -> None:
        cursor: Any = value
        for part in path[:-1]:
            cursor = cursor[part]
        cursor[path[-1]] = new_value

    return mutate


# ---------------------------------------------------------------------------
# Happy paths
# ---------------------------------------------------------------------------


def test_scenario_baseline_validates() -> None:
    validate_scenario(_scenario())


def test_scenario_result_baseline_validates() -> None:
    validate_result(_scenario_result(), scenario_id="S001")


def test_finding_baseline_validates() -> None:
    validate_finding(_finding())


def test_finding_candidate_baseline_validates() -> None:
    validate_finding_candidate(_finding_candidate())


def test_finding_triage_baseline_validates() -> None:
    validate_finding_triage(_finding_triage())


def test_finding_evidence_accepts_all_three_shapes() -> None:
    """Schema declares ``evidence`` as ``oneOf [string, array, object]``."""
    for shape in (
        "string evidence",
        [{"path": "a.php", "line": 1, "snippet": "x", "note": "n"}],
        {"path": "a.php", "details": "..."},
    ):
        finding = _finding()
        finding["evidence"] = shape
        validate_finding(finding)


# ---------------------------------------------------------------------------
# Negative cases — each row mutates the baseline and asserts a failure path
# ---------------------------------------------------------------------------


SCENARIO_CASES = [
    pytest.param(_drop("id"), "$", id="missing-id"),
    pytest.param(_drop("expert"), "$", id="missing-expert"),
    pytest.param(_drop("proof_question"), "$", id="missing-proof-question"),
    pytest.param(_set(["id"], "S99"), "$.id", id="id-too-short"),
    pytest.param(_set(["id"], "scenario-1"), "$.id", id="id-bad-prefix"),
    pytest.param(_set(["evidence_required"], 7), "$.evidence_required", id="evidence-bad-type"),
    pytest.param(_set(["evidence_required"], [""]), "$.evidence_required", id="evidence-array-empty-string"),
    pytest.param(_set(["target_path"], ""), "$.target_path", id="target-path-empty"),
    pytest.param(_set(["priority"], "urgent"), "$.priority", id="priority-bad-enum"),
    pytest.param(_set(["routing_unit_id"], "unit-1"), "$.routing_unit_id", id="routing-unit-bad-pattern"),
    pytest.param(
        _set(["proof_obligations"], [{"id": "BAD ID", "question": "?", "evidence_required": "e"}]),
        "$.proof_obligations.0.id",
        id="obligation-id-bad-pattern",
    ),
    pytest.param(
        _set(["proof_obligations"], [{"id": "ok", "question": "?"}]),
        "$.proof_obligations.0",
        id="obligation-missing-evidence-required",
    ),
]


@pytest.mark.parametrize("mutate,expected_path", SCENARIO_CASES)
def test_scenario_invalid_cases(mutate: Callable[[dict[str, Any]], None], expected_path: str) -> None:
    scenario = _scenario()
    mutate(scenario)
    with pytest.raises(ValueError) as exc:
        validate_scenario(scenario)
    assert expected_path in str(exc.value)
    assert "scenario-schema.json" in str(exc.value)


RESULT_CASES = [
    pytest.param(_drop("scenario_id"), "$", id="missing-scenario-id"),
    pytest.param(_set(["scenario_id"], "X1"), "$.scenario_id", id="scenario-id-bad-pattern"),
    pytest.param(_set(["review_mode"], "batch"), "$.review_mode", id="review-mode-not-allowed"),
    pytest.param(_set(["status"], "maybe"), "$.status", id="status-bad-enum"),
    pytest.param(_set(["scenario_prompt_sha256"], "deadbeef"), "$.scenario_prompt_sha256", id="sha-too-short"),
    pytest.param(_set(["reviewed_files"], []), "$.reviewed_files", id="reviewed-files-empty"),
    pytest.param(_set(["evidence"], []), "$.evidence", id="evidence-empty"),
    pytest.param(
        _set(["evidence"], [{"path": "a.php", "line": 1, "snippet": "x"}]),
        "$.evidence.0",
        id="evidence-missing-note",
    ),
    pytest.param(
        _set(["proof_obligations"], [{"id": "ok", "status": "weird", "summary": "s"}]),
        "$.proof_obligations.0.status",
        id="obligation-status-bad-enum",
    ),
]


@pytest.mark.parametrize("mutate,expected_path", RESULT_CASES)
def test_scenario_result_invalid_cases(
    mutate: Callable[[dict[str, Any]], None], expected_path: str
) -> None:
    result = _scenario_result()
    mutate(result)
    with pytest.raises(ValueError) as exc:
        validate_result(result, scenario_id="S001")
    assert expected_path in str(exc.value)
    assert "scenario-result-schema.json" in str(exc.value)


FINDING_CASES = [
    pytest.param(_drop("title"), "$", id="missing-title"),
    pytest.param(_drop("recommended_fix"), "$", id="missing-recommended-fix"),
    pytest.param(_set(["severity"], "catastrophic"), "$.severity", id="severity-bad-enum"),
    pytest.param(_set(["summary"], ""), "$.summary", id="summary-empty"),
    pytest.param(_set(["evidence"], 7), "$.evidence", id="evidence-bad-type"),
]


@pytest.mark.parametrize("mutate,expected_path", FINDING_CASES)
def test_finding_invalid_cases(
    mutate: Callable[[dict[str, Any]], None], expected_path: str
) -> None:
    finding = _finding()
    mutate(finding)
    with pytest.raises(ValueError) as exc:
        validate_finding(finding)
    assert expected_path in str(exc.value)
    assert "finding-schema.json" in str(exc.value)


CANDIDATE_CASES = [
    pytest.param(_drop("candidate_id"), "$", id="missing-candidate-id"),
    pytest.param(_set(["candidate_id"], "S001-001"), "$.candidate_id", id="candidate-id-bad-pattern"),
    pytest.param(_set(["candidate_id"], "S1-F1"), "$.candidate_id", id="candidate-id-too-short"),
    pytest.param(_set(["status"], "accepted"), "$.status", id="status-not-pending-triage"),
    pytest.param(_set(["scenario_id"], "scn-1"), "$.scenario_id", id="scenario-id-bad-pattern"),
]


@pytest.mark.parametrize("mutate,expected_path", CANDIDATE_CASES)
def test_finding_candidate_invalid_cases(
    mutate: Callable[[dict[str, Any]], None], expected_path: str
) -> None:
    candidate = _finding_candidate()
    mutate(candidate)
    with pytest.raises(ValueError) as exc:
        validate_finding_candidate(candidate)
    assert expected_path in str(exc.value)
    assert "finding-candidate-schema.json" in str(exc.value)


TRIAGE_CASES = [
    pytest.param(_drop("decision"), "$", id="missing-decision"),
    pytest.param(_drop("evidence_gaps"), "$", id="missing-evidence-gaps"),
    pytest.param(_set(["decision"], "approved"), "$.decision", id="decision-bad-enum"),
    pytest.param(_set(["review_mode"], "per-scenario-subagent"), "$.review_mode", id="review-mode-wrong"),
    pytest.param(_set(["final_severity"], "huge"), "$.final_severity", id="severity-bad-enum"),
    pytest.param(_set(["confidence"], "very-high"), "$.confidence", id="confidence-bad-enum"),
    pytest.param(_set(["triage_prompt_sha256"], "ZZZ"), "$.triage_prompt_sha256", id="sha-bad-pattern"),
    pytest.param(_set(["reviewed_files"], []), "$.reviewed_files", id="reviewed-files-empty"),
]


@pytest.mark.parametrize("mutate,expected_path", TRIAGE_CASES)
def test_finding_triage_invalid_cases(
    mutate: Callable[[dict[str, Any]], None], expected_path: str
) -> None:
    triage = _finding_triage()
    mutate(triage)
    with pytest.raises(ValueError) as exc:
        validate_finding_triage(triage)
    assert expected_path in str(exc.value)
    assert "finding-triage-schema.json" in str(exc.value)


def test_validator_reports_multiple_errors() -> None:
    """The error message bullets each violation so authors can fix in one pass."""
    scenario = _scenario()
    scenario.pop("id")
    scenario.pop("expert")
    scenario["target_path"] = ""
    with pytest.raises(ValueError) as exc:
        validate_scenario(scenario)
    message = str(exc.value)
    # Each missing required field surfaces as a separate bullet.
    assert message.count("\n- ") >= 3


def test_baselines_are_independent() -> None:
    """Mutating one fixture instance must not leak into another."""
    a = _scenario()
    b = _scenario()
    a["id"] = "S999"
    assert b["id"] == "S001"
    # And the deep-copy assumption holds for nested structures.
    a2 = copy.deepcopy(_scenario_result())
    a2["evidence"][0]["note"] = "mutated"
    fresh = _scenario_result()
    assert fresh["evidence"][0]["note"] != "mutated"
