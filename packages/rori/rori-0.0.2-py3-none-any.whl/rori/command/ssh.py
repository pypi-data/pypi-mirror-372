from typing import Optional, Self

from rori.command.base import CommandContext
from rori.models import RoriError


class CommandSsh(CommandContext):
    """
    Builder for SSH port forwarding configurations.
    This class is responsible for creating and managing port forwarding configurations
    using SSH.
    """

    def __init__(self):
        super().__init__()
        self.host_from: Optional[str] = None
        self.remote_user: Optional[str] = None
        self.remote_server: Optional[str] = None
        self.private_key: Optional[str] = None

    @classmethod
    def build(
        cls,
        *,
        port_from: int,
        port_to: int,
        host_from: str,
        remote_user: str,
        remote_server: str,
        private_key: Optional[str] = None,
    ) -> Self:
        instance = cls()
        instance.port_from = port_from
        instance.port_to = port_to
        instance.host_from = host_from
        instance.remote_user = remote_user
        instance.remote_server = remote_server
        instance.private_key = private_key
        return instance

    @classmethod
    def interactive(cls) -> Self:
        """
        Create an interactive instance of the SSH command context.
        This method is used to gather user input for port forwarding configuration.
        """
        raise RoriError("interactive mode is not supported yet")
        instance = cls()
        return instance

    def setup(self):
        pass

    @property
    def command(self) -> str:
        """
        Return the SSH command for port forwarding.
        """
        key_option = ""
        if self.private_key:
            key_option = f" -i {self.private_key}"
        return f"ssh -v -N -T -L {self.port_to}:{self.host_from}:{self.port_from} {self.remote_user}@{self.remote_server}{key_option}"

    @property
    def metadata(self) -> dict:
        data = {}

        def add_if_defined(label, value):
            data.update({label: value}) if value else ...

        add_if_defined("host_from", self.host_from)
        add_if_defined("remote_user", self.remote_user)
        add_if_defined("remote_server", self.remote_server)
        add_if_defined("private_key", self.private_key)
        return data

    @property
    def type_(self) -> str:
        return "ssh"

    @property
    def executable(self) -> str:
        return "ssh"
