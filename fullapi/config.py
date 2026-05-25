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
    redis: bool = False
    middleware: bool = False
    logging: bool = False
    template: str = None  # Path to custom template directory
    terraform: bool = False
    cloud_provider: str = None  # aws | gcp | azure
    region: str = None
    instance_size: str = "small"  # small | medium | large
