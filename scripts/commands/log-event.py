#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from whitebox_pentesting_agent.log import emit
from whitebox_pentesting_agent.paths import run_path


def main():
    parser = argparse.ArgumentParser(description="Append a run log event.")
    parser.add_argument("target")
    parser.add_argument("run_id")
    parser.add_argument("actor")
    parser.add_argument("status")
    parser.add_argument("summary")
    args = parser.parse_args()
    emit(run_path(args.target, args.run_id), args.actor, args.status, args.summary)


if __name__ == "__main__":
    main()
