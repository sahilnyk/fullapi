"""CLI entry point — thin dispatch for `gen` and `check`."""

import argparse
import sys
from pathlib import Path

from fullapi import __version__
from fullapi.spec import load_spec, SpecError
from fullapi.generate import write
from fullapi.check import run_check, CheckError

DEFAULT_SPEC = "api.yaml"


def main() -> None:
    parser = argparse.ArgumentParser(prog="fullapi", description="Spec-driven FastAPI.")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("gen", help="Generate the project from the spec")
    gen.add_argument("spec", nargs="?", default=DEFAULT_SPEC, help="Spec file (default: api.yaml)")
    gen.add_argument("-o", "--out", default=".", help="Output directory (default: .)")

    chk = sub.add_parser("check", help="Check the live app against the spec")
    chk.add_argument("spec", nargs="?", default=DEFAULT_SPEC, help="Spec file (default: api.yaml)")
    chk.add_argument("--app", default="app.main:app", help="App import path (default: app.main:app)")

    args = parser.parse_args()
    {"gen": _gen, "check": _check}[args.command](args)


def _load(spec_path: str):
    try:
        return load_spec(Path(spec_path))
    except SpecError as exc:
        sys.exit(f"spec error: {exc}")


def _gen(args) -> None:
    spec = _load(args.spec)
    written = write(spec, Path(args.out))
    root = Path(args.out).resolve()
    for path in written:
        print(path.resolve().relative_to(root))
    print(f"\n{len(written)} files written")


def _check(args) -> None:
    spec = _load(args.spec)
    try:
        result = run_check(spec, args.app)
    except CheckError as exc:
        sys.exit(f"check error: {exc}")

    if result.ok:
        print("ok — app matches spec")
        return
    for change in result.breaking:
        print(f"breaking: {change.detail}")
    sys.exit(f"\n{len(result.breaking)} breaking change(s)")


if __name__ == "__main__":
    main()
