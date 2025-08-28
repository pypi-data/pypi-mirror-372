import signal
from typing import Optional, Self

import questionary
from loguru import logger

from rori.command.base import CommandContext
from rori.k8s import (
    KubernetesService,
)
from rori.models import RoriError
from rori.ui import fzf_select_from_choices


class CommandK8s(CommandContext):
    """
    Builder for Kubernetes port forwarding configurations.
    """

    _service = KubernetesService()

    def __init__(self):
        super().__init__()
        self.context: Optional[str] = None
        self.namespace: Optional[str] = None
        self.service: Optional[str] = None
        self.pod: Optional[str] = None

    @classmethod
    def build(
        cls,
        *,
        port_from: int,
        port_to: int,
        context: str,
        namespace: str,
        service: Optional[str],
        pod: Optional[str],
    ) -> Self:
        """
        Build the port forwarding command for Kubernetes.
        """
        instance = cls()
        instance.port_from = port_from
        instance.port_to = port_to
        # kubernetes-specific options
        instance.context = context
        instance.namespace = namespace
        instance.service = service
        instance.pod = pod
        return instance

    def setup(self) -> None:
        self._service.set_context(self.context)

    @classmethod
    def interactive(cls):
        instance = cls()
        instance.context = cls._i_get_context()
        instance.namespace = cls._i_get_namespace()
        resource_type = cls._i_get_resource_type()
        match resource_type:
            case "pod":
                instance.pod = cls._i_get_pod(namespace=instance.namespace)
            case "service":
                instance.service = cls._i_get_service(namespace=instance.namespace)
                instance.port_from = cls._i_get_service_port(
                    namespace=instance.namespace,
                    service_name=instance.service,
                )
            case _:
                raise RoriError(f"unknown resource type {resource_type}")
        instance.port_to = cls._i_get_port_to()
        return instance

    @classmethod
    def _i_get_context(cls):
        contexts = cls._service.get_available_contexts()

        if len(contexts) == 1:
            selected_context = contexts[0]["name"]
            logger.info(f"using context {selected_context}")
            return selected_context

        context_choices = []
        for ctx in contexts:
            display = f"{ctx['name']}"
            if ctx["active"]:
                display += " *"  # Mark active context
            display += f" [{ctx['cluster']}]"
            context_choices.append(questionary.Choice(display, ctx["name"]))

        selected_context = fzf_select_from_choices("select context:", context_choices)
        return selected_context

    @classmethod
    def _i_get_namespace(cls):
        namespaces = cls._service.get_namespaces()
        if not namespaces:
            raise RoriError(f"no namespaces found in {cls._service.current_context}")

        selected_namespace = fzf_select_from_choices("select namespace", namespaces)
        return selected_namespace

    @classmethod
    def _i_get_resource_type(cls):
        resource_choices = [
            questionary.Choice("pod", "pod"),
            questionary.Choice("service", "service"),
        ]

        selected_resource = fzf_select_from_choices(
            "select resource type", resource_choices
        )

        return selected_resource

    @classmethod
    def _i_get_service(cls, namespace: str):
        services = cls._service.get_services(namespace)
        if not services:
            raise RoriError(f"no services found in {namespace} namespace")

        service_choices = []
        for svc in services:
            display = f"{svc['name']} [{svc['type']}] {svc['ports']}"
            service_choices.append(questionary.Choice(display, svc["name"]))

        selected_service = fzf_select_from_choices("select service", service_choices)
        return selected_service

    @classmethod
    def _i_get_service_port(cls, namespace: str, service_name: str) -> int:
        service_ports = cls._service.get_service_ports(namespace, service_name)
        if len(service_ports) == 1:
            return service_ports[0]

        port_choices = [
            questionary.Choice(f"{port}", f"{port}") for port in service_ports
        ]
        selected_port = fzf_select_from_choices("select port from", port_choices)
        return int(selected_port)

    @classmethod
    def _i_get_pod(cls, namespace: str):
        pods = cls._service.get_pods(namespace)
        if not pods:
            raise RoriError(f"no running pods found in {namespace} namespace")

        pod_choices = []
        for pod in pods:
            display = f"{pod['name']} [{pod['status']}, {pod['ready']}]"
            pod_choices.append(questionary.Choice(display, pod["name"]))

        selected_pod = fzf_select_from_choices("select pod", pod_choices)
        return selected_pod

    @classmethod
    def _i_get_port_to(cls):
        try:
            local_port_str = questionary.text(
                "enter port to",  # [{service_port}]: ",
                default="8080",  # str(service_port),
                # style=FZF_STYLE,
                instruction=" (Enter for default, Ctrl+C to cancel)",
            ).ask()
        except (KeyboardInterrupt, EOFError):
            print("👋 Local port input cancelled")
            return None

        return local_port_str

    @property
    def command(self) -> str:
        if self.service:
            command = f"kubectl port-forward -n {self.namespace} service/{self.service} {self.port_to}:{self.port_from}"
        elif self.pod:
            command = f"kubectl port-forward -n {self.namespace} pod/{self.pod} {self.port_to}:{self.port_from}"
        else:
            raise RoriError("either service or pod must be specified")

        return command

    # TODO: make these static not to fully restore context
    @property
    def type_(self) -> str:
        return "kubernetes"

    @property
    def executable(self) -> str:
        return "kubectl"

    @property
    def signal(self) -> signal.Signals:
        return signal.SIGINT

    @property
    def metadata(self):
        data = {}

        def add_if_defined(label, value):
            data.update({label: value}) if value else ...

        add_if_defined("context", self.context)
        add_if_defined("namespace", self.namespace)
        add_if_defined("service", self.service)
        add_if_defined("pod", self.pod)
        return data
