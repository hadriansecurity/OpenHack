#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from whitebox_pentesting_agent.recon import run_recon
from whitebox_pentesting_agent.paths import run_path
from whitebox_pentesting_agent.summary import format_checkpoint


def main():
    parser = argparse.ArgumentParser(description="Run source reconnaissance.")
    parser.add_argument("target")
    parser.add_argument("run_id")
    parser.add_argument("--semgrep", action="store_true", help="Also run bundled Semgrep recon rules.")
    parser.add_argument("--semgrep-config", action="append", default=[], help="Extra Semgrep config path.")
    args = parser.parse_args()
    rows = run_recon(args.target, args.run_id, args.semgrep, args.semgrep_config)
    path = run_path(args.target, args.run_id)
    recon = path / "recon-output"
    artifacts = [recon / name for name in [
        "recon-items.jsonl",
        "routes.jsonl",
        "inputs.jsonl",
        "sinks.jsonl",
        "exposures.jsonl",
        "coverage-gaps.json",
    ]]
    if args.semgrep:
        artifacts.append(recon / "semgrep-results.json")
    source = " plus Semgrep hints" if args.semgrep else ""
    print(format_checkpoint(
        "Run Recon",
        f"Recorded {len(rows)} recon items from lightweight inventories{source}.",
        artifacts=artifacts,
        review="Skim the recon counts and decide whether routing should be prepared.",
        next_command=f"python3 scripts/commands/create-scenarios.py {args.target} {args.run_id}",
    ))


if __name__ == "__main__":
    main()
