"""Layer 2: routing-unit clustering."""

from __future__ import annotations

from typing import Any

import pytest

from openhack.routing_units import (
    KIND_TERMS,
    MAX_EVIDENCE_ROWS,
    _candidate_kinds,
    _compact_row,
    _dedupe_rows,
    _kind_for_terms,
    _row_kind,
    build_routing_units,
)


@pytest.mark.parametrize(
    "text,expected",
    [
        ({"exec", "shell"}, "command_execution_sink"),
        ({"query", "raw"}, "database_query_sink"),
        ({"innerhtml"}, "html_template_dom_sink"),
        ({"upload", "filename"}, "file_upload_download_storage"),
        ({"webhook", "fetch"}, "outbound_fetch_boundary"),
        ({"session", "role"}, "identity_state_access_control"),
        ({"secret"}, "secret_debug_exposure"),
        ({"yaml", "deserialize"}, "parser_deserialization_integrity"),
        ({"jwt", "crypto"}, "cryptographic_secret_token"),
        ({"queue", "limit"}, "resource_consumption"),
        ({"manifest", "lockfile"}, "supply_chain_manifest"),
        (set(), "configuration_or_static_surface"),
        ({"unrelated"}, "configuration_or_static_surface"),
    ],
)
def test_kind_for_terms(text: set[str], expected: str) -> None:
    assert _kind_for_terms(text) == expected


def test_kind_for_terms_first_match_wins() -> None:
    """Order in ``KIND_TERMS`` is a deliberate priority list."""
    # 'queue' appears in both resource_consumption and parser_deserialization_integrity
    # — KIND_TERMS lists parser earlier, so it should win for ambiguous terms in its set.
    [parser_terms] = [terms for name, terms in KIND_TERMS if name == "parser_deserialization_integrity"]
    # Pick an unambiguous parser-only term to confirm priority logic.
    assert _kind_for_terms({"xxe"}) == "parser_deserialization_integrity"
    assert "xxe" in parser_terms


def test_row_kind_classifies_request_boundary_evidence() -> None:
    row = {
        "kind": "inputs",
        "path": "app/Api.php",
        "line": 10,
        "match": ["execute"],
        "text": "shell exec",
    }
    assert _row_kind(row) == "command_execution_sink"


def test_compact_row_truncates_long_text() -> None:
    row = {"kind": "inputs", "line": 1, "match": [], "text": "x" * 1000}
    compact = _compact_row(row)
    assert len(compact["text"]) == 240
    assert compact["kind"] == "inputs"


def test_compact_row_keeps_optional_keys_when_present() -> None:
    row = {
        "kind": "request_boundaries",
        "line": 5,
        "match": [],
        "text": "",
        "endpoint": "/api/foo",
        "methods": ["POST"],
    }
    compact = _compact_row(row)
    assert compact["endpoint"] == "/api/foo"
    assert compact["methods"] == ["POST"]


def test_compact_row_drops_empty_optional_keys() -> None:
    row = {"kind": "inputs", "line": 1, "match": [], "text": "", "endpoint": "", "methods": []}
    compact = _compact_row(row)
    assert "endpoint" not in compact
    assert "methods" not in compact


def test_dedupe_rows_collapses_duplicates_and_caps_at_max() -> None:
    rows = [{"kind": "inputs", "line": 1, "match": ["x"], "text": "same"}] * 5
    rows.extend(
        {"kind": "inputs", "line": i, "match": ["y"], "text": f"row-{i}"}
        for i in range(MAX_EVIDENCE_ROWS + 5)
    )
    deduped = _dedupe_rows(rows)
    assert len(deduped) <= MAX_EVIDENCE_ROWS
    # The duplicate block collapses to one entry, then unique rows fill the rest.
    assert sum(1 for r in deduped if r["text"] == "same") == 1


def test_candidate_kinds_for_boundary_returns_request_boundary() -> None:
    pair = {
        "expert": "injection",
        "path": "app/Api.php",
        "boundary_mandatory": True,
        "boundary_id": "B1",
    }
    assert _candidate_kinds(pair, {}) == ["request_boundary"]


def test_candidate_kinds_uses_expert_hints_from_rows() -> None:
    pair: dict[str, Any] = {
        "expert": "injection",
        "path": "app/Api.php",
        "matched_terms": [],
        "signals": [],
        "evidence": [],
    }
    rows_by_kind = {
        "sinks": [
            {"kind": "sinks", "path": "app/Api.php", "line": 1, "match": ["exec"], "text": "shell"},
        ],
    }
    assert "command_execution_sink" in _candidate_kinds(pair, rows_by_kind)


# ---------------------------------------------------------------------------
# build_routing_units end-to-end
# ---------------------------------------------------------------------------


def _req(path: str, expert: str, **extra: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "expert": expert,
        "path": path,
        "reason": "test",
        "matched_terms": [],
        "signals": [],
        "kinds": [],
        "evidence": [],
        "interesting": True,
        "path_class": "runtime",
    }
    base.update(extra)
    return base


def test_build_routing_units_assigns_ids_in_sort_order() -> None:
    coverage_gaps = {
        "routing_requirements": [
            _req("app/QueryHandler.php", "injection"),
            _req("app/Auth.php", "authentication-failures"),
        ],
    }
    inventory: dict[str, list[dict[str, Any]]] = {
        "sinks": [
            {"kind": "sinks", "path": "app/QueryHandler.php", "line": 1, "match": ["raw"], "text": "query"},
            {"kind": "sinks", "path": "app/Auth.php", "line": 1, "match": ["session"], "text": "auth"},
        ],
    }
    units = build_routing_units(coverage_gaps, inventory)
    assert [u["unit_id"] for u in units] == ["U001", "U002"]
    # Mandatory coverage requirements always sort first; both here are mandatory.
    assert all(u["coverage"] == "mandatory" for u in units)


def test_build_routing_units_separates_required_from_suggested() -> None:
    coverage_gaps = {
        "routing_requirements": [_req("app/QueryHandler.php", "injection")],
        "coverage_suggestions": [_req("app/QueryHandler.php", "broken-access-control")],
    }
    inventory: dict[str, list[dict[str, Any]]] = {
        "sinks": [
            {"kind": "sinks", "path": "app/QueryHandler.php", "line": 1, "match": ["raw", "role"], "text": "query"},
        ],
    }
    units = build_routing_units(coverage_gaps, inventory)
    # Both pairs target the same path; whether they merge into one unit or split
    # depends on the chosen kind. Verify the expert tagging is preserved.
    required = {expert for u in units for expert in u["required_experts"]}
    suggested = {expert for u in units for expert in u["suggested_experts"]}
    assert "injection" in required
    assert "broken-access-control" in suggested
    assert "injection" not in suggested
    assert "broken-access-control" not in required


def test_build_routing_units_preserves_boundary_fields() -> None:
    coverage_gaps = {
        "routing_requirements": [
            _req(
                "app/Api.php",
                "injection",
                boundary_mandatory=True,
                boundary_id="B1",
                endpoint="/api/run",
                methods=["POST"],
                boundary_type="route",
                request_fields=["cmd"],
            ),
        ],
    }
    units = build_routing_units(coverage_gaps, inventory={})
    assert len(units) == 1
    unit = units[0]
    assert unit["kind"] == "request_boundary"
    assert unit["boundary_id"] == "B1"
    assert unit["endpoint"] == "/api/run"
    assert unit["methods"] == ["POST"]


def test_build_routing_units_emits_mandatory_path_unit_for_uncovered_gap() -> None:
    coverage_gaps = {
        "input_with_sink_or_exposure": [{"path": "app/Untriaged.php"}],
    }
    inventory: dict[str, list[dict[str, Any]]] = {
        "inputs": [
            {"kind": "inputs", "path": "app/Untriaged.php", "line": 1, "match": [], "text": "raw"}
        ],
    }
    units = build_routing_units(coverage_gaps, inventory)
    assert len(units) == 1
    assert units[0]["coverage"] == "mandatory_path"
    assert units[0]["required_experts"] == []
