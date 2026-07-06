"""Spec model — the single source of truth for the API.

Loads and validates `api.yaml` into typed dataclasses. Downstream packages
(`generate`, `check`) depend only on these types, never on raw YAML.
"""

from fullapi.spec.model import Spec, Resource, Field
from fullapi.spec.loader import load_spec, SpecError

__all__ = ["Spec", "Resource", "Field", "load_spec", "SpecError"]
