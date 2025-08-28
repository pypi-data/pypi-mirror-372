"""Test PofManager functionality."""

from unittest.mock import MagicMock, patch

import pytest

from rori.manager import PofManager


def test_pof_manager_initialization():
    """Test PofManager initialization."""
    with patch("rori.manager.PofDb") as mock_db:
        manager = PofManager()
        mock_db.assert_called_once()


def test_add_manual_pof(mock_hapless):
    """Test adding a manual port forward."""
    with patch("rori.manager.PofDb") as mock_db:
        manager = PofManager()

        # Mock database operations
        mock_db_instance = mock_db.return_value
        mock_db_instance.add.return_value = 1

        result = manager.add_manual_pof(8080, 80, name="test-forward")

        # Verify hap was created
        mock_hapless.create_hap.assert_called_once()

        # Verify database entry was added
        mock_db_instance.add.assert_called_once()

        assert result is not None


def test_add_manual_pof_without_name(mock_hapless):
    """Test adding a manual port forward without specifying name."""
    with patch("rori.manager.PofDb") as mock_db:
        manager = PofManager()
        mock_db_instance = mock_db.return_value
        mock_db_instance.add.return_value = 1

        result = manager.add_manual_pof(8080, 80)

        # Should still create the hap
        mock_hapless.create_hap.assert_called_once()
        assert result is not None


def test_start_pof(mock_hapless):
    """Test starting a port forward."""
    with patch("rori.manager.PofDb") as mock_db:
        manager = PofManager()

        # Mock getting hap
        mock_hap = MagicMock()
        mock_hap.hid = "test-hap"
        mock_hapless.get_hap.return_value = mock_hap

        manager.start("test-forward")

        mock_hapless.get_hap.assert_called_once_with("test-forward")


def test_start_nonexistent_pof(mock_hapless):
    """Test starting a non-existent port forward."""
    with patch("rori.manager.PofDb"):
        manager = PofManager()

        # Mock hap not found
        mock_hapless.get_hap.return_value = None

        with pytest.raises(Exception):
            manager.start("nonexistent")


def test_stop_pof(mock_hapless):
    """Test stopping a port forward."""
    with patch("rori.manager.PofDb"):
        manager = PofManager()

        # Mock getting hap
        mock_hap = MagicMock()
        mock_hap.hid = "test-hap"
        mock_hapless.get_hap.return_value = mock_hap

        manager.stop("test-forward")

        mock_hapless.get_hap.assert_called_once_with("test-forward")


def test_remove_pof(mock_hapless):
    """Test removing a port forward."""
    with patch("rori.manager.PofDb") as mock_db:
        manager = PofManager()
        mock_db_instance = mock_db.return_value

        # Mock getting hap
        mock_hap = MagicMock()
        mock_hap.hid = "test-hap"
        mock_hapless.get_hap.return_value = mock_hap

        manager.remove("test-forward")

        mock_hapless.get_hap.assert_called_once_with("test-forward")
        mock_db_instance.delete.assert_called_once_with("test-hap")


def test_list_pofs(mock_hapless):
    """Test listing port forwards."""
    with patch("rori.manager.PofDb"):
        manager = PofManager()

        # Mock hapless list_haps
        mock_hap1 = MagicMock()
        mock_hap1.hid = "hap1"
        mock_hap1.name = "test-forward-1"

        mock_hap2 = MagicMock()
        mock_hap2.hid = "hap2"
        mock_hap2.name = "test-forward-2"

        mock_hapless.list_haps.return_value = [mock_hap1, mock_hap2]

        result = manager.list_pofs()

        assert len(result) == 2
        mock_hapless.list_haps.assert_called_once()


def test_status_pof(mock_hapless):
    """Test getting status of a port forward."""
    with patch("rori.manager.PofDb"):
        manager = PofManager()

        # Mock getting hap
        mock_hap = MagicMock()
        mock_hap.hid = "test-hap"
        mock_hap.status = "running"
        mock_hapless.get_hap.return_value = mock_hap

        result = manager.status("test-forward")

        mock_hapless.get_hap.assert_called_once_with("test-forward")
        assert result is not None


def test_show_logs(mock_hapless):
    """Test showing logs for a port forward."""
    with patch("rori.manager.PofDb"):
        manager = PofManager()

        # Mock getting hap
        mock_hap = MagicMock()
        mock_hap.hid = "test-hap"
        mock_hapless.get_hap.return_value = mock_hap

        with patch.object(manager, "_follow_logs") as mock_follow:
            manager.show_logs("test-forward", follow=True)
            mock_follow.assert_called_once()


def test_show_logs_without_follow(mock_hapless):
    """Test showing logs without follow."""
    with patch("rori.manager.PofDb"):
        manager = PofManager()

        # Mock getting hap
        mock_hap = MagicMock()
        mock_hap.hid = "test-hap"
        mock_hapless.get_hap.return_value = mock_hap

        with patch("rori.manager.console") as mock_console:
            manager.show_logs("test-forward", follow=False)
            mock_console.print.assert_called()


@patch("rori.manager.get_executable_or_exit")
def test_get_kubectl_command(mock_get_executable):
    """Test getting kubectl command."""
    with patch("rori.manager.PofDb"):
        manager = PofManager()

        mock_get_executable.return_value = "/usr/local/bin/kubectl"

        result = manager._get_kubectl_command(
            "default", "test-service", 8080, 80, "test-context"
        )

        expected_cmd = [
            "/usr/local/bin/kubectl",
            "port-forward",
            "--context",
            "test-context",
            "--namespace",
            "default",
            "service/test-service",
            "8080:80",
        ]

        assert result == expected_cmd
        mock_get_executable.assert_called_once_with("kubectl")


def test_format_port_forward_command():
    """Test formatting port forward command."""
    with patch("rori.manager.PofDb"):
        manager = PofManager()

        result = manager._format_port_forward_command(8080, 80)
        assert result == "8080:80"

        result = manager._format_port_forward_command(9090, 90)
        assert result == "9090:90"


@patch("rori.manager.psutil")
def test_is_port_in_use(mock_psutil):
    """Test checking if port is in use."""
    with patch("rori.manager.PofDb"):
        manager = PofManager()

        # Mock psutil to return connections
        mock_conn = MagicMock()
        mock_conn.laddr.port = 8080
        mock_psutil.net_connections.return_value = [mock_conn]

        result = manager._is_port_in_use(8080)
        assert result is True

        result = manager._is_port_in_use(9090)
        assert result is False
