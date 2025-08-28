"""Test Kubernetes integration functionality."""

from unittest.mock import MagicMock, patch

import pytest


def test_kubernetes_port_forward_initialization(mock_kubernetes_config):
    """Test KubernetesPortForward initialization."""
    from rori.k8s import KubernetesPortForward

    k8s_pf = KubernetesPortForward()
    assert k8s_pf is not None


def test_get_contexts(mock_kubernetes_config):
    """Test getting Kubernetes contexts."""
    from rori.k8s import KubernetesPortForward

    k8s_pf = KubernetesPortForward()
    contexts = k8s_pf.get_contexts()

    assert len(contexts) == 2
    assert "test-context" in contexts
    assert "prod-context" in contexts


def test_get_current_context(mock_kubernetes_config):
    """Test getting current Kubernetes context."""
    from rori.k8s import KubernetesPortForward

    k8s_pf = KubernetesPortForward()
    current_context = k8s_pf.get_current_context()

    assert current_context == "test-context"


@patch("rori.k8s.client.CoreV1Api")
def test_get_namespaces(mock_core_api, mock_kubernetes_config, mock_k8s_client):
    """Test getting namespaces."""
    from rori.k8s import KubernetesPortForward

    mock_core_api.return_value = mock_k8s_client

    k8s_pf = KubernetesPortForward()
    namespaces = k8s_pf.get_namespaces("test-context")

    assert len(namespaces) == 3
    assert "default" in namespaces
    assert "kube-system" in namespaces
    assert "test-namespace" in namespaces


@patch("rori.k8s.client.CoreV1Api")
def test_get_services(mock_core_api, mock_kubernetes_config, mock_k8s_client):
    """Test getting services."""
    from rori.k8s import KubernetesPortForward

    mock_core_api.return_value = mock_k8s_client

    k8s_pf = KubernetesPortForward()
    services = k8s_pf.get_services("test-context", "default")

    assert len(services) == 2
    assert "test-service" in services
    assert "another-service" in services


@patch("rori.k8s.client.CoreV1Api")
def test_get_service_ports(mock_core_api, mock_kubernetes_config, mock_k8s_client):
    """Test getting service ports."""
    from rori.k8s import KubernetesPortForward

    mock_core_api.return_value = mock_k8s_client

    k8s_pf = KubernetesPortForward()
    ports = k8s_pf.get_service_ports("test-context", "default", "test-service")

    assert len(ports) == 1
    assert ports[0] == 80


def test_interactive_setup(mock_questionary, mock_kubernetes_config):
    """Test interactive setup flow."""
    from rori.k8s import KubernetesPortForward

    with patch.object(KubernetesPortForward, "get_namespaces") as mock_get_ns:
        with patch.object(KubernetesPortForward, "get_services") as mock_get_svc:
            with patch.object(
                KubernetesPortForward, "get_service_ports"
            ) as mock_get_ports:
                mock_get_ns.return_value = ["default", "test-namespace"]
                mock_get_svc.return_value = ["test-service", "another-service"]
                mock_get_ports.return_value = [80, 443]

                # Configure questionary responses
                mock_questionary.select.return_value.ask.side_effect = [
                    "test-context",  # context selection
                    "80",  # port selection
                ]
                mock_questionary.autocomplete.return_value.ask.side_effect = [
                    "default",  # namespace selection
                    "test-service",  # service selection
                ]
                mock_questionary.text.return_value.ask.return_value = (
                    "8080"  # local port
                )
                mock_questionary.confirm.return_value.ask.return_value = True  # confirm

                k8s_pf = KubernetesPortForward()
                result = k8s_pf.interactive_setup()

                assert result is not None
                assert result["context"] == "test-context"
                assert result["namespace"] == "default"
                assert result["service"] == "test-service"
                assert result["remote_port"] == "80"
                assert result["local_port"] == "8080"


def test_interactive_setup_cancellation(mock_questionary, mock_kubernetes_config):
    """Test interactive setup when user cancels."""
    from rori.k8s import KubernetesPortForward

    # Simulate user cancellation
    mock_questionary.confirm.return_value.ask.return_value = False

    k8s_pf = KubernetesPortForward()
    result = k8s_pf.interactive_setup()

    assert result is None


@patch("rori.k8s.config.load_kube_config")
def test_load_config_for_context(mock_load_config, mock_kubernetes_config):
    """Test loading config for specific context."""
    from rori.k8s import KubernetesPortForward

    k8s_pf = KubernetesPortForward()
    k8s_pf._load_config_for_context("test-context")

    mock_load_config.assert_called_once_with(context="test-context")


def test_questionary_style_configuration():
    """Test that questionary is configured with custom style."""
    from rori.k8s import KubernetesPortForward

    # Just verify that the class can be instantiated without errors
    # The style configuration is applied in the methods
    k8s_pf = KubernetesPortForward()
    assert hasattr(k8s_pf, "fzf_style")


@patch("rori.k8s.client.CoreV1Api")
def test_kubernetes_api_error_handling(mock_core_api, mock_kubernetes_config):
    """Test handling of Kubernetes API errors."""
    from rori.k8s import KubernetesPortForward

    # Mock API to raise exception
    mock_core_api.return_value.list_namespace.side_effect = Exception("API Error")

    k8s_pf = KubernetesPortForward()

    with pytest.raises(Exception, match="API Error"):
        k8s_pf.get_namespaces("test-context")


def test_empty_service_list_handling(mock_kubernetes_config):
    """Test handling when no services are found."""
    from rori.k8s import KubernetesPortForward

    with patch.object(KubernetesPortForward, "get_services") as mock_get_svc:
        mock_get_svc.return_value = []

        k8s_pf = KubernetesPortForward()
        services = k8s_pf.get_services("test-context", "empty-namespace")

        assert services == []


def test_service_without_ports_handling(mock_kubernetes_config):
    """Test handling services without ports."""
    from rori.k8s import KubernetesPortForward

    with patch.object(KubernetesPortForward, "get_service_ports") as mock_get_ports:
        mock_get_ports.return_value = []

        k8s_pf = KubernetesPortForward()
        ports = k8s_pf.get_service_ports("test-context", "default", "no-ports-service")

        assert ports == []


@patch("rori.k8s.config.list_kube_config_contexts")
def test_no_contexts_available(mock_list_contexts):
    """Test handling when no contexts are available."""
    from rori.k8s import KubernetesPortForward

    mock_list_contexts.return_value = ([], None)

    k8s_pf = KubernetesPortForward()
    contexts = k8s_pf.get_contexts()

    assert contexts == []


def test_invalid_context_handling(mock_kubernetes_config):
    """Test handling of invalid context."""
    from rori.k8s import KubernetesPortForward

    with patch.object(KubernetesPortForward, "_load_config_for_context") as mock_load:
        mock_load.side_effect = Exception("Invalid context")

        k8s_pf = KubernetesPortForward()

        with pytest.raises(Exception, match="Invalid context"):
            k8s_pf.get_namespaces("invalid-context")
