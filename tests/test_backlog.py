"""Layer 2: scenario backlog validation and write-out.

Tests prefer the public entry points (``coverage_errors``, ``record_backlog``)
over private predicates. The private helpers are still exercised — just
through the API a real caller uses.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from openhack import backlog
from openhack.backlog import coverage_errors, record_backlog


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def _scn(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {"id": "S001", "expert": "injection", "target_path": "app/Foo.php"}
    base.update(overrides)
    return base


def _write_coverage(path: Path, payload: dict[str, Any]) -> None:
    (path / "recon-output").mkdir(parents=True, exist_ok=True)
    (path / "recon-output" / "coverage-gaps.json").write_text(json.dumps(payload))


def _write_units(path: Path, units: list[dict[str, Any]]) -> None:
    (path / "recon-output").mkdir(parents=True, exist_ok=True)
    (path / "recon-output" / "routing-units.jsonl").write_text(
        "".join(json.dumps(u) + "\n" for u in units)
    )


# ---------------------------------------------------------------------------
# coverage_errors — exercises the scenario/decision predicates as a side effect
# ---------------------------------------------------------------------------


def test_path_requirement_flagged_when_no_scenario_covers_it(run_dir: Path) -> None:
    _write_coverage(run_dir, {"input_with_sink_or_exposure": [{"path": "app/Untouched.php"}]})
    errors = coverage_errors(run_dir, scenarios=[], coverage_decisions=[])
    assert any("missing path coverage for app/Untouched.php" in e for e in errors)


def test_path_requirement_satisfied_by_target_path(run_dir: Path) -> None:
    _write_coverage(run_dir, {"input_with_sink_or_exposure": [{"path": "app/Foo.php"}]})
    errors = coverage_errors(run_dir, scenarios=[_scn()], coverage_decisions=[])
    assert not any("missing path coverage" in e for e in errors)


def test_path_requirement_satisfied_by_related_paths(run_dir: Path) -> None:
    """``_scenario_paths`` must consider ``related_paths`` as well as ``target_path``."""
    _write_coverage(run_dir, {"input_with_sink_or_exposure": [{"path": "app/Bar.php"}]})
    scn = _scn(related_paths=["app/Bar.php"])
    errors = coverage_errors(run_dir, scenarios=[scn], coverage_decisions=[])
    assert not any("missing path coverage" in e for e in errors)


def test_path_requirement_satisfied_by_covered_paths_list(run_dir: Path) -> None:
    _write_coverage(run_dir, {"input_with_sink_or_exposure": [{"path": "app/Inc.php"}]})
    scn = _scn(covered_paths=["app/Inc.php"])
    errors = coverage_errors(run_dir, scenarios=[scn], coverage_decisions=[])
    assert not any("missing path coverage" in e for e in errors)


def test_path_requirement_satisfied_by_path_level_decision(run_dir: Path) -> None:
    _write_coverage(run_dir, {"input_with_sink_or_exposure": [{"path": "app/Untouched.php"}]})
    decisions = [{
        "path": "app/Untouched.php", "expert": "*",
        "decision": "not_applicable", "reason": "framework-owned, not invocable by users",
    }]
    errors = coverage_errors(run_dir, scenarios=[], coverage_decisions=decisions)
    assert not any("missing path coverage" in e for e in errors)


def test_pair_requirement_flagged_when_expert_mismatches(run_dir: Path) -> None:
    _write_coverage(run_dir, {
        "routing_requirements": [{"path": "app/Foo.php", "expert": "injection"}],
    })
    # Scenario covers the path but with a different expert.
    scn = _scn(expert="cryptographic-failures")
    errors = coverage_errors(run_dir, scenarios=[scn], coverage_decisions=[])
    assert any("missing expert coverage for app/Foo.php -> injection" in e for e in errors)


def test_pair_requirement_satisfied_by_matching_scenario(run_dir: Path) -> None:
    _write_coverage(run_dir, {
        "routing_requirements": [{"path": "app/Foo.php", "expert": "injection"}],
    })
    errors = coverage_errors(run_dir, scenarios=[_scn()], coverage_decisions=[])
    assert not any("missing expert coverage" in e for e in errors)


def test_routing_unit_satisfied_by_scenario_with_unit_id(run_dir: Path) -> None:
    _write_units(run_dir, [{
        "unit_id": "U001",
        "path": "app/Foo.php",
        "coverage": "mandatory",
        "required_experts": ["injection"],
    }])
    scn = _scn(routing_unit_id="U001")
    errors = coverage_errors(run_dir, scenarios=[scn], coverage_decisions=[])
    assert not any("missing routing-unit" in e for e in errors)


def test_routing_unit_satisfied_by_covered_routing_unit_ids(run_dir: Path) -> None:
    """A scenario can claim coverage over a unit it isn't the primary owner of."""
    _write_units(run_dir, [{
        "unit_id": "U002",
        "path": "app/Foo.php",
        "coverage": "mandatory",
        "required_experts": ["injection"],
    }])
    scn = _scn(routing_unit_id="U001", covered_routing_unit_ids=["U002"])
    errors = coverage_errors(run_dir, scenarios=[scn], coverage_decisions=[])
    assert not any("missing routing-unit" in e for e in errors)


def test_routing_unit_flagged_when_no_scenario_or_decision(run_dir: Path) -> None:
    _write_units(run_dir, [{
        "unit_id": "U001",
        "path": "app/Foo.php",
        "coverage": "mandatory",
        "required_experts": ["injection"],
    }])
    errors = coverage_errors(run_dir, scenarios=[], coverage_decisions=[])
    assert any("missing routing-unit expert coverage for U001" in e for e in errors)


# ---------------------------------------------------------------------------
# Boundary-requirement coverage (item 4 in review)
# ---------------------------------------------------------------------------


def _boundary_req(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "path": "app/Api.php",
        "expert": "injection",
        "boundary_id": "B1",
        "endpoint": "/api/run",
    }
    base.update(overrides)
    return base


def test_boundary_requirement_flagged_without_scenario_or_decision(run_dir: Path) -> None:
    _write_coverage(run_dir, {"boundary_requirements": [_boundary_req()]})
    errors = coverage_errors(run_dir, scenarios=[], coverage_decisions=[])
    assert any(
        "missing request-boundary coverage for app/Api.php -> injection -> /api/run" in e
        for e in errors
    )


def test_boundary_requirement_satisfied_by_scenario_with_boundary_id(run_dir: Path) -> None:
    _write_coverage(run_dir, {"boundary_requirements": [_boundary_req()]})
    scn = _scn(boundary_id="B1")
    errors = coverage_errors(run_dir, scenarios=[scn], coverage_decisions=[])
    assert not any("missing request-boundary" in e for e in errors)


def test_boundary_requirement_satisfied_by_covered_boundary_ids_list(run_dir: Path) -> None:
    _write_coverage(run_dir, {"boundary_requirements": [_boundary_req()]})
    scn = _scn(covered_boundary_ids=["B1", "B2"])
    errors = coverage_errors(run_dir, scenarios=[scn], coverage_decisions=[])
    assert not any("missing request-boundary" in e for e in errors)


def test_boundary_requirement_satisfied_by_recon_item_id_fallback(run_dir: Path) -> None:
    """Boundary req without scenario boundary_id can be matched by recon_item_id."""
    _write_coverage(run_dir, {
        "boundary_requirements": [_boundary_req(recon_item_id="R1")],
    })
    scn = _scn(recon_item_id="R1")
    errors = coverage_errors(run_dir, scenarios=[scn], coverage_decisions=[])
    assert not any("missing request-boundary" in e for e in errors)


def test_boundary_requirement_satisfied_by_boundary_id_decision(run_dir: Path) -> None:
    _write_coverage(run_dir, {"boundary_requirements": [_boundary_req()]})
    decisions = [{
        "path": "app/Api.php", "expert": "injection", "boundary_id": "B1",
        "decision": "not_applicable", "reason": "internal admin endpoint behind VPN",
    }]
    errors = coverage_errors(run_dir, scenarios=[], coverage_decisions=decisions)
    assert not any("missing request-boundary" in e for e in errors)


def test_boundary_decision_without_boundary_id_does_not_satisfy(run_dir: Path) -> None:
    """``_has_boundary_decision`` requires the boundary_id to match exactly."""
    _write_coverage(run_dir, {"boundary_requirements": [_boundary_req()]})
    decisions = [{
        "path": "app/Api.php", "expert": "injection",
        "decision": "not_applicable", "reason": "internal admin endpoint behind VPN",
    }]
    errors = coverage_errors(run_dir, scenarios=[], coverage_decisions=decisions)
    assert any("missing request-boundary" in e for e in errors)


# ---------------------------------------------------------------------------
# Decision validation (exercised through coverage_errors)
# ---------------------------------------------------------------------------


def test_decision_with_unknown_value_is_flagged(run_dir: Path) -> None:
    decisions = [{"path": "a.php", "expert": "injection", "decision": "wat", "reason": "x" * 25}]
    errors = coverage_errors(run_dir, scenarios=[], coverage_decisions=decisions)
    assert any("invalid decision" in e for e in errors)


def test_decision_missing_path_is_flagged(run_dir: Path) -> None:
    decisions = [{"decision": "not_applicable", "reason": "x" * 25}]
    errors = coverage_errors(run_dir, scenarios=[], coverage_decisions=decisions)
    assert any("missing path" in e for e in errors)


@pytest.mark.parametrize("decision_value", ["covered_by_scenario", "merged", "scenario"])
def test_coverage_claim_decision_requires_scenario_ids(
    run_dir: Path, decision_value: str
) -> None:
    decisions = [{"path": "a.php", "expert": "injection", "decision": decision_value}]
    errors = coverage_errors(run_dir, scenarios=[], coverage_decisions=decisions)
    assert any("must reference scenario_ids" in e for e in errors)


def test_decision_referencing_unknown_scenario_is_flagged(run_dir: Path) -> None:
    decisions = [{
        "path": "a.php", "expert": "injection",
        "decision": "covered_by_scenario", "scenario_ids": ["S999"],
    }]
    errors = coverage_errors(run_dir, scenarios=[_scn()], coverage_decisions=decisions)
    assert any("references unknown" in e and "S999" in e for e in errors)


def test_dismissal_decision_requires_substantive_reason(run_dir: Path) -> None:
    decisions = [{
        "path": "a.php", "expert": "injection", "decision": "not_applicable", "reason": "no"
    }]
    errors = coverage_errors(run_dir, scenarios=[], coverage_decisions=decisions)
    assert any("needs a concrete reason" in e for e in errors)


def test_decision_with_wildcard_expert_is_accepted(run_dir: Path) -> None:
    decisions = [{
        "path": "a.php", "expert": "*",
        "decision": "not_applicable", "reason": "x" * 25,
    }]
    errors = coverage_errors(run_dir, scenarios=[], coverage_decisions=decisions)
    assert not any("invalid decision" in e or "unknown expert" in e for e in errors)


def test_decision_with_unknown_expert_is_flagged(run_dir: Path) -> None:
    decisions = [{
        "path": "a.php", "expert": "made-up-expert",
        "decision": "not_applicable", "reason": "x" * 25,
    }]
    errors = coverage_errors(run_dir, scenarios=[], coverage_decisions=decisions)
    assert any("unknown expert" in e for e in errors)


# ---------------------------------------------------------------------------
# record_backlog — full pipeline including emit() log + scope check
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
def patched_run_dir(run_dir: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
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
    payload = json.loads(written.read_text())
    assert payload["priority"] == "normal"  # DEFAULTS layered in
    assert payload["result_location"] == "scenarios/finished/S001.json"

    index = patched_run_dir / "scenarios" / "index.jsonl"
    assert index.read_text().strip().count("\n") == 0  # one line, no trailing extras


def test_record_backlog_emits_audit_event(
    patched_run_dir: Path, tmp_path: Path
) -> None:
    """The recorder must log a ``scenario-router/complete`` event for auditing."""
    router = tmp_path / "router.json"
    router.write_text(json.dumps(_router_output([_valid_scenario()])))
    record_backlog("acme", "demo", router)

    events = patched_run_dir / "logs" / "events.jsonl"
    assert events.is_file()
    lines = [json.loads(line) for line in events.read_text().splitlines() if line.strip()]
    assert any(
        e.get("actor") == "scenario-router" and e.get("status") == "complete"
        for e in lines
    )


def test_record_backlog_rejects_scenario_using_unselected_expert(
    patched_run_dir: Path, tmp_path: Path
) -> None:
    """A run-config that restricts experts must block out-of-scope scenarios."""
    (patched_run_dir / "run-config.yaml").write_text(
        'expert_scope:\n  mode: "selected"\n  experts:\n    - "injection"\n'
    )
    scn = _valid_scenario(expert="broken-access-control")
    router = tmp_path / "router.json"
    router.write_text(json.dumps(_router_output([scn])))
    with pytest.raises(ValueError, match="uses unselected expert"):
        record_backlog("acme", "demo", router)


def test_record_backlog_accepts_scenario_with_selected_expert(
    patched_run_dir: Path, tmp_path: Path
) -> None:
    (patched_run_dir / "run-config.yaml").write_text(
        'expert_scope:\n  mode: "selected"\n  experts:\n    - "injection"\n'
    )
    router = tmp_path / "router.json"
    router.write_text(json.dumps(_router_output([_valid_scenario()])))
    result = record_backlog("acme", "demo", router)
    assert [s["id"] for s in result] == ["S001"]


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
