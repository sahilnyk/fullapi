# FullAPI Commands

## Overview
Complete list of CLI commands implemented in the fullapi project.

---

## 1. **fullapi new** - Create New FastAPI Project

### Usage
```bash
fullapi new <project_name> [options]
```

### Description
Generate a complete FastAPI project structure with optional database, authentication, Docker support, and more.

### Arguments
- `project_name` - Name of the project to create

### Options

#### Mode Options (mutually exclusive)
- `--basic` - Minimal structure (main, router, config). Skip interactive prompts.
- `--full` - Complete structure (models, CRUD, auth, DB). Skip interactive prompts.

#### Feature Options
- `--db {none|sqlite|postgresql|mysql}` - Specify database type (default: interactive prompt)
- `--auth` - Add JWT authentication support
- `--docker` - Add Docker and docker-compose files
- `--redis` - Add Redis caching support
- `--middleware` - Add middleware support
- `--logging` - Add logging support
- `--template <path>` - Use custom template directory

#### General Options
- `-h, --help` - Show help message
- `--version` - Show version

### Examples
```bash
# Interactive mode (prompts for options)
fullapi new my_api

# Basic mode (minimal setup)
fullapi new my_api --basic

# Full mode with all features
fullapi new my_api --full --db postgresql --auth --docker --redis --middleware --logging

# Full mode with specific database
fullapi new my_api --full --db mysql --auth --docker

# With custom templates
fullapi new my_api --template /path/to/custom/templates
```

---

## 2. **fullapi add** - Add Components to Existing Project

### Usage
```bash
fullapi add <component_type> <component_name>
```

### Description
Add new routers, models, and other components to an existing fullapi project.

### Arguments
- `component_type` - Type of component to add: `router` or `model`
- `component_name` - Name of the component (e.g., User, Product)

#### Supported Components

##### Router
```bash
fullapi add router <name>
```
Adds a new router with CRUD operations

**Example:**
```bash
fullapi add router User
fullapi add router Product
```

##### Model
```bash
fullapi add model <name>
```
Adds a new model with schema

**Example:**
```bash
fullapi add model User
fullapi add model Product
```

### Options
- `-h, --help` - Show help for add command

### Requirements
- Must be run from a valid fullapi project directory
- `main.py` file must exist in the current directory

### Examples
```bash
fullapi add router User
fullapi add router Product
fullapi add model User
fullapi add model Order
```

---

## 3. **fullapi deploy** - Deploy generated project to cloud

### Usage
```bash
fullapi deploy [options]
```

### Description
Deploy the current fullapi project to a cloud provider. Supports generating provider-specific infrastructure (Terraform) and choosing deployment style (serverless or server).

### Options
- `--cloud {aws|gcp|azure}` - Target cloud provider (required)
- `--service {serverless|server}` - Deployment target type: `serverless` (e.g., Lambdas/Cloud Run) or `server` (containerized service)
- `--region <region>` - Cloud region to deploy to (e.g., `us-east-1`, `us-central1`, `eastus`)
- `--env {dev|staging|prod}` - Deployment environment (default: `dev`)
- `--terraform` - Generate provider Terraform configuration alongside deployment
- `--confirm` - Skip interactive confirmations and proceed
- `-h, --help` - Show help for deploy command

### Examples
```bash
# Deploy a serverless app to AWS (production)
fullapi deploy --cloud aws --service serverless --env prod --region us-east-1 --terraform --confirm

# Deploy a containerized server to GCP (staging)
fullapi deploy --cloud gcp --service server --env staging --region us-central1

# Deploy to Azure in dev mode and generate Terraform
fullapi deploy --cloud azure --service serverless --env dev --region eastus --terraform
```

---

## 3. **General Options** (for all commands)

- `-h, --help` - Display help message
- `--version` - Show fullapi version

---

## Summary Table

| Command | Purpose | Key Options |
|---------|---------|------------|
| `fullapi new` | Create new project | `--basic`, `--full`, `--db`, `--auth`, `--docker`, `--redis`, `--middleware`, `--logging`, `--template` |
| `fullapi add router` | Add router to project | - |
| `fullapi add model` | Add model to project | - |

---

## Implementation Details

- **CLI Framework**: Python `argparse`
- **Entry Point**: `fullapi/cli.py` (`main()` function)
- **Module Entry**: `python -m fullapi` (via `fullapi/__main__.py`)

---

## Related Files
- [fullapi/cli.py](fullapi/cli.py) - Command definitions and handlers
- [fullapi/scaffold.py](fullapi/scaffold.py) - Project scaffolding logic
- [fullapi/add_component.py](fullapi/add_component.py) - Component addition logic
- [fullapi/prompt.py](fullapi/prompt.py) - Interactive prompts
- [fullapi/config.py](fullapi/config.py) - Configuration management
