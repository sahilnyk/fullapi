"""Typed spec model."""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Field:
    """One field on a resource."""
    name: str
    type: str        # a key of fullapi.types.TYPE_MAP
    required: bool = True


@dataclass(frozen=True)
class Resource:
    """One API resource -> model + schema + CRUD + REST router."""
    name: str            # singular, lowercase, e.g. "user"
    fields: List[Field]
    auth: bool = False   # protect this resource's routes


@dataclass(frozen=True)
class Spec:
    """The whole API described by api.yaml."""
    name: str
    database: str            # none | sqlite | postgres
    auth: bool               # jwt auth scaffolding enabled
    resources: List[Resource]
