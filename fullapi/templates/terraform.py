"""Terraform configuration templates."""


def main_tf(project_name: str, cloud_provider: str, enable_database: bool, enable_cache: bool):
    """Generate main.tf file."""
    modules = []

    # Always include registry and network
    modules.append("""
# Container registry
module "registry" {
  source = "~/.fullapi/terraform-modules/registry/${var.cloud_provider}"

  project_name = var.project_name
  environment  = var.environment
}

# Network infrastructure
module "network" {
  source = "~/.fullapi/terraform-modules/network/${var.cloud_provider}"

  project_name = var.project_name
  environment  = var.environment
}""")

    # Database module (conditional)
    if enable_database:
        modules.append("""
# Database
module "database" {
  source = "~/.fullapi/terraform-modules/database/${var.cloud_provider}"

  project_name   = var.project_name
  environment    = var.environment
  instance_size  = var.instance_size
  engine         = var.db_engine
  engine_version = var.db_version
  username       = var.db_username
  password       = var.db_password
  vpc_id         = module.network.vpc_id
  subnet_ids     = module.network.private_subnet_ids
}""")

    # Cache module (conditional)
    if enable_cache:
        modules.append("""
# Cache
module "cache" {
  source = "~/.fullapi/terraform-modules/cache/${var.cloud_provider}"

  project_name  = var.project_name
  environment   = var.environment
  instance_size = var.instance_size
  vpc_id        = module.network.vpc_id
  subnet_ids    = module.network.private_subnet_ids
}""")

    # Compute module (always included)
    env_vars = []
    if enable_database:
        env_vars.append('    DATABASE_URL = module.database.connection_string')
    if enable_cache:
        env_vars.append('    REDIS_URL    = module.cache.connection_string')
    env_vars.append('    ENVIRONMENT  = var.environment')

    compute = f"""
# Compute (container runtime)
module "compute" {{
  source = "~/.fullapi/terraform-modules/compute/${{var.cloud_provider}}"

  project_name      = var.project_name
  environment       = var.environment
  instance_size     = var.instance_size
  container_port    = var.container_port
  image_uri         = var.container_image_uri
  health_check_path = "/health"

  vpc_id     = module.network.vpc_id
  subnet_ids = module.network.public_subnet_ids

  environment_vars = {{
{chr(10).join(env_vars)}
  }}
}}"""
    modules.append(compute)

    return f'''terraform {{
  required_version = ">= 1.0.0, < 2.0.0"

  required_providers {{
    {_get_provider_block(cloud_provider)}
  }}
}}

{_get_provider_config(cloud_provider)}
{''.join(modules)}
'''


def _get_provider_block(cloud_provider: str) -> str:
    """Get provider block for terraform block."""
    if cloud_provider == "aws":
        return '''aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }'''
    elif cloud_provider == "gcp":
        return '''google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }'''
    elif cloud_provider == "azure":
        return '''azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }'''
    return ""


def _get_provider_config(cloud_provider: str) -> str:
    """Get provider configuration."""
    if cloud_provider == "aws":
        return '''
provider "aws" {
  region = var.region
}
'''
    elif cloud_provider == "gcp":
        return '''
provider "google" {
  project = var.gcp_project_id
  region  = var.region
}
'''
    elif cloud_provider == "azure":
        return '''
provider "azurerm" {
  features {}
  subscription_id = var.azure_subscription_id
}
'''
    return ""


def variables_tf(cloud_provider: str, enable_database: bool, enable_cache: bool):
    """Generate variables.tf file."""
    base_vars = '''variable "project_name" {
  description = "Project name"
  type        = string
}

variable "cloud_provider" {
  description = "Cloud provider: aws | gcp | azure"
  type        = string
}

variable "region" {
  description = "Deployment region"
  type        = string
}

variable "environment" {
  description = "Environment: dev | staging | prod"
  type        = string
  default     = "dev"
}

variable "instance_size" {
  description = "Instance size tier: small | medium | large"
  type        = string
  default     = "small"
}

variable "container_image_uri" {
  description = "Container image URI"
  type        = string
}

variable "container_port" {
  description = "Container port"
  type        = number
  default     = 8000
}
'''

    provider_vars = ""
    if cloud_provider == "gcp":
        provider_vars = '''
variable "gcp_project_id" {
  description = "GCP project ID"
  type        = string
}
'''
    elif cloud_provider == "azure":
        provider_vars = '''
variable "azure_subscription_id" {
  description = "Azure subscription ID"
  type        = string
}
'''

    db_vars = ""
    if enable_database:
        db_vars = '''
variable "db_engine" {
  description = "Database engine: postgresql | mysql"
  type        = string
}

variable "db_version" {
  description = "Database engine version"
  type        = string
}

variable "db_username" {
  description = "Database username"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}
'''

    return base_vars + provider_vars + db_vars


def outputs_tf(enable_database: bool, enable_cache: bool):
    """Generate outputs.tf file."""
    outputs = ['''output "service_url" {
  description = "Service URL"
  value       = module.compute.service_url
}

output "registry_url" {
  description = "Container registry URL"
  value       = module.registry.registry_url
}
''']

    if enable_database:
        outputs.append('''
output "database_endpoint" {
  description = "Database endpoint"
  value       = module.database.endpoint
  sensitive   = true
}
''')

    if enable_cache:
        outputs.append('''
output "cache_endpoint" {
  description = "Cache endpoint"
  value       = module.cache.endpoint
  sensitive   = true
}
''')

    return ''.join(outputs)


def terraform_tfvars(config):
    """Generate terraform.tfvars file."""
    lines = [
        f'# Auto-generated by fullapi',
        f'# Project: {config.name}',
        f'',
        f'project_name       = "{config.name}"',
        f'cloud_provider     = "{config.cloud_provider}"',
        f'region             = "{config.region}"',
        f'environment        = "dev"',
        f'instance_size      = "{config.instance_size}"',
        f'container_port     = 8000',
        f'',
        f'# Update after building and pushing Docker image',
        f'container_image_uri = "REPLACE_WITH_IMAGE_URI"',
    ]

    if config.cloud_provider == "gcp":
        lines.extend(['', 'gcp_project_id = "your-gcp-project-id"'])
    elif config.cloud_provider == "azure":
        lines.extend(['', 'azure_subscription_id = "your-azure-subscription-id"'])

    if config.database != "none":
        engine = "postgresql" if config.database == "postgresql" else "mysql"
        version = "15" if engine == "postgresql" else "8.0"
        lines.extend([
            '',
            f'db_engine   = "{engine}"',
            f'db_version  = "{version}"',
            f'db_username = "admin"',
            f'db_password = "CHANGE_ME_IN_PRODUCTION"',
        ])

    return '\n'.join(lines) + '\n'


def gitignore_additions():
    """Terraform entries to add to .gitignore."""
    return '''
# Terraform
*.tfstate
*.tfstate.*
.terraform/
.terraform.lock.hcl
terraform.tfvars
'''


def readme_terraform():
    """Terraform README content."""
    return '''# Terraform Infrastructure

## Prerequisites

1. Install Terraform (v1.x): https://www.terraform.io/downloads
2. Configure cloud provider credentials
3. Build and push Docker image

## Quick Start

```bash
# Initialize Terraform
fullapi terraform init

# Review planned changes
fullapi terraform plan

# Apply infrastructure
fullapi terraform apply

# Destroy infrastructure
fullapi terraform destroy
```

## Scaling

```bash
# Scale up instance size
fullapi scale up

# Scale down instance size
fullapi scale down

# Set specific size
fullapi scale set medium
```

## Manual Terraform

```bash
cd terraform/
terraform init
terraform plan
terraform apply
```

## Configuration

Edit `terraform.tfvars` to customize:
- `instance_size`: small | medium | large
- `environment`: dev | staging | prod
- Database credentials
- Cloud provider settings
'''
