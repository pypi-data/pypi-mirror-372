"""Test CLI commands and options."""

from unittest.mock import Mock, patch

import pytest

from rori import cli


def test_executable_invocation(runner):
    """Test basic CLI invocation."""
    result = runner.invoke(cli.cli)
    assert result.exit_code == 0


def test_version_invocation(runner):
    """Test version command."""
    result = runner.invoke(cli.cli, ["--version"])
    assert result.exit_code == 0
    assert "pof, version" in result.output


def test_help_invocation(runner):
    """Test help command."""
    result = runner.invoke(cli.cli, ["--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


def test_list_command(runner):
    """Test list command invocation."""
    with patch("rori.cli.PofManager") as mock_manager:
        mock_instance = Mock()
        mock_manager.return_value = mock_instance
        mock_instance.list_pofs.return_value = []

        result = runner.invoke(cli.cli, ["list"])
        assert result.exit_code == 0
        mock_instance.list_pofs.assert_called_once()


def test_list_command_with_verbose(runner):
    """Test list command with verbose flag."""
    with patch("rori.cli.PofManager") as mock_manager:
        mock_instance = Mock()
        mock_manager.return_value = mock_instance
        mock_instance.list_pofs.return_value = []

        result = runner.invoke(cli.cli, ["list", "--verbose"])
        assert result.exit_code == 0
        mock_instance.list_pofs.assert_called_once()


def test_add_command_with_ports(runner):
    """Test add command with port specifications."""
    with patch("rori.cli.PofManager") as mock_manager:
        mock_instance = Mock()
        mock_manager.return_value = mock_instance

        result = runner.invoke(cli.cli, ["add", "8080:80"])
        assert result.exit_code == 0
        mock_instance.add_manual_rori.assert_called_once_with(8080, 80, name=None)


def test_add_command_with_name(runner):
    """Test add command with custom name."""
    with patch("rori.cli.PofManager") as mock_manager:
        mock_instance = Mock()
        mock_manager.return_value = mock_instance

        result = runner.invoke(cli.cli, ["add", "8080:80", "--name", "test-forward"])
        assert result.exit_code == 0
        mock_instance.add_manual_rori.assert_called_once_with(
            8080, 80, name="test-forward"
        )


def test_add_command_invalid_port_format(runner):
    """Test add command with invalid port format."""
    result = runner.invoke(cli.cli, ["add", "invalid"])
    assert result.exit_code != 0
    assert "Invalid port format" in result.output


def test_start_command(runner):
    """Test start command."""
    with patch("rori.cli.PofManager") as mock_manager:
        mock_instance = Mock()
        mock_manager.return_value = mock_instance

        result = runner.invoke(cli.cli, ["start", "test-forward"])
        assert result.exit_code == 0
        mock_instance.start.assert_called_once_with("test-forward")


def test_stop_command(runner):
    """Test stop command."""
    with patch("rori.cli.PofManager") as mock_manager:
        mock_instance = Mock()
        mock_manager.return_value = mock_instance

        result = runner.invoke(cli.cli, ["stop", "test-forward"])
        assert result.exit_code == 0
        mock_instance.stop.assert_called_once_with("test-forward")


def test_remove_command(runner):
    """Test remove command."""
    with patch("rori.cli.PofManager") as mock_manager:
        mock_instance = Mock()
        mock_manager.return_value = mock_instance

        result = runner.invoke(cli.cli, ["remove", "test-forward"])
        assert result.exit_code == 0
        mock_instance.remove.assert_called_once_with("test-forward")


def test_k8s_command_group(runner):
    """Test k8s command group."""
    result = runner.invoke(cli.cli, ["k8s", "--help"])
    assert result.exit_code == 0
    assert "Kubernetes commands" in result.output


def test_k8s_setup_command(runner, mock_questionary, mock_kubernetes_config):
    """Test k8s setup command."""
    with patch("rori.cli.KubernetesService") as mock_k8s:
        mock_instance = Mock()
        mock_k8s.return_value = mock_instance
        mock_instance.interactive_setup.return_value = {
            "name": "test-forward",
            "namespace": "default",
            "service": "test-service",
            "local_port": 8080,
            "remote_port": 80,
            "context": "test-context",
        }

        result = runner.invoke(cli.cli, ["k8s", "setup"])
        assert result.exit_code == 0
        mock_instance.interactive_setup.assert_called_once()


@patch("rori.cli.click.echo")
def test_error_handling_decorator(echo_mock, runner):
    """Test error handling decorator functionality."""
    with patch("rori.cli.PofManager") as mock_manager:
        mock_instance = Mock()
        mock_manager.return_value = mock_instance
        mock_instance.start.side_effect = Exception("Test error")

        result = runner.invoke(cli.cli, ["start", "test-forward"])
        assert result.exit_code == 1
        echo_mock.assert_called()


def test_logs_command(runner):
    """Test logs command."""
    with patch("rori.cli.PofManager") as mock_manager:
        mock_instance = Mock()
        mock_manager.return_value = mock_instance

        result = runner.invoke(cli.cli, ["logs", "test-forward"])
        assert result.exit_code == 0
        mock_instance.show_logs.assert_called_once_with("test-forward", follow=False)


def test_logs_command_with_follow(runner):
    """Test logs command with follow flag."""
    with patch("rori.cli.PofManager") as mock_manager:
        mock_instance = Mock()
        mock_manager.return_value = mock_instance

        result = runner.invoke(cli.cli, ["logs", "test-forward", "--follow"])
        assert result.exit_code == 0
        mock_instance.show_logs.assert_called_once_with("test-forward", follow=True)


def test_status_command(runner):
    """Test status command."""
    with patch("rori.cli.PofManager") as mock_manager:
        mock_instance = Mock()
        mock_manager.return_value = mock_instance

        result = runner.invoke(cli.cli, ["status", "test-forward"])
        assert result.exit_code == 0
        mock_instance.status.assert_called_once_with("test-forward")
