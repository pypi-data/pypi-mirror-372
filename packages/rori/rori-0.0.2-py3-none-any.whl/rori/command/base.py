import signal
from abc import ABC, abstractmethod
from typing import Optional, Self


class CommandContext(ABC):
    def __init__(self):
        self.port_from: Optional[int] = None
        self.port_to: Optional[int] = None

    @abstractmethod
    def setup(self):
        pass

    @classmethod
    @abstractmethod
    def interactive(cls) -> Self:
        pass

    @classmethod
    @abstractmethod
    def build(cls, *args, **kwargs) -> Self:
        pass

    @property
    @abstractmethod
    def metadata(self) -> dict:
        pass

    @property
    @abstractmethod
    def command(self) -> str:
        pass

    @property
    @abstractmethod
    def type_(self) -> str:
        pass

    @property
    @abstractmethod
    def executable(self) -> str:
        """Main executable to run the command."""
        pass

    @property
    def signal(self) -> signal.Signals:
        """Signal to use for stopping the process."""
        return signal.SIGTERM
