"""Configuration dataclass for project scaffolding."""

from dataclasses import dataclass


@dataclass
class ProjectConfig:
    """Configuration that drives all scaffolding decisions."""
    
    name: str
    mode: str = "basic"  # basic | full
    database: str = "none"  # none | sqlite | postgresql | mysql
    auth: bool = False
    docker: bool = False
