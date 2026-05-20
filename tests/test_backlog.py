"""Layer 2: scenario backlog validation and write-out."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from openhack import backlog
from openhack.backlog import (
    DECISIONS,
    _scenario_covers_boundary,
    _scenario_covers_pair,
    _scenario_covers_path,
    _scenario_covers_unit,
    _scenario_paths,
    _validate_decisions,
    coverage_errors,
    record_backlog,
)

EXPERTS = {
    "injection",
    "broken-access-control",
    "authentication-failures",
    "cryptographic-failures",
}


# ---------------------------------------------------------------------------
# _scenario_paths
# ---------------------------------------------------------------------------


def test_scenario_paths_collects_from_all_fields() -> None:
    scenario: dict[str, Any] = {
        "target_path": "app/Foo.php",
        "target_paths": ["app/Bar.php", "app/Baz.php"],
        "related_paths": "app/Util.php",
        "covered_paths": ["app/Inc.php"],
    }
    assert _scenario_paths(scenario) == {
        "app/Foo.php",
        "app/Bar.php",
        "app/Baz.php",
        "app/Util.php",
        "app/Inc.php",
    }


def test_scenario_paths_handles_missing_fields_and_filters_empty() -> None:
    scenario: dict[str, Any] = {"target_path": "app/A.php", "related_paths": []}
    assert _scenario_paths(scenario) == {"app/A.php"}


# ---------------------------------------------------------------------------
# Scenario coverage predicates
# ---------------------------------------------------------------------------


def _scn(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {"id": "S001", "expert": "injection", "target_path": "app/Foo.php"}
    base.update(overrides)
    return base


def test_scenario_covers_path_matches_target_path() -> None:
    assert _scenario_covers_path([_scn()], "app/Foo.php")
    assert not _scenario_covers_path([_scn()], "app/Bar.php")


def test_scenario_covers_path_also_matches_related_paths() -> None:
    scn = _scn(related_paths=["app/Bar.php"])
    assert _scenario_covers_path([scn], "app/Bar.php")


def test_scenario_covers_pair_requires_expert_and_path() -> None:
    scn = _scn()
    assert _scenario_covers_pair([scn], "app/Foo.php", "injection")
    assert not _scenario_covers_pair([scn], "app/Foo.php", "cryptographic-failures")
    assert not _scenario_covers_pair([scn], "app/Bar.php", "injection")


def test_scenario_covers_boundary_by_boundary_id() -> None:
    scn = _scn(boundary_id="B1")
    req = {"boundary_id": "B1", "expert": "injection"}
    assert _scenario_covers_boundary([scn], req)
    req2 = {"boundary_id": "B2", "expert": "injection"}
    assert not _scenario_covers_boundary([scn], req2)


def test_scenario_covers_boundary_by_covered_boundary_ids_list() -> None:
    scn = _scn(covered_boundary_ids=["B1", "B2"])
    req = {"boundary_id": "B2", "expert": "injection"}
    assert _scenario_covers_boundary([scn], req)


def test_scenario_covers_boundary_falls_back_to_recon_item_id() -> None:
    scn = _scn(recon_item_id="R1")
    req = {"recon_item_id": "R1", "expert": "injection"}
    assert _scenario_covers_boundary([scn], req)


def test_scenario_covers_unit_by_routing_unit_id_or_covered_list() -> None:
    direct = _scn(routing_unit_id="U001")
    covered = _scn(id="S002", covered_routing_unit_ids=["U002"])
    assert _scenario_covers_unit([direct], "U001", "injection")
    assert _scenario_covers_unit([covered], "U002", "injection")
    assert not _scenario_covers_unit([direct], "U001", "cryptographic-failures")


# ---------------------------------------------------------------------------
# _validate_decisions
# ---------------------------------------------------------------------------


def test_validate_decisions_rejects_unknown_decision_value() -> None:
    decisions = [{"path": "a.php", "expert": "injection", "decision": "wat", "reason": "x" * 25}]
    errors = _validate_decisions(decisions, scenarios=[], experts=EXPERTS)
    assert any("invalid decision" in e for e in errors)


def test_validate_decisions_requires_path() -> None:
    decisions = [{"decision": "not_applicable", "reason": "x" * 25}]
    errors = _validate_decisions(decisions, scenarios=[], experts=EXPERTS)
    assert any("missing path" in e for e in errors)


def test_validate_decisions_requires_scenario_ids_for_coverage_claims() -> None:
    for decision_value in ("covered_by_scenario", "merged", "scenario"):
        decisions = [{"path": "a.php", "expert": "injection", "decision": decision_value}]
        errors = _validate_decisions(decisions, scenarios=[], experts=EXPERTS)
        assert any("must reference scenario_ids" in e for e in errors), decision_value


def test_validate_decisions_flags_unknown_scenario_id() -> None:
    decisions = [{
        "path": "a.php",
        "expert": "injection",
        "decision": "covered_by_scenario",
        "scenario_ids": ["S999"],
    }]
    scenarios = [_scn()]
    errors = _validate_decisions(decisions, scenarios=scenarios, experts=EXPERTS)
    assert any("references unknown" in e and "S999" in e for e in errors)


def test_validate_decisions_requires_substantive_reason_for_dismissals() -> None:
    # 'not_applicable' is a dismissal — short reason is rejected.
    decisions = [{
        "path": "a.php", "expert": "injection", "decision": "not_applicable", "reason": "no"
    }]
    errors = _validate_decisions(decisions, scenarios=[], experts=EXPERTS)
    assert any("needs a concrete reason" in e for e in errors)


def test_validate_decisions_accepts_wildcard_expert() -> None:
    decisions = [{"path": "a.php", "expert": "*", "decision": "not_applicable", "reason": "x" * 25}]
    errors = _validate_decisions(decisions, scenarios=[], experts=EXPERTS)
    assert errors == []


def test_validate_decisions_rejects_unknown_expert() -> None:
    decisions = [{
        "path": "a.php", "expert": "made-up-expert",
        "decision": "not_applicable", "reason": "x" * 25,
    }]
    errors = _validate_decisions(decisions, scenarios=[], experts=EXPERTS)
    assert any("unknown expert" in e for e in errors)


def test_decisions_constant_lists_every_decision_kind() -> None:
    """The set is consulted by router prompts; lock it in."""
    assert DECISIONS == {
        "scenario", "covered_by_scenario", "merged",
        "not_applicable", "needs_context", "out_of_scope",
    }


# ---------------------------------------------------------------------------
# coverage_errors
# ---------------------------------------------------------------------------


def _write_coverage(path: Path, payload: dict[str, Any]) -> None:
    (path / "recon-output").mkdir(parents=True, exist_ok=True)
    (path / "recon-output" / "coverage-gaps.json").write_text(json.dumps(payload))


def _write_units(path: Path, units: list[dict[str, Any]]) -> None:
    (path / "recon-output").mkdir(parents=True, exist_ok=True)
    (path / "recon-output" / "routing-units.jsonl").write_text(
        "".join(json.dumps(u) + "\n" for u in units)
    )


def test_coverage_errors_flags_uncovered_path(run_dir: Path) -> None:
    _write_coverage(run_dir, {"input_with_sink_or_exposure": [{"path": "app/Untouched.php"}]})
    errors = coverage_errors(run_dir, scenarios=[], coverage_decisions=[])
    assert any("missing path coverage for app/Untouched.php" in e for e in errors)


def test_coverage_errors_path_decision_satisfies_uncovered_path(run_dir: Path) -> None:
    _write_coverage(run_dir, {"input_with_sink_or_exposure": [{"path": "app/Untouched.php"}]})
    decisions = [{
        "path": "app/Untouched.php", "expert": "*",
        "decision": "not_applicable", "reason": "framework-owned, not invocable by users",
    }]
    errors = coverage_errors(run_dir, scenarios=[], coverage_decisions=decisions)
    assert not any("missing path coverage" in e for e in errors)


def test_coverage_errors_flags_unrouted_required_pair(run_dir: Path) -> None:
    _write_coverage(run_dir, {
        "routing_requirements": [{"path": "app/Foo.php", "expert": "injection"}],
    })
    errors = coverage_errors(run_dir, scenarios=[], coverage_decisions=[])
    assert any("missing expert coverage for app/Foo.php -> injection" in e for e in errors)


def test_coverage_errors_satisfied_by_scenario_targeting_the_pair(run_dir: Path) -> None:
    _write_coverage(run_dir, {
        "routing_requirements": [{"path": "app/Foo.php", "expert": "injection"}],
    })
    scn = _scn()  # target_path=app/Foo.php, expert=injection
    errors = coverage_errors(run_dir, scenarios=[scn], coverage_decisions=[])
    assert not any("missing expert coverage" in e for e in errors)


def test_coverage_errors_flags_missing_routing_unit_coverage(run_dir: Path) -> None:
    _write_units(run_dir, [{
        "unit_id": "U001",
        "path": "app/Foo.php",
        "coverage": "mandatory",
        "required_experts": ["injection"],
    }])
    errors = coverage_errors(run_dir, scenarios=[], coverage_decisions=[])
    assert any("missing routing-unit expert coverage for U001" in e for e in errors)


def test_coverage_errors_routing_unit_satisfied_by_scenario_with_unit_id(run_dir: Path) -> None:
    _write_units(run_dir, [{
        "unit_id": "U001",
        "path": "app/Foo.php",
        "coverage": "mandatory",
        "required_experts": ["injection"],
    }])
    scn = _scn(routing_unit_id="U001")
    errors = coverage_errors(run_dir, scenarios=[scn], coverage_decisions=[])
    assert not any("missing routing-unit" in e for e in errors)


# ---------------------------------------------------------------------------
# record_backlog — happy path + key error gates
# ---------------------------------------------------------------------------


def _valid_scenario(scn_id: str = "S001", **overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": scn_id,
        "recon_item_id": "R001",
        "expert": "injection",
        "target_path": "app/Foo.php",
        "proof_question": "Is user input concatenated into a raw SQL query?",
        "evidence_required": ["sink call", "lack of binding"],
        "security_invariant": "Database queries must use parameter binding.",
        "proof_obligations": [
            {"id": "p1", "question": "Is the sink raw?", "evidence_required": "snippet"}
        ],
    }
    base.update(overrides)
    return base


@pytest.fixture()
def patched_run_dir(
    run_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> Path:
    """Redirect ``run_path`` so ``record_backlog`` writes into tmp."""
    monkeypatch.setattr(backlog, "run_path", lambda target, run_id: run_dir)
    return run_dir


def _router_output(scenarios: list[dict[str, Any]], **extras: Any) -> dict[str, Any]:
    payload = {"scenarios": scenarios, "coverage_decisions": [], "coverage_notes": []}
    payload.update(extras)
    return payload


def test_record_backlog_writes_scenario_files_on_happy_path(
    patched_run_dir: Path, tmp_path: Path
) -> None:
    router = tmp_path / "router.json"
    router.write_text(json.dumps(_router_output([_valid_scenario()])))

    result = record_backlog("acme", "demo", router)
    assert [s["id"] for s in result] == ["S001"]

    written = patched_run_dir / "scenarios" / "backlog" / "S001.json"
    assert written.is_file()
    payload = json.loads(written.read_text())
    # DEFAULTS are layered in by record_backlog.
    assert payload["priority"] == "normal"
    assert payload["result_location"] == "scenarios/finished/S001.json"

    index = patched_run_dir / "scenarios" / "index.jsonl"
    assert index.read_text().strip().count("\n") == 0  # one line, no trailing extras

    decisions = patched_run_dir / "scenarios" / "coverage-decisions.json"
    assert json.loads(decisions.read_text())["coverage_decisions"] == []


def test_record_backlog_rejects_unknown_expert(
    patched_run_dir: Path, tmp_path: Path
) -> None:
    router = tmp_path / "router.json"
    router.write_text(json.dumps(_router_output([_valid_scenario(expert="made-up-expert")])))
    with pytest.raises(ValueError, match="Unknown expert"):
        record_backlog("acme", "demo", router)


def test_record_backlog_rejects_duplicate_scenario_id(
    patched_run_dir: Path, tmp_path: Path
) -> None:
    router = tmp_path / "router.json"
    router.write_text(json.dumps(_router_output([
        _valid_scenario("S001"),
        _valid_scenario("S001", target_path="app/Bar.php"),
    ])))
    with pytest.raises(ValueError, match="Duplicate scenario id"):
        record_backlog("acme", "demo", router)


def test_record_backlog_rejects_duplicate_proof_obligation_id(
    patched_run_dir: Path, tmp_path: Path
) -> None:
    scn = _valid_scenario()
    scn["proof_obligations"] = [
        {"id": "p1", "question": "Q1", "evidence_required": "e"},
        {"id": "p1", "question": "Q2", "evidence_required": "e"},
    ]
    router = tmp_path / "router.json"
    router.write_text(json.dumps(_router_output([scn])))
    with pytest.raises(ValueError, match="duplicate proof obligation"):
        record_backlog("acme", "demo", router)


def test_record_backlog_rejects_missing_required_field(
    patched_run_dir: Path, tmp_path: Path
) -> None:
    scn = _valid_scenario()
    scn.pop("security_invariant")
    router = tmp_path / "router.json"
    router.write_text(json.dumps(_router_output([scn])))
    with pytest.raises(ValueError, match="missing: \\['security_invariant'\\]"):
        record_backlog("acme", "demo", router)


def test_record_backlog_surfaces_schema_failure(
    patched_run_dir: Path, tmp_path: Path
) -> None:
    scn = _valid_scenario(id="invalid-id-format")
    router = tmp_path / "router.json"
    router.write_text(json.dumps(_router_output([scn])))
    with pytest.raises(ValueError, match="scenario-schema.json"):
        record_backlog("acme", "demo", router)


def test_record_backlog_surfaces_coverage_gap(
    patched_run_dir: Path, tmp_path: Path
) -> None:
    _write_coverage(patched_run_dir, {
        "routing_requirements": [{"path": "app/Unrelated.php", "expert": "injection"}],
    })
    router = tmp_path / "router.json"
    router.write_text(json.dumps(_router_output([_valid_scenario()])))
    with pytest.raises(ValueError, match="does not cover recon evidence"):
        record_backlog("acme", "demo", router)
