"""Tests for AWS terraform templates."""

from fullapi.cloud_templates.aws_server import AWSServerTemplate


def test_generate_main_tf_minimal():
    """Test generating main.tf without database or redis."""
    template = AWSServerTemplate(
        project_name="myapi",
        region="us-east-1",
        has_database=False,
        has_redis=False
    )

    main_tf = template.generate_main_tf()

    assert "terraform {" in main_tf
    assert "aws" in main_tf
    assert "resource \"aws_ecs_cluster\"" in main_tf


def test_generate_main_tf_with_database():
    """Test generating main.tf with database."""
    template = AWSServerTemplate(
        project_name="myapi",
        region="us-east-1",
        has_database=True,
        has_redis=False
    )

    main_tf = template.generate_main_tf()

    assert "aws_db_instance" in main_tf
    assert "postgresql" in main_tf.lower()


def test_generate_variables_tf():
    """Test generating variables.tf."""
    template = AWSServerTemplate(
        project_name="myapi",
        region="us-east-1",
        has_database=True,
        has_redis=True
    )

    variables_tf = template.generate_variables_tf()

    assert "variable \"project_name\"" in variables_tf
    assert "variable \"region\"" in variables_tf
    assert "variable \"image_uri\"" in variables_tf


def test_generate_main_tf_with_redis():
    """Test generating main.tf with redis."""
    template = AWSServerTemplate(
        project_name="myapi",
        region="us-east-1",
        has_database=False,
        has_redis=True
    )

    main_tf = template.generate_main_tf()

    assert "aws_elasticache_cluster" in main_tf
    assert "redis" in main_tf.lower()


def test_generate_outputs_tf():
    """Test generating outputs.tf."""
    template = AWSServerTemplate(
        project_name="myapi",
        region="us-east-1",
        has_database=True,
        has_redis=True
    )

    outputs_tf = template.generate_outputs_tf()

    assert "output \"service_url\"" in outputs_tf
    assert "output \"database_endpoint\"" in outputs_tf
    assert "output \"redis_endpoint\"" in outputs_tf


def test_generate_tfvars():
    """Test generating terraform.tfvars."""
    template = AWSServerTemplate(
        project_name="myapi",
        region="us-east-1",
        has_database=True,
        has_redis=False
    )

    tfvars = template.generate_tfvars(
        image_uri="123456789.dkr.ecr.us-east-1.amazonaws.com/myapi:latest",
        port=8000,
        health_check="/health",
        env_vars={}
    )

    assert "project_name" in tfvars
    assert "image_uri" in tfvars
    assert "db_username" in tfvars
    assert "db_password" in tfvars


def test_database_conditionals_in_variables():
    """Test that database variables are conditional."""
    template_without_db = AWSServerTemplate(
        project_name="myapi",
        region="us-east-1",
        has_database=False,
        has_redis=False
    )

    variables_tf = template_without_db.generate_variables_tf()

    assert "db_username" not in variables_tf
    assert "db_password" not in variables_tf
