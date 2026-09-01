"""Spec model — the single source of truth for the API.

Loads and validates `api.yaml` into typed dataclasses. Downstream packages
(`generate`, `check`) depend only on these types, never on raw YAML.
"""

from fullapi.spec.loader import SpecError, load_spec
from fullapi.spec.model import Field, Resource, Spec

__all__ = ["Field", "Resource", "Spec", "SpecError", "load_spec"]
