#!/usr/bin/env python3
"""Compatibility entry point for running the checked-in tests with pytest."""

import argparse
import subprocess
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--verbosity", type=int, choices=(1, 2, 3), default=2)
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-l", "--list", action="store_true", help="Collect tests only")
    parser.add_argument("-m", "--module", help="Select tests/test_<module>.py")
    parser.add_argument("-c", "--coverage", action="store_true")
    parser.add_argument("-i", "--env-info", action="store_true")
    parser.add_argument(
        "-e",
        "--develop",
        "-s",
        "--skip-failing",
        "-o",
        "--only-successful",
        "-f",
        "--fix-imports",
        dest="retired",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args(argv)
    if args.retired:
        parser.error(
            "Test rewriting, failure-based filtering, and environment installation "
            "were retired. Install the dev extras explicitly and use pytest's "
            "collection and selection options."
        )

    tests = Path(__file__).resolve().parent
    target = tests
    if args.module is not None:
        if not args.module.isidentifier():
            parser.error("Use a test module name such as document")
        target = tests / f"test_{args.module}.py"
        if not target.is_file():
            parser.error(f"No test module named {args.module}")

    command = [sys.executable, "-m", "pytest"]
    if args.env_info:
        print(f"Python {sys.version} ({sys.executable})", flush=True)
        version = subprocess.run(
            [*command, "--version"],
            cwd=tests.parent,
            stdin=subprocess.DEVNULL,
            check=False,
        )
        if version.returncode or not args.list:
            return version.returncode

    if args.debug or args.verbosity == 3:
        command.extend(["-vvs", "--showlocals", "--no-header", "--tb=native"])
    elif args.verbosity == 2:
        command.append("-v")
    if args.coverage:
        command.extend(["--cov=mdp", "--cov-report=term", "--cov-report=html"])
    if args.list:
        command.append("--collect-only")

    return subprocess.run(
        [*command, str(target)],
        cwd=tests.parent,
        stdin=subprocess.DEVNULL,
        check=False,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
