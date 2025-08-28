"""Data models for port forwarding entries."""

import functools
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Callable, Concatenate, Optional, ParamSpec, Self, TypeVar, cast

from hapless.hap import Hap
from hapless.hap import Status as HapStatus

from rori import config

R = TypeVar("R")
P = ParamSpec("P")


def check_initialized(
    func: Callable[Concatenate["Rori", P], R],
) -> Callable[Concatenate["Rori", P], R]:
    @functools.wraps(func)
    def wrapper(self: "Rori", *args: P.args, **kwargs: P.kwargs) -> R:
        if self._hap is None or self._db_entry is None:
            raise RuntimeError(
                f"Cannot get {func.__name__} on the uninitialized instance."
            )

        return func(self, *args, **kwargs)

    return wrapper


class RoriError(ValueError):
    pass


class Status(StrEnum):
    """Enumeration for port forward entry statuses."""

    STARTING = "starting"
    ACTIVE = "active"
    INACTIVE = "inactive"
    BACKOFF = "backoff"
    ERROR = "error"


class EntryTypes(StrEnum):
    """Enumeration for port forward entry types."""

    SYSTEM = "system"
    MANUAL = "manual"
    KUBERNETES = "kubernetes"
    SSH = "ssh"
    SOCAT = "socat"

    @classmethod
    def choices(cls) -> list[str]:
        # TODO: add self.SOCAT
        return [cls.KUBERNETES, cls.SSH]


@dataclass
class RoriDbEntry:
    """Port forwarding entry data model."""

    hid: int  # same as rori_id
    port_from: int = 0
    port_to: int = 0
    type_: EntryTypes = EntryTypes.MANUAL
    desired_state: Status = Status.INACTIVE  # desired status, used by watcher
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Optional[dict[str, str]] = None

    # def __post_init__(self):
    #     """Set updated_at timestamp."""
    #     if self.hid is not None:
    #         self.updated_at = datetime.now()


class Rori:
    def __init__(self):
        # Internal fields
        self._hap: Optional[Hap] = None
        self._db_entry: Optional[RoriDbEntry] = None

    @property
    @check_initialized
    def hid(self) -> str:
        return cast(Hap, self._hap).hid

    @property
    @check_initialized
    def name(self) -> str:
        return self._hap.name

    @property
    @check_initialized
    def uptime(self) -> str:
        if self.status == Status.ACTIVE:
            return self._hap.runtime
        return ""

    @property
    @check_initialized
    def logfile(self) -> str:
        return self._hap.stdout_path

    @property
    @check_initialized
    def command(self) -> str:
        return self._hap.cmd

    @property
    @check_initialized
    def restarts(self) -> int:
        return self._hap.restarts

    @property
    @check_initialized
    def pid(self) -> Optional[int]:
        return self._hap.pid

    @property
    @check_initialized
    def port_from(self) -> int:
        return self._db_entry.port_from

    @property
    @check_initialized
    def port_to(self) -> int:
        return self._db_entry.port_to

    @property
    @check_initialized
    def type_(self) -> str:
        return self._db_entry.type_

    @property
    @check_initialized
    def metadata(self) -> dict[str, str]:
        return self._db_entry.metadata

    @property
    @check_initialized
    def status(self) -> Status:
        # backoff takes priority over other statuses
        if self._db_entry.desired_state == Status.BACKOFF:
            return Status.BACKOFF

        status = Status.INACTIVE
        hap = self._hap
        match hap.status:
            case HapStatus.RUNNING:
                status = Status.ACTIVE
            case HapStatus.FAILED:
                status = Status.ERROR
            case HapStatus.SUCCESS | HapStatus.PAUSED | HapStatus.UNBOUND:
                status = Status.INACTIVE

        return status

    @property
    @check_initialized
    def desired_state(self) -> Status:
        return self._db_entry.desired_state

    @property
    @check_initialized
    def is_system(self) -> bool:
        return (
            self.hid == "0"
            or self.name == config.RORIW_EXEC
            or self.type_ == EntryTypes.SYSTEM
        )

    @classmethod
    def compile(cls, rori_db_entry: RoriDbEntry, rori_hap: Hap) -> Self:
        """
        Compile a Rori instance from database entry and hap instance.
        """
        instance = cls()
        instance._hap = rori_hap
        instance._db_entry = rori_db_entry
        return instance

    def __str__(self) -> str:
        return f"#{self.hid} ({self.name})"

    def __rich__(self) -> str:
        rich_text = f"rori {config.ICON_RORIV}{self.hid} ([{config.COLOR_MAIN} bold]{self.name}[/])"
        # TODO: add info on the ports
        return rich_text

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self} object at {hex(id(self))}>"
