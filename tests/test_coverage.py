"""Layer 2: coverage scoring and routing requirement generation.

``coverage.py`` is the biggest single module (608 LOC) and decides which
``(path, expert)`` pairs become mandatory scenarios. A miss here surfaces
as silently dropped attack surface, so these tests pin down the decision
table branch-by-branch.
"""

from __future__ import annotations

from typing import Any

import pytest

from openhack.coverage import (
    MAX_REQUIREMENTS_PER_PATH,
    PRODUCTIVE_CLASSES,
    SUGGESTION_LIMIT,
    _path_class,
    _score_pair,
    _source_or_sink,
    _tokens,
    coverage_opportunities,
    coverage_suggestions,
    routing_requirements,
)


# ---------------------------------------------------------------------------
# Path classification
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path,expected",
    [
        (".ddev/config.yaml", "dev"),
        (".devcontainer/Dockerfile", "dev"),
        ("app/tests/FooTest.php", "test"),
        ("src/__fixtures__/sample.json", "test"),
        ("public/assets/libraries/jquery.js", "asset"),
        (".github/workflows/ci.yml", "ci"),
        ("path/to/.github/workflows/x.yml", "ci"),
        ("package.json", "manifest"),
        ("composer.lock", "manifest"),
        ("requirements.txt", "manifest"),
        ("docs/intro.md", "docs"),
        ("README.md", "docs"),
        ("notes.rst", "docs"),
        ("src/translations/en.yml", "fixture"),
        ("public/assets/js/app.js", "client"),
        ("src/foo.js", "client"),
        ("public/assets/logo.png", "asset"),
        ("public/icon.svg", "asset"),
        ("templates/home.twig", "template"),
        ("config/services.yml", "config"),
        ("settings.xml", "config"),
        ("bin/run", "script"),
        ("scripts/deploy.sh", "script"),
        ("app/Http/Controller.php", "runtime"),
        ("app/bundles/foo/Service.php", "runtime"),
        ("plugins/extra/handler.php", "runtime"),
        ("README", "other"),
    ],
)
def test_path_class(path: str, expected: str) -> None:
    assert _path_class(path) == expected


def test_productive_classes_match_expectations() -> None:
    """Sanity-check the productive set — scoring depends on this membership."""
    assert PRODUCTIVE_CLASSES == {
        "client", "config", "manifest", "runtime", "script", "template"
    }


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------


def test_tokens_drops_short_and_stopwords() -> None:
    out = _tokens("the AND a URL path data 12 abc_def query")
    assert "the" not in out and "and" not in out
    assert "url" not in out  # in STOPWORDS
    assert "path" not in out  # in STOPWORDS
    assert "abc_def" in out  # underscores preserved
    assert "query" in out
    assert "12" not in out  # below length-3 cutoff


def test_tokens_splits_on_non_alphanumeric() -> None:
    assert _tokens("Foo-Bar.baz/Qux") == {"foo", "bar", "baz", "qux"}


# ---------------------------------------------------------------------------
# Pair scoring
# ---------------------------------------------------------------------------


def _pair(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "expert": "injection",
        "path": "app/Foo.php",
        "reason": "test",
        "matched_terms": [],
        "signals": [],
        "kinds": [],
        "evidence": [],
        "interesting": False,
        "path_class": "runtime",
    }
    base.update(overrides)
    return base


def test_score_boundary_mandatory_always_high() -> None:
    pair = _pair(boundary_mandatory=True, strong_terms=["endpoint"])
    confidence, strong, _ = _score_pair(pair)
    assert confidence == "high"
    assert strong == ["endpoint"]


def test_score_supply_chain_on_manifest_is_high() -> None:
    pair = _pair(expert="software-supply-chain-failures", path="package.json")
    confidence, _, reason = _score_pair(pair)
    assert confidence == "high"
    assert "supply-chain" in reason or "Dependency" in reason


def test_score_non_productive_path_class_is_low() -> None:
    pair = _pair(path="public/assets/logo.png")
    confidence, _, reason = _score_pair(pair)
    assert confidence == "low"
    assert "not a runtime attack surface" in reason


def test_score_runtime_without_strong_terms_is_low() -> None:
    pair = _pair(path="app/Generic.php")
    confidence, _, reason = _score_pair(pair)
    assert confidence == "low"
    assert "generic" in reason.lower()


def test_score_runtime_with_strong_terms_but_no_sink_is_suggestion() -> None:
    pair = _pair(path="app/query/Builder.php", interesting=False)
    confidence, strong, _ = _score_pair(pair)
    assert confidence == "suggestion"
    assert "query" in strong


def test_score_runtime_with_strong_terms_and_sink_is_high() -> None:
    pair = _pair(path="app/query/Builder.php", interesting=True)
    confidence, strong, reason = _score_pair(pair)
    assert confidence == "high"
    assert "query" in strong
    assert "source, sink" in reason or "boundary evidence" in reason


def test_source_or_sink_truthy_for_boundary() -> None:
    assert _source_or_sink(_pair(boundary_mandatory=True)) is True
    assert _source_or_sink(_pair(interesting=True)) is True
    assert _source_or_sink(_pair()) is False


# ---------------------------------------------------------------------------
# End-to-end: candidate pair generation from inventory
# ---------------------------------------------------------------------------


def _inv_row(kind: str, path: str, **extra: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "kind": kind,
        "path": path,
        "line": 1,
        "match": [],
        "text": "",
    }
    row.update(extra)
    return row


SELECTED = ["injection", "software-supply-chain-failures"]


def test_routing_requirements_yields_high_confidence_pairs_only() -> None:
    inventory: dict[str, list[dict[str, Any]]] = {
        "inputs": [_inv_row("inputs", "app/QueryHandler.php", match=["query"])],
        "sinks": [_inv_row("sinks", "app/QueryHandler.php", match=["raw"])],
    }
    reqs = routing_requirements(inventory, recon_items=None, selected_experts=SELECTED)
    assert reqs, "expected at least one high-confidence requirement"
    for req in reqs:
        assert req["confidence"] == "high"
        # Public pairs have the private 'interesting' flag stripped.
        assert "interesting" not in req
        assert req["requirement"].startswith("Create a scenario")


def test_routing_requirements_skips_non_productive_paths() -> None:
    inventory: dict[str, list[dict[str, Any]]] = {
        "inputs": [_inv_row("inputs", "tests/QueryTest.php", match=["query"])],
        "sinks": [_inv_row("sinks", "tests/QueryTest.php", match=["raw"])],
    }
    reqs = routing_requirements(inventory, recon_items=None, selected_experts=SELECTED)
    assert reqs == []


def test_routing_requirements_promotes_supply_chain_for_manifest() -> None:
    inventory: dict[str, list[dict[str, Any]]] = {
        "inputs": [_inv_row("inputs", "package.json", match=["dependency"])],
    }
    reqs = routing_requirements(
        inventory, recon_items=None, selected_experts=["software-supply-chain-failures"]
    )
    paths = {req["path"] for req in reqs}
    assert "package.json" in paths


def test_coverage_opportunities_groups_by_expert() -> None:
    inventory: dict[str, list[dict[str, Any]]] = {
        "inputs": [
            _inv_row("inputs", "app/QueryHandler.php", match=["query"]),
            _inv_row("inputs", "app/ShellRunner.php", match=["shell", "exec"]),
        ],
        "sinks": [
            _inv_row("sinks", "app/QueryHandler.php", match=["raw"]),
            _inv_row("sinks", "app/ShellRunner.php", match=["exec"]),
        ],
    }
    opps = coverage_opportunities(
        inventory, recon_items=None, selected_experts=["injection"]
    )
    assert len(opps) == 1
    [opp] = opps
    assert opp["expert"] == "injection"
    assert opp["candidate_paths"] >= 2
    paths = {ex["path"] for ex in opp["examples"]}
    assert {"app/QueryHandler.php", "app/ShellRunner.php"} <= paths


def test_coverage_suggestions_skip_required_pairs() -> None:
    """Items already represented in ``required_keys`` must not double-count."""
    inventory: dict[str, list[dict[str, Any]]] = {
        "inputs": [_inv_row("inputs", "app/QueryHandler.php", match=["query"])],
        "sinks": [_inv_row("sinks", "app/QueryHandler.php", match=["raw"])],
    }
    required = {("app/QueryHandler.php", "injection")}
    sugs = coverage_suggestions(
        inventory,
        recon_items=None,
        required_keys=required,
        selected_experts=["injection"],
    )
    assert all(s["path"] != "app/QueryHandler.php" for s in sugs)


def test_constants_have_expected_values() -> None:
    """Lock in the public limits referenced from docs/AGENTS.md."""
    assert MAX_REQUIREMENTS_PER_PATH == 4
    assert SUGGESTION_LIMIT == 500
