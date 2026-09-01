"""Spec -> FastAPI project generation.

`render` is a pure function: a `Spec` in, a dict of relative-path -> file-text
out, with no filesystem side effects. `write` is the only function that touches
disk; it flushes `render`'s output under a destination directory.
"""

from pathlib import Path

from fullapi.generate.renderers import render
from fullapi.spec import Spec

__all__ = ["render", "write"]


def write(spec: Spec, dest: Path) -> list[Path]:
    """Write `render(spec)` under `dest`, returning the sorted written paths."""
    dest = Path(dest)
    written: list[Path] = []
    for rel_path, content in render(spec).items():
        target = dest / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written.append(target)
    return sorted(written)
