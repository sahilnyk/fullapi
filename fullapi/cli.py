"""CLI entry point — thin dispatch for `gen` and `check`."""

import argparse
import os
import sys
from pathlib import Path

from fullapi import __version__
from fullapi.spec import load_spec, SpecError
from fullapi.generate import write
from fullapi.check import run_check, CheckError

DEFAULT_SPEC = "api.yaml"
DEFAULT_APP = "app.main:app"

STARTER_SPEC = """\
name: my_api
database: sqlite   # none | sqlite | postgres
# auth: jwt         # uncomment to require JWT auth on every resource

resources:
  - name: product
    fields:
      title: str
      price: float
      note: str?    # trailing ? = optional field
    # auth: true    # uncomment to protect just this resource
"""


def _use_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return sys.stdout.isatty()


class _Style:
    def __init__(self, enabled: bool):
        self.enabled = enabled

    def _wrap(self, code: str, text: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.enabled else text

    def dim(self, t: str) -> str:   return self._wrap("2", t)
    def bold(self, t: str) -> str:  return self._wrap("1", t)
    def green(self, t: str) -> str: return self._wrap("32", t)
    def red(self, t: str) -> str:   return self._wrap("31", t)
    def cyan(self, t: str) -> str:  return self._wrap("36", t)
    def yellow(self, t: str) -> str: return self._wrap("33", t)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="fullapi",
        description="Spec-driven FastAPI — generate a project from api.yaml and enforce it in CI.",
    )
    parser.add_argument("--version", action="version", version=f"fullapi {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="{init,gen,check}", required=True)

    init = sub.add_parser("init", help="write a starter api.yaml")
    init.add_argument("spec", nargs="?", default=DEFAULT_SPEC,
                      help=f"spec file to write (default: {DEFAULT_SPEC})")

    gen = sub.add_parser("gen", help="generate the project from api.yaml")
    gen.add_argument("spec", nargs="?", default=DEFAULT_SPEC,
                     help=f"spec file (default: {DEFAULT_SPEC})")
    gen.add_argument("-o", "--out", default=".", help="output directory (default: .)")

    chk = sub.add_parser("check", help="fail CI when the live app drifts from api.yaml")
    chk.add_argument("spec", nargs="?", default=DEFAULT_SPEC,
                     help=f"spec file (default: {DEFAULT_SPEC})")
    chk.add_argument("--app", default=DEFAULT_APP,
                     help=f"app import path (default: {DEFAULT_APP})")
    chk.add_argument("-v", "--verbose", action="store_true",
                     help="also list safe (non-breaking) changes")

    args = parser.parse_args()
    style = _Style(_use_color())
    {"init": _init, "gen": _gen, "check": _check}[args.command](args, style)


def _init(args, style: "_Style") -> None:
    path = Path(args.spec)
    if path.exists():
        sys.exit(f"{style.red('error:')} {path} already exists")
    path.write_text(STARTER_SPEC)
    print(f"{style.green('done')} — wrote {style.cyan(str(path))}")


def _load(spec_path: str, style: "_Style"):
    try:
        return load_spec(Path(spec_path))
    except SpecError as exc:
        sys.exit(f"{style.red('spec error:')} {exc}")


def _gen(args, style: "_Style") -> None:
    spec = _load(args.spec, style)
    written = write(spec, Path(args.out))
    root = Path(args.out).resolve()
    for path in written:
        rel = path.resolve().relative_to(root)
        print(f"  {style.dim('+')} {rel}")
    total = style.bold(str(len(written)))
    print(f"\n{style.green('done')} — {total} files written to {style.cyan(str(root))}")


def _check(args, style: "_Style") -> None:
    spec = _load(args.spec, style)
    try:
        result = run_check(spec, args.app)
    except CheckError as exc:
        sys.exit(f"{style.red('check error:')} {exc}")

    safe = [c for c in result.changes if c.severity == "safe"]
    if args.verbose:
        for change in safe:
            print(f"  {style.yellow('~')} {style.dim(change.detail)}")

    if result.ok:
        summary = f"{style.green('ok')} — app matches spec"
        if safe:
            summary += style.dim(f" ({len(safe)} safe change(s))")
        print(summary)
        return

    for change in result.breaking:
        print(f"  {style.red('x')} {change.detail}")
    count = style.bold(str(len(result.breaking)))
    sys.exit(f"\n{style.red('fail')} — {count} breaking change(s)")


if __name__ == "__main__":
    main()
