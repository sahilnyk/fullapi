"""Classify differences between two normalized schemas."""

from typing import List

from fullapi.check.model import Change


def _diff_routes(expected: set, actual: set) -> List[Change]:
    changes = []
    for route in sorted(expected - actual):
        changes.append(Change("route_removed", "breaking", f"route missing: {route}"))
    for route in sorted(actual - expected):
        changes.append(Change("route_added", "safe", f"new route: {route}"))
    return changes


def _diff_fields(schema_name: str, expected: dict, actual: dict) -> List[Change]:
    changes = []
    for field, spec in expected.items():
        if field not in actual:
            changes.append(
                Change("field_removed", "breaking",
                       f"{schema_name}.{field} removed")
            )
            continue
        live = actual[field]
        if spec["type"] != live["type"]:
            changes.append(
                Change("field_type_changed", "breaking",
                       f"{schema_name}.{field} type changed "
                       f"{spec['type']} -> {live['type']}")
            )
        # Tightening: expected optional but live requires it.
        if live["required"] and not spec["required"]:
            changes.append(
                Change("field_required_tightened", "breaking",
                       f"{schema_name}.{field} became required")
            )

    for field, live in actual.items():
        if field in expected:
            continue
        severity = "breaking" if live["required"] else "safe"
        changes.append(
            Change("field_added", severity,
                   f"{schema_name}.{field} added"
                   + (" (required)" if live["required"] else ""))
        )
    return changes


def diff(expected: dict, actual: dict) -> List[Change]:
    """Return the list of Changes turning expected into actual."""
    changes = _diff_routes(expected["routes"], actual["routes"])

    exp_schemas = expected["schemas"]
    act_schemas = actual["schemas"]
    for name, exp_fields in exp_schemas.items():
        act_fields = act_schemas.get(name, {})
        changes += _diff_fields(name, exp_fields, act_fields)
    return changes
