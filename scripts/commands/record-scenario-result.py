#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from whitebox_pentesting_agent.paths import run_path
from whitebox_pentesting_agent.results import record_bundle, record_result
from whitebox_pentesting_agent.summary import format_checkpoint, next_step


def main():
    parser = argparse.ArgumentParser(description="Record a scenario result.")
    parser.add_argument("target")
    parser.add_argument("run_id")
    parser.add_argument("scenario_or_bundle")
    parser.add_argument("result_json", nargs="?", type=Path)
    args = parser.parse_args()
    path = run_path(args.target, args.run_id)
    if args.result_json:
        written = record_result(
            args.target, args.run_id, args.scenario_or_bundle, args.result_json
        )
        finished = path / "scenarios" / "finished" / f"{args.scenario_or_bundle}.json"
        artifacts = [finished] + written
    else:
        written = record_bundle(args.target, args.run_id, Path(args.scenario_or_bundle))
        artifacts = [path / "scenarios" / "finished"] + written
    step = next_step(args.target, args.run_id)
    print(format_checkpoint(
        "Record Scenario Result",
        f"Recorded scenario output and wrote {len(written)} finding files.",
        artifacts=artifacts,
        review="Check the result status and any generated finding text before continuing.",
        next_command=step["command"],
    ))


if __name__ == "__main__":
    main()
