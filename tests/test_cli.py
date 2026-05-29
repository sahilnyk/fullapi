"""Tests for CLI deploy command."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest


def test_deploy_command_requires_all_arguments():
    """Test that deploy command requires --cloud, --type, and --name."""
    from fullapi.cli import main

    # Missing all arguments
    with patch.object(sys, 'argv', ['fullapi', 'deploy']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 2


def test_deploy_command_validates_cloud_choices():
    """Test that --cloud only accepts aws, gcp, azure."""
    from fullapi.cli import main

    # Invalid cloud provider
    with patch.object(sys, 'argv', ['fullapi', 'deploy', '--cloud', 'invalid', '--type', 'server', '--name', 'myapp']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 2


def test_deploy_command_validates_type_choices():
    """Test that --type only accepts server, serverless."""
    from fullapi.cli import main

    # Invalid deployment type
    with patch.object(sys, 'argv', ['fullapi', 'deploy', '--cloud', 'aws', '--type', 'invalid', '--name', 'myapp']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 2


@patch('fullapi.cli.deploy_project')
def test_deploy_command_calls_deploy_project_with_defaults(mock_deploy):
    """Test that deploy command calls deploy_project with correct defaults."""
    from fullapi.cli import main

    mock_deploy.return_value = True

    with patch.object(sys, 'argv', ['fullapi', 'deploy', '--cloud', 'aws', '--type', 'server', '--name', 'myapp']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

    mock_deploy.assert_called_once_with(
        project_path=Path("."),
        cloud_provider="aws",
        deployment_type="server",
        app_name="myapp",
        region="us-east-1"
    )


@patch('fullapi.cli.deploy_project')
def test_deploy_command_calls_deploy_project_with_custom_region(mock_deploy):
    """Test that deploy command passes custom region."""
    from fullapi.cli import main

    mock_deploy.return_value = True

    with patch.object(sys, 'argv', ['fullapi', 'deploy', '--cloud', 'gcp', '--type', 'serverless', '--name', 'myapp', '--region', 'us-west-2']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

    mock_deploy.assert_called_once_with(
        project_path=Path("."),
        cloud_provider="gcp",
        deployment_type="serverless",
        app_name="myapp",
        region="us-west-2"
    )


@patch('fullapi.cli.deploy_project')
def test_deploy_command_exits_with_code_1_on_failure(mock_deploy):
    """Test that deploy command exits with code 1 when deploy_project returns False."""
    from fullapi.cli import main

    mock_deploy.return_value = False

    with patch.object(sys, 'argv', ['fullapi', 'deploy', '--cloud', 'azure', '--type', 'server', '--name', 'myapp']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


@patch('fullapi.cli.deploy_project')
def test_deploy_command_exits_with_code_0_on_success(mock_deploy):
    """Test that deploy command exits with code 0 when deploy_project returns True."""
    from fullapi.cli import main

    mock_deploy.return_value = True

    with patch.object(sys, 'argv', ['fullapi', 'deploy', '--cloud', 'aws', '--type', 'server', '--name', 'myapp']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
