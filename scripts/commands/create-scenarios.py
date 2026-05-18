#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from whitebox_pentesting_agent.scenarios import prepare_scenario_router
from whitebox_pentesting_agent.summary import format_checkpoint


def main():
    parser = argparse.ArgumentParser(description="Prepare scenario-router agent prompt.")
    parser.add_argument("target")
    parser.add_argument("run_id")
    args = parser.parse_args()
    prompt = prepare_scenario_router(args.target, args.run_id)
    print(format_checkpoint(
        "Prepare Scenario Routing",
        "Wrote the scenario-router prompt from recon evidence and expert manifests.",
        artifacts=[prompt],
        review="Read the prompt size and routing scope before asking the router to answer.",
        next_note="Have the scenario-router produce JSON with a top-level scenarios array.",
        next_command=f"python3 scripts/commands/record-scenario-backlog.py {args.target} {args.run_id} router-result.json",
    ))


if __name__ == "__main__":
    main()
