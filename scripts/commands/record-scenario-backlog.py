#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from whitebox_pentesting_agent.backlog import record_backlog
from whitebox_pentesting_agent.paths import run_path
from whitebox_pentesting_agent.summary import format_checkpoint


def main():
    parser = argparse.ArgumentParser(description="Record scenario-router output.")
    parser.add_argument("target")
    parser.add_argument("run_id")
    parser.add_argument("router_result_json", type=Path)
    args = parser.parse_args()
    scenarios = record_backlog(args.target, args.run_id, args.router_result_json)
    path = run_path(args.target, args.run_id)
    print(format_checkpoint(
        "Record Scenario Backlog",
        f"Recorded {len(scenarios)} scenario assignments from router output.",
        artifacts=[path / "scenarios" / "index.jsonl", path / "scenarios" / "backlog"],
        review=(
            "Confirm backlog size, coverage decisions, and expert fan-out, then "
            "ask whether to run all recorded scenarios as one expert-review batch."
        ),
        next_note=(
            "After approval, render the backlog prompts, review every unfinished "
            "scenario, and record the results as a bundle."
        ),
    ))


if __name__ == "__main__":
    main()
