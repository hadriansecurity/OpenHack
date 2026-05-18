#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from whitebox_pentesting_agent.summary import format_checkpoint, next_step
from whitebox_pentesting_agent.triage import record_triage


def main():
    parser = argparse.ArgumentParser(description="Record a finding triage result.")
    parser.add_argument("target")
    parser.add_argument("run_id")
    parser.add_argument("candidate_id")
    parser.add_argument("triage_json", type=Path)
    args = parser.parse_args()
    written = record_triage(args.target, args.run_id, args.candidate_id, args.triage_json)
    step = next_step(args.target, args.run_id)
    print(format_checkpoint(
        "Record Finding Triage",
        f"Recorded triage for {args.candidate_id}.",
        artifacts=written,
        review="Accepted or downgraded decisions are now materialized as final findings.",
        next_command=step["command"],
    ))


if __name__ == "__main__":
    main()
