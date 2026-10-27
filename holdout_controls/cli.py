"""holdout-controls run ENV [--task ID ...] [--json PATH]

Exit codes: 0 no findings, 1 at least one finding, 2 an error (bad arguments, or a run crashed).
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from . import __version__
from .adapter import load
from .runner import run


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="holdout-controls",
                                     description="Run scripted controls against an RL environment's grader.")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    p_run = sub.add_parser("run", help="run the controls on every task")
    p_run.add_argument("env", help="the environment, as module:attribute")
    p_run.add_argument("--task", action="append", help="only this task (repeatable)")
    p_run.add_argument("--json", metavar="PATH", help="also write the report as JSON")
    args = parser.parse_args(argv)

    try:
        env = load(args.env)
    except (ImportError, AttributeError, TypeError, ValueError) as exc:
        print(f"holdout-controls: {exc}", file=sys.stderr)
        return 2
    report = run(env, tasks=args.task)

    for r in report.results:
        reward = "-" if r.reward is None else f"{r.reward:g}"
        line = f"{r.status:8} {r.task:30} {r.control:12} reward={reward}"
        print(line + (f"  ({r.detail.splitlines()[-1]})" if r.detail else ""))
    counts = report.to_dict()["counts"]
    print(f"\n{counts['finding']} finding(s), {counts['error']} error(s), "
          f"{counts['ok']} ok, {counts['skipped']} skipped")

    if args.json:
        with open(args.json, "w") as f:
            json.dump(report.to_dict(), f, indent=2)
    if report.errors:
        return 2
    return 1 if report.findings else 0


if __name__ == "__main__":
    sys.exit(main())
