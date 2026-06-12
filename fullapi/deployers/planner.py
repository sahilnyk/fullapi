"""Deployment planning and specification."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from fullapi.analyzers.codebase import CodebaseAnalysis
from fullapi.colors import ICON_CHECK, bold


@dataclass
class DeploymentSpec:
    """Specification for a deployment."""
    project_name: str
    cloud_provider: str  # aws | gcp | azure
    deployment_type: str  # serverless | server
    region: str

    # From codebase analysis
    database: Optional[Dict]
    redis: bool
    port: int
    health_check_path: str

    # Docker info
    dockerfile_path: str
    image_uri: str  # Set after build

    # Environment & Secrets
    env_vars: Dict[str, str]
    secrets: List[str]

    # Infrastructure
    instance_size: str = "small"

    # Smart update info
    existing_deployment: bool = False
    changes_detected: List[str] = field(default_factory=list)


class DeploymentPlanner:
    """Creates deployment specifications from codebase analysis."""

    COST_ESTIMATES = {
        "aws": {
            "server": "$25-35/month",
            "serverless": "$10-20/month"
        },
        "gcp": {
            "server": "$30-40/month",
            "serverless": "$15-25/month"
        },
        "azure": {
            "server": "$28-38/month",
            "serverless": "$12-22/month"
        }
    }

    def __init__(self, analysis: CodebaseAnalysis, project_name: str,
                 cloud_provider: str, deployment_type: str, region: str):
        """Initialize planner."""
        self.analysis = analysis
        self.project_name = project_name
        self.cloud_provider = cloud_provider
        self.deployment_type = deployment_type
        self.region = region

    def create_spec(self) -> DeploymentSpec:
        """Create deployment specification from analysis."""
        # Separate secrets from regular env vars
        env_vars = {
            k: v for k, v in self.analysis.env_vars.items()
            if k not in self.analysis.secrets
        }

        return DeploymentSpec(
            project_name=self.project_name,
            cloud_provider=self.cloud_provider,
            deployment_type=self.deployment_type,
            region=self.region,
            database=self.analysis.database,
            redis=self.analysis.redis,
            port=self.analysis.port,
            health_check_path=self.analysis.health_check_path,
            dockerfile_path=self.analysis.dockerfile_path or "Dockerfile",
            image_uri="",  # Will be set by DockerBuilder
            env_vars=env_vars,
            secrets=self.analysis.secrets,
            instance_size="small"
        )

    def show_summary(self) -> None:
        """Display deployment plan summary."""
        print()
        print(f"  {bold('Analyzing codebase...')}")

        # Show detected features
        if self.analysis.database:
            db_type = self.analysis.database['type']
            db_version = self.analysis.database.get('version', 'latest')
            source = "docker-compose.yml" if self.analysis.has_docker_compose else "requirements.txt"
            print(f"  {ICON_CHECK}  Detected {db_type.capitalize()} {db_version} (from {source})")

        if self.analysis.redis:
            source = "docker-compose.yml" if self.analysis.has_docker_compose else "requirements.txt"
            print(f"  {ICON_CHECK}  Detected Redis (from {source})")

        if self.analysis.has_custom_dockerfile:
            print(f"  {ICON_CHECK}  Found custom Dockerfile (will use existing)")

        print(f"  {ICON_CHECK}  Port: {self.analysis.port}", end="")
        if self.analysis.has_custom_dockerfile:
            print(" (from Dockerfile EXPOSE)")
        else:
            print()

        print(f"  {ICON_CHECK}  Health check: {self.analysis.health_check_path}")

        secret_count = len(self.analysis.secrets)
        config_count = len(self.analysis.env_vars) - secret_count
        print(f"  {ICON_CHECK}  Environment vars: {len(self.analysis.env_vars)} detected ({secret_count} secrets, {config_count} config)")

        print()
        print(f"  {bold('Deployment Plan:')}")
        print(f"    Cloud: {self.cloud_provider.upper()} ({self.region})")

        deployment_name = "Container (ECS Fargate)" if self.cloud_provider == "aws" else "Container"
        if self.deployment_type == "serverless":
            deployment_name = "Serverless (Lambda)" if self.cloud_provider == "aws" else "Serverless"
        print(f"    Type: {deployment_name}")

        if self.analysis.database:
            db_type = self.analysis.database['type'].capitalize()
            db_version = self.analysis.database.get('version', 'latest')
            print(f"    Database: RDS {db_type} {db_version}")

        if self.analysis.redis:
            print("    Cache: ElastiCache Redis")

        if self.analysis.secrets:
            print(f"    Secrets: AWS Secrets Manager ({len(self.analysis.secrets)} secrets)")

        cost = self.COST_ESTIMATES[self.cloud_provider][self.deployment_type]
        print(f"    Estimated cost: {cost}")
        print()

    def get_confirmation(self) -> bool:
        """Ask user to confirm deployment."""
        response = input("Continue? (y/n): ").strip().lower()
        return response == 'y'
