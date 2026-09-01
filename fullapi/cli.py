"""CLI entry point — thin dispatch for init/gen/check/migrate."""

import argparse
import sys
from pathlib import Path
from typing import NoReturn

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from fullapi import __version__
from fullapi.spec import load_spec, SpecError
from fullapi.generate import write
from fullapi.check import run_check, CheckError
from fullapi.migrate import run_migrate, MigrateError

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

# soft_wrap keeps short status lines from being hard-wrapped when stdout
# isn't a real terminal, e.g. piped output, CI logs, the test suite.
console = Console(soft_wrap=True)
error_console = Console(stderr=True, soft_wrap=True)


def _fail(message: str) -> NoReturn:
    """Print a red error line to stderr and exit with status 1."""
    error_console.print(message)
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="fullapi",
        description="Spec-driven FastAPI — generate a project from api.yaml and enforce it in CI.",
    )
    parser.add_argument("--version", action="version", version=f"fullapi {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="{init,gen,check,migrate}", required=True)

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

    mig = sub.add_parser("migrate", help="autogenerate an Alembic migration for the app")
    mig.add_argument("-o", "--out", default=".", help="generated app directory (default: .)")
    mig.add_argument("-m", "--message", default="auto migration",
                     help="migration message (default: 'auto migration')")

    args = parser.parse_args()
    {"init": _init, "gen": _gen, "check": _check, "migrate": _migrate}[args.command](args)


def _init(args) -> None:
    path = Path(args.spec)
    if path.exists():
        _fail(f"[red]error:[/] {escape(str(path))} already exists")

    path.write_text(STARTER_SPEC)
    console.print(Panel.fit(
        f"[green]done[/] — wrote [cyan]{escape(str(path))}[/]\n"
        f"[dim]next: fullapi gen {escape(str(path))}[/]",
        border_style="green",
    ))


def _load(spec_path: str):
    try:
        return load_spec(Path(spec_path))
    except SpecError as exc:
        _fail(f"[red]spec error:[/] {escape(str(exc))}")


def _gen(args) -> None:
    spec = _load(args.spec)
    written = write(spec, Path(args.out))
    root = Path(args.out).resolve()

    # Group the flat list of written paths into a directory tree so the
    # output reads like a real file listing, not a wall of paths.
    tree = Tree(f"[cyan]{escape(str(root))}[/]")
    dirs = {"": tree}
    for path in written:
        rel = path.resolve().relative_to(root)
        parent_key = ""
        for part in rel.parts[:-1]:
            child_key = f"{parent_key}/{part}"
            if child_key not in dirs:
                dirs[child_key] = dirs[parent_key].add(f"[dim]{escape(part)}/[/]")
            parent_key = child_key
        dirs[parent_key].add(escape(rel.parts[-1]))

    console.print(tree)
    console.print(f"\n[green]done[/] — [bold]{len(written)}[/] files written to [cyan]{escape(str(root))}[/]")


def _check(args) -> None:
    spec = _load(args.spec)
    try:
        result = run_check(spec, args.app)
    except CheckError as exc:
        _fail(f"[red]check error:[/] {escape(str(exc))}")

    safe = [c for c in result.changes if c.severity == "safe"]
    if args.verbose and safe:
        table = Table(show_header=False, box=None, title="safe changes", title_justify="left")
        for change in safe:
            table.add_row("[yellow]~[/]", f"[dim]{escape(change.detail)}[/]")
        console.print(table)

    if result.ok:
        summary = "[green]ok[/] — app matches spec"
        if safe:
            summary += f" [dim]({len(safe)} safe change(s))[/]"
        console.print(summary)
        return

    table = Table(title="breaking changes", header_style="bold red", title_justify="left")
    table.add_column("kind")
    table.add_column("detail")
    for change in result.breaking:
        table.add_row(change.kind, escape(change.detail))
    console.print(table)
    _fail(f"[red]fail[/] — [bold]{len(result.breaking)}[/] breaking change(s)")


def _migrate(args) -> None:
    app_dir = Path(args.out)
    try:
        # run_migrate shells out to alembic; its output is real subprocess
        # text (log lines like "[alembic.runtime.migration] ..."), not
        # markup we control, so it's escaped before rich sees it.
        output = run_migrate(app_dir, args.message)
    except MigrateError as exc:
        _fail(f"[red]migrate error:[/] {escape(str(exc))}")

    console.print(Panel(escape(output.strip()), title="alembic", border_style="cyan"))
    console.print("[green]done[/] — migration written")


if __name__ == "__main__":
    main()
