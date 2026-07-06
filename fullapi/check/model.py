"""Data types shared across the check package."""

from dataclasses import dataclass
from typing import List


class CheckError(Exception):
    """Raised when the live app cannot be imported or introspected."""


@dataclass(frozen=True)
class Change:
    """One classified difference between expected and actual schemas."""
    kind: str        # e.g. "field_removed", "field_type_changed", "route_removed",
                     #      "field_added", "route_added", "field_required_tightened"
    severity: str    # "breaking" | "safe"
    detail: str


@dataclass(frozen=True)
class CheckResult:
    """Outcome of a check run."""
    changes: List[Change]

    @property
    def breaking(self) -> List[Change]:
        return [c for c in self.changes if c.severity == "breaking"]

    @property
    def ok(self) -> bool:
        return not self.breaking
