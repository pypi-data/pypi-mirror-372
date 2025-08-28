"""Kubernetes interaction module for port forwarding."""

from typing import Dict, List, Optional

import questionary
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from loguru import logger

from rori.models import RoriError
from rori.ui import fzf_select_from_choices


class KubernetesService:
    """Handle Kubernetes operations for port forwarding."""

    def __init__(self, context: Optional[str] = None):
        """Initialize Kubernetes client."""
        self.v1: Optional[client.CoreV1Api] = None
        self.current_context = context
        self._load_config()

    def _load_config(self) -> None:
        try:
            config.load_kube_config(context=self.current_context)
            logger.debug(f"Loaded kubeconfig with context: {self.current_context}")
        except config.ConfigException as e:
            logger.error(f"Failed to load kubernetes config: {e}")
            raise RoriError(
                f"cannot load kubernetes configuration for {self.current_context} context"
            )
        self.v1: client.CoreV1Api = client.CoreV1Api()

    def set_context(self, context: str) -> None:
        """Set the current Kubernetes context."""
        logger.debug(f"Switching context to: {context}")
        self.current_context = context
        self._load_config()

    @staticmethod
    def get_available_contexts() -> List[Dict[str, str]]:
        """Get all available Kubernetes contexts."""
        try:
            contexts, active_context = config.list_kube_config_contexts()
            context_list = []

            for context in contexts:
                context_info = {
                    "name": context["name"],
                    "cluster": context["context"].get("cluster", "unknown"),
                    "user": context["context"].get("user", "unknown"),
                    "namespace": context["context"].get("namespace", "default"),
                    "active": context["name"] == active_context["name"]
                    if active_context
                    else False,
                }
                context_list.append(context_info)

            return context_list
        except config.ConfigException as e:
            print(f"❌ Error fetching contexts: {e}")
            return []

    @staticmethod
    def get_current_context() -> Optional[str]:
        """Get the currently active Kubernetes context."""
        try:
            _, active_context = config.list_kube_config_contexts()
            return active_context["name"] if active_context else None
        except config.ConfigException:
            return None

    def get_namespaces(self) -> List[str]:
        """Get all available namespaces."""

        try:
            namespaces = self.v1.list_namespace()
            return [ns.metadata.name for ns in namespaces.items]
        except ApiException as e:
            print(f"❌ Error fetching namespaces: {e}")
            return []

    def get_pods(self, namespace: str) -> List[Dict[str, str]]:
        """Get all pods in a namespace."""

        try:
            pods = self.v1.list_namespaced_pod(namespace=namespace)
            pod_list = []
            for pod in pods.items:
                if pod.status.phase == "Running":
                    pod_info = {
                        "name": pod.metadata.name,
                        "status": pod.status.phase,
                        "ready": self._get_pod_ready_status(pod),
                    }
                    pod_list.append(pod_info)
            return pod_list
        except ApiException as e:
            print(f"❌ Error fetching pods: {e}")
            return []

    def get_services(self, namespace: str) -> List[Dict[str, str]]:
        """Get all services in a namespace."""

        try:
            services = self.v1.list_namespaced_service(namespace=namespace)
            service_list = []
            for svc in services.items:
                ports = []
                if svc.spec.ports:
                    ports = [
                        f"{port.port}:{port.target_port}" for port in svc.spec.ports
                    ]

                service_info = {
                    "name": svc.metadata.name,
                    "type": svc.spec.type,
                    "ports": ", ".join(ports) if ports else "None",
                }
                service_list.append(service_info)
            return service_list
        except ApiException as e:
            print(f"❌ Error fetching services: {e}")
            return []

    def get_pod_ports(self, namespace: str, pod_name: str) -> List[int]:
        """Get available ports for a pod."""

        try:
            pod = self.v1.read_namespaced_pod(name=pod_name, namespace=namespace)
            ports = []

            if pod.spec.containers:
                for container in pod.spec.containers:
                    if container.ports:
                        for port in container.ports:
                            if port.container_port:
                                ports.append(port.container_port)

            return sorted(list(set(ports))) if ports else [8080]  # Default port
        except ApiException as e:
            print(f"❌ Error fetching pod ports: {e}")
            return [8080]

    def get_service_ports(self, namespace: str, service_name: str) -> list[int]:
        """Get available ports for a service (port, target_port)."""
        try:
            service = self.v1.read_namespaced_service(
                name=service_name, namespace=namespace
            )
            ports = []

            if service.spec.ports:
                ports = [item.port for item in service.spec.ports]

            return ports
        except ApiException as e:
            logger.error(f"error fetching service ports: {e}")
            raise RoriError("cannot fetch service ports")

    def _get_pod_ready_status(self, pod) -> str:
        """Get the ready status of a pod."""
        if not pod.status.conditions:
            return "Unknown"

        for condition in pod.status.conditions:
            if condition.type == "Ready":
                return "Ready" if condition.status == "True" else "Not Ready"

        return "Unknown"


def interactive_port_forward() -> Optional[str]:
    """Interactive questionary flow for port forwarding setup with fzf-like interface."""

    print("🔍 Kubernetes Port Forward (fzf-style)")
    print("═" * 45)
    print("💡 Use 'q' or 'Esc' to quit at any step")
    print()

    # Step 0: Select Kubernetes context (if not in-cluster)

    contexts = KubernetesService.get_available_contexts()
    if not contexts:
        print("❌ No Kubernetes contexts found")
        return None

    if len(contexts) == 1:
        # Only one context available, use it directly
        selected_context = contexts[0]["name"]
        print(f"✓ Using context: {selected_context}")
    else:
        # Multiple contexts, let user choose with fzf-like interface
        context_choices = []
        for ctx in contexts:
            display = f"{ctx['name']}"
            if ctx["active"]:
                display += " *"  # Mark active context
            display += f" [{ctx['cluster']}]"
            context_choices.append(questionary.Choice(display, ctx["name"]))

        selected_context = fzf_select_from_choices(
            "select kubernetes context:", context_choices
        )

        if not selected_context:
            print("👋 Context selection cancelled")
            return None

        try:
            k8s = KubernetesService(context=selected_context)
        except Exception as e:
            print(f"❌ Failed to initialize Kubernetes client: {e}")
            return None

    # Step 1: Select namespace with fuzzy search
    namespaces = k8s.get_namespaces()
    if not namespaces:
        print("❌ No namespaces found")
        return None

    namespace = fzf_select_from_choices("Select namespace:", namespaces)

    if not namespace:
        print("👋 Namespace selection cancelled")
        return None

    # Step 2: Select resource type
    resource_choices = [
        questionary.Choice("pod", "pod"),
        questionary.Choice("service", "service"),
    ]

    resource_type = fzf_select_from_choices("Select resource type:", resource_choices)

    if not resource_type:
        print("👋 Resource type selection cancelled")
        return None

    # Step 3: Select specific resource
    if resource_type == "pod":
        pods = k8s.get_pods(namespace)
        if not pods:
            print(f"❌ No running pods found in namespace '{namespace}'")
            return None

        # Create choices with status info
        pod_choices = []
        for pod in pods:
            display = f"{pod['name']} [{pod['status']}, {pod['ready']}]"
            pod_choices.append(questionary.Choice(display, pod["name"]))

        selected_resource = fzf_select_from_choices("Select pod:", pod_choices)

        if not selected_resource:
            print("👋 Pod selection cancelled")
            return None

        # Get pod ports
        ports = k8s.get_pod_ports(namespace, selected_resource)

        if len(ports) > 1:
            port_choices = [questionary.Choice(str(port), str(port)) for port in ports]
            selected_port = fzf_select_from_choices("Select port:", port_choices)

            if not selected_port:
                print("👋 Port selection cancelled")
                return None

            container_port = int(selected_port)
        else:
            container_port = ports[0]

        # Ask for local port with fzf-like input
        try:
            local_port_str = questionary.text(
                f"Enter local port [{container_port}]: ",
                default=str(container_port),
                style=FZF_STYLE,
                instruction=" (Enter for default, Ctrl+C to cancel)",
            ).ask()
        except (KeyboardInterrupt, EOFError):
            print("👋 Local port input cancelled")
            return None

        if local_port_str is None:
            return None

        local_port = local_port_str or str(container_port)

        # Generate kubectl command
        kubectl_command = f"kubectl port-forward -n {namespace} pod/{selected_resource} {local_port}:{container_port}"

    else:  # service
        services = k8s.get_services(namespace)
        if not services:
            print(f"❌ No services found in namespace '{namespace}'")
            return None

        service_choices = []
        for svc in services:
            display = f"{svc['name']} [{svc['type']}] {svc['ports']}"
            service_choices.append(questionary.Choice(display, svc["name"]))

        selected_resource = fzf_select_from_choices("Select service:", service_choices)

        if not selected_resource:
            print("👋 Service selection cancelled")
            return None

        # Get service ports
        service_ports = k8s.get_service_ports(namespace, selected_resource)

        if len(service_ports) > 1:
            port_choices = []
            for port, target_port in service_ports:
                display = f"{port}:{target_port}"
                port_choices.append(
                    questionary.Choice(display, f"{port}:{target_port}")
                )

            selected_port_pair = fzf_select_from_choices(
                "Select port mapping:", port_choices
            )

            if not selected_port_pair:
                print("👋 Port mapping selection cancelled")
                return None

            service_port, target_port = map(int, selected_port_pair.split(":"))
        else:
            service_port, target_port = service_ports[0]

        # Ask for local port
        try:
            local_port_str = questionary.text(
                f"Enter local port [{service_port}]: ",
                default=str(service_port),
                style=FZF_STYLE,
                instruction=" (Enter for default, Ctrl+C to cancel)",
            ).ask()
        except (KeyboardInterrupt, EOFError):
            print("👋 Local port input cancelled")
            return None

        if local_port_str is None:
            return None

        local_port = local_port_str or str(service_port)

        # Generate kubectl command
        kubectl_command = f"kubectl port-forward -n {namespace} service/{selected_resource} {local_port}:{service_port}"

    return kubectl_command


def fzf_select(
    message: str, choices: List[str], allow_quit: bool = True
) -> Optional[str]:
    """FZF-like selection with fuzzy search and quit capability."""
    try:
        result = questionary.autocomplete(
            message,
            choices=choices,
            style=FZF_STYLE,
            validate=lambda x: x in choices if x else True,
            # Enable fuzzy matching
            match_middle=True,
        ).ask()

        # Handle quit scenarios
        if not result and allow_quit:
            return None

        return result
    except (KeyboardInterrupt, EOFError):
        if allow_quit:
            return None
        raise
