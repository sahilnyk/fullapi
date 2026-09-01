"""Spec compliance check — enforce a live FastAPI app matches its spec.

Public API:
    expected_schema(spec)        -> normalized dict derived from the spec (pure)
    actual_schema(app_import_path) -> normalized dict from a live app.openapi()
    diff(expected, actual)       -> list[Change] classifying differences
    run_check(spec, app_import_path) -> CheckResult (orchestrates; no printing)

Both sides are reduced to the same normalized structure before diffing so the
comparison logic (``diff``) stays independent of OpenAPI's exact shape.
"""

from fullapi.check.actual import actual_schema
from fullapi.check.differ import diff
from fullapi.check.expected import expected_schema
from fullapi.check.model import Change, CheckError, CheckResult


def run_check(spec, app_import_path: str) -> CheckResult:
    """Load the live app, compare it to the spec, return a CheckResult."""
    expected = expected_schema(spec)
    actual = actual_schema(app_import_path)
    return CheckResult(changes=diff(expected, actual))


__all__ = [
    "Change",
    "CheckError",
    "CheckResult",
    "actual_schema",
    "diff",
    "expected_schema",
    "run_check",
]
