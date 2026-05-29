"""AWS ECS Fargate terraform templates."""

from typing import Dict


class AWSServerTemplate:
    """Generates terraform configs for AWS ECS Fargate deployment."""

    def __init__(self, project_name: str, region: str,
                 has_database: bool, has_redis: bool):
        """Initialize template generator."""
        self.project_name = project_name
        self.region = region
        self.has_database = has_database
        self.has_redis = has_redis

    def generate_main_tf(self) -> str:
        """Generate main.tf with all resources."""
        sections = []

        # Terraform and provider config
        sections.append(self._terraform_block())
        sections.append(self._provider_block())

        # Networking
        sections.append(self._vpc_block())

        # ECS Cluster
        sections.append(self._ecs_cluster_block())

        # Database
        if self.has_database:
            sections.append(self._database_block())

        # Redis
        if self.has_redis:
            sections.append(self._redis_block())

        # Secrets Manager
        sections.append(self._secrets_manager_block())

        # ECS Task Definition and Service
        sections.append(self._ecs_task_definition_block())
        sections.append(self._ecs_service_block())

        # Load Balancer
        sections.append(self._load_balancer_block())

        return "\n\n".join(sections)

    def generate_variables_tf(self) -> str:
        """Generate variables.tf."""
        vars = [
            self._var("project_name", "string", "Project name"),
            self._var("region", "string", "AWS region"),
            self._var("environment", "string", "Environment (dev/staging/prod)", "dev"),
            self._var("image_uri", "string", "Container image URI"),
            self._var("container_port", "number", "Container port", "8000"),
            self._var("health_check_path", "string", "Health check endpoint", "/health"),
        ]

        if self.has_database:
            vars.extend([
                self._var("db_username", "string", "Database username", sensitive=True),
                self._var("db_password", "string", "Database password", sensitive=True),
            ])

        return "\n\n".join(vars)

    def generate_outputs_tf(self) -> str:
        """Generate outputs.tf."""
        outputs = [
            self._output("service_url", "aws_lb.main.dns_name", "Service URL"),
        ]

        if self.has_database:
            outputs.append(
                self._output("database_endpoint", "aws_db_instance.main.endpoint",
                           "Database endpoint", sensitive=True)
            )

        if self.has_redis:
            outputs.append(
                self._output("redis_endpoint",
                           "aws_elasticache_cluster.main.cache_nodes.0.address",
                           "Redis endpoint", sensitive=True)
            )

        return "\n\n".join(outputs)

    def generate_tfvars(self, image_uri: str, port: int,
                       health_check: str, env_vars: Dict) -> str:
        """Generate terraform.tfvars."""
        lines = [
            f"project_name       = \"{self.project_name}\"",
            f"region             = \"{self.region}\"",
            f"environment        = \"dev\"",
            f"image_uri          = \"{image_uri}\"",
            f"container_port     = {port}",
            f"health_check_path  = \"{health_check}\"",
        ]

        if self.has_database:
            lines.extend([
                "",
                "# Database credentials (change in production)",
                "db_username = \"admin\"",
                "db_password = \"CHANGE_ME_IN_PRODUCTION\"",
            ])

        return "\n".join(lines)

    # Helper methods for generating blocks

    def _terraform_block(self) -> str:
        return '''terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}'''

    def _provider_block(self) -> str:
        return f'''provider "aws" {{
  region = var.region
}}'''

    def _vpc_block(self) -> str:
        return '''# VPC and Networking
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-1"
  }
}

resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.region}b"
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-2"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "ecs_tasks" {
  name        = "${var.project_name}-ecs-tasks"
  description = "Allow inbound access from ALB"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "alb" {
  name        = "${var.project_name}-alb"
  description = "Allow inbound HTTP/HTTPS"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}'''

    def _ecs_cluster_block(self) -> str:
        return '''# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"
}'''

    def _database_block(self) -> str:
        return '''# RDS PostgreSQL
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet"
  subnet_ids = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds"
  description = "Allow PostgreSQL from ECS"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }
}

resource "aws_db_instance" "main" {
  identifier           = "${var.project_name}-db"
  engine               = "postgres"
  engine_version       = "15"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  storage_type         = "gp2"

  db_name  = replace(var.project_name, "-", "_")
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  skip_final_snapshot = true

  lifecycle {
    prevent_destroy = true
  }
}'''

    def _redis_block(self) -> str:
        return '''# ElastiCache Redis
resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-redis-subnet"
  subnet_ids = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

resource "aws_security_group" "redis" {
  name        = "${var.project_name}-redis"
  description = "Allow Redis from ECS"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }
}

resource "aws_elasticache_cluster" "main" {
  cluster_id           = "${var.project_name}-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379

  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]

  lifecycle {
    prevent_destroy = true
  }
}'''

    def _secrets_manager_block(self) -> str:
        return '''# Secrets Manager
resource "aws_secretsmanager_secret" "app_secrets" {
  name = "${var.project_name}-secrets"
}'''

    def _ecs_task_definition_block(self) -> str:
        env_vars = []
        if self.has_database:
            env_vars.append('        {"name": "DATABASE_URL", "value": "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.main.endpoint}/${replace(var.project_name, \\"-\\", \\"_\\")}"}')
        if self.has_redis:
            env_vars.append('        {"name": "REDIS_URL", "value": "redis://${aws_elasticache_cluster.main.cache_nodes.0.address}:6379"}')

        env_json = ",\n".join(env_vars) if env_vars else ""
        if env_json:
            env_json = ',\n      "environment": [\n' + env_json + '\n      ]'

        return f'''# ECS Task Definition
resource "aws_iam_role" "ecs_task_execution" {{
  name = "${{var.project_name}}-ecs-task-execution"

  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {{
        Service = "ecs-tasks.amazonaws.com"
      }}
    }}]
  }})
}}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {{
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}}

resource "aws_ecs_task_definition" "main" {{
  family                   = var.project_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([{{
    name  = var.project_name
    image = var.image_uri

    portMappings = [{{
      containerPort = var.container_port
      protocol      = "tcp"
    }}]{env_json}

    logConfiguration = {{
      logDriver = "awslogs"
      options = {{
        "awslogs-group"         = "/ecs/${{var.project_name}}"
        "awslogs-region"        = var.region
        "awslogs-stream-prefix" = "ecs"
        "awslogs-create-group"  = "true"
      }}
    }}
  }}])
}}'''

    def _ecs_service_block(self) -> str:
        return '''# ECS Service
resource "aws_ecs_service" "main" {
  name            = "${var.project_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.public_1.id, aws_subnet.public_2.id]
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.main.arn
    container_name   = var.project_name
    container_port   = var.container_port
  }

  depends_on = [aws_lb_listener.main]
}'''

    def _load_balancer_block(self) -> str:
        return '''# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

resource "aws_lb_target_group" "main" {
  name        = "${var.project_name}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = var.health_check_path
    healthy_threshold   = 2
    unhealthy_threshold = 10
    timeout             = 30
    interval            = 60
  }
}

resource "aws_lb_listener" "main" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }
}'''

    def _var(self, name: str, type: str, description: str,
             default: str = None, sensitive: bool = False) -> str:
        """Generate a variable block."""
        lines = [
            f'variable "{name}" {{',
            f'  description = "{description}"',
            f'  type        = {type}'
        ]
        if default:
            lines.append(f'  default     = {default}')
        if sensitive:
            lines.append('  sensitive   = true')
        lines.append('}')
        return '\n'.join(lines)

    def _output(self, name: str, value: str, description: str,
                sensitive: bool = False) -> str:
        """Generate an output block."""
        lines = [
            f'output "{name}" {{',
            f'  description = "{description}"',
            f'  value       = {value}'
        ]
        if sensitive:
            lines.append('  sensitive   = true')
        lines.append('}')
        return '\n'.join(lines)
