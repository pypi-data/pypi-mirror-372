import os
import random
import shutil
import signal
from pathlib import Path
from typing import Callable, Optional

from hapless.hap import Hap
from hapless.main import Hapless
from loguru import logger

from rori import config
from rori.command import CommandContext, CommandK8s, CommandSsh
from rori.db import RoriDb
from rori.models import EntryTypes, Rori, RoriDbEntry, RoriError, Status
from rori.utils import cat, tail


def filter_active(rori: Rori):
    return rori.status in (Status.ACTIVE,)


class RoriManager:
    def __init__(self, rori_dir: Path | str, *, init_watcher: bool = False):
        rori_dir = Path(rori_dir)
        if not rori_dir.exists():
            rori_dir.mkdir(parents=True, exist_ok=True)
            os.utime(rori_dir)
        self._rori_dir = rori_dir
        self._hapless = Hapless(rori_dir, quiet=True)
        self._db = RoriDb(rori_dir / "rori.db")

        if init_watcher:
            self._init_watcher()

    def _init_watcher(self):
        # TODO: match bool pairs
        if config.RORIW_ENABLED and shutil.which(config.RORIW_EXEC) is None:
            logger.critical(
                f"{config.RORIW_EXEC} not found, watcher will not be started"
            )
            return

        watcher_hap = self._hapless.get_hap(config.RORIW_EXEC)
        match (config.RORIW_ENABLED, watcher_hap):
            case (True, _):
                watcher_hap = watcher_hap or self._hapless.create_hap(
                    cmd=config.RORIW_EXEC,
                    hid="0",
                    name=config.RORIW_EXEC,
                    redirect_stderr=True,
                )
                if not watcher_hap.active:
                    logger.info("starting system watcher")
                    self._hapless.run_hap(watcher_hap)
                else:
                    logger.info(f"watcher is already running {watcher_hap}")
            case (False, None):
                # watcher is disabled and not found, nothing to do
                pass
            case (False, _):
                if watcher_hap.active:
                    logger.warning(
                        f"terminating watcher {watcher_hap} as it was disabled"
                    )
                    self._hapless.signal(watcher_hap, sig=signal.SIGTERM)

    def get_random_name(self) -> str:
        prefix = random.choice(["ro", "ri"])
        name = f"{prefix}-{Hap.get_random_name()}"
        return name

    def create(self, name: Optional[str], context: CommandContext) -> Rori:
        """
        Create a new port forwarding configuration.
        """
        name = name or self.get_random_name()
        existing_rori = self._get_or_none(name)
        if existing_rori:
            raise RoriError(f"entry with such a name already exists: {existing_rori}")

        rori_hap = self._hapless.create_hap(
            cmd=context.command,
            name=name,
            redirect_stderr=True,
        )
        # check initial hap status
        rori_db_entry = RoriDbEntry(
            hid=rori_hap.hid,
            port_from=context.port_from,
            port_to=context.port_to,
            type_=context.type_,
            metadata=context.metadata,
        )
        self._db.add(rori_db_entry)
        rori = Rori.compile(rori_db_entry, rori_hap)
        return rori

    def delete(self, rori: Rori, force: bool = False) -> None:
        if rori.status == Status.ACTIVE:
            raise RoriError(f"cannot delete active forwarding {rori.name}")
        self._hapless._clean_one(rori._hap)
        self._db.delete(rori_id=rori.hid)

    def rename(self, rori: Rori, new_name: str) -> None:
        new_name = new_name.strip()
        if not new_name:
            raise RoriError("new name cannot be empty")

        existing_rori = self._get_or_none(new_name)
        if existing_rori:
            raise RoriError(f"entry with such a name already exists: {existing_rori}")

        self._hapless.rename_hap(rori._hap, new_name)

    def run_command(self, command: str):
        name: str = self.get_random_name()
        hap = self._hapless.create_hap(
            cmd=command,
            name=name,
            redirect_stderr=True,
        )
        self._hapless.run_hap(hap)

    def start(self, rori: Rori, context: Optional[CommandContext] = None) -> None:
        """
        Start the port forwarding process for the given entry.
        """
        if rori.status == Status.ACTIVE:
            raise RoriError(f"port forwarding {rori.name} is already active")

        command_context = context or self.restore_context(rori)
        command_context.setup()
        self._hapless.run_hap(rori._hap)
        self._db.set_desired_state(rori_id=rori.hid, state=Status.ACTIVE)

    def stop(self, rori: Rori):
        """
        Stop the port forwarding process for the given entry.
        """
        self._db.set_desired_state(rori_id=rori.hid, state=Status.INACTIVE)

        if rori.status != Status.ACTIVE:
            raise RoriError(f"port forwarding {rori.name} is already inactive")

        command_context = self.restore_context(rori)
        self._hapless.signal(hap=rori._hap, sig=command_context.signal)

    def restart(self, rori: Rori) -> None:
        # TODO: context is needed here too
        self._hapless.restart(rori._hap)

    def get_rori(self, rori_alias: str) -> Rori:
        rori_hap = self._hapless.get_hap(rori_alias)
        if rori_hap is None:
            raise RoriError(f"no rori found for alias {rori_alias}")
        rori_db_entry = self._db.get(rori_id=rori_hap.hid)
        if rori_db_entry is None:
            raise RoriError(
                f"no rori entry found in the database for id {rori_hap.hid}"
            )

        rori = Rori.compile(rori_db_entry, rori_hap)
        return rori

    def _get_or_none(self, rori_alias: str) -> Optional[Rori]:
        try:
            return self.get_rori(rori_alias)
        except RoriError:
            pass

    def get_roris(
        self,
        filter_fn: Optional[Callable[[Rori], bool]] = None,
    ) -> list[Rori]:
        """
        Retrieve the list of port forwarding configurations.
        """
        # Placeholder for actual implementation
        haps = self._hapless.get_haps()
        roris = []
        for rori_hap in haps:
            rori_db_entry = self._db.get(rori_id=rori_hap.hid)
            if rori_db_entry is None:
                raise RoriError(
                    f"no rori entry found in the database for id {rori_hap.hid}"
                )
            roris.append(Rori.compile(rori_db_entry, rori_hap))

        if filter_fn is None:
            return roris
        return list(filter(filter_fn, roris))

    def logs(self, rori: Rori, follow: bool = False):
        """
        Retrieve logs for a specific port forwarding entry.
        If `follow` is True, it should stream the logs.
        """
        if follow:
            return tail(rori.logfile, follow=True)

        return cat(rori.logfile)

    def restore_context(self, rori: Rori) -> CommandContext:
        """
        Restores a command context for the given port forwarding entry.
        """
        match rori.type_:
            case EntryTypes.KUBERNETES:
                context = CommandK8s.build(
                    port_from=rori.port_from,
                    port_to=rori.port_to,
                    context=rori.metadata.get("context"),
                    namespace=rori.metadata.get("namespace"),
                    service=rori.metadata.get("service"),
                    pod=rori.metadata.get("pod"),
                )
            case EntryTypes.SSH:
                context = CommandSsh.build(
                    port_from=rori.port_from,
                    port_to=rori.port_to,
                    host_from=rori.metadata.get("host_from"),
                    remote_user=rori.metadata.get("remote_user"),
                    remote_server=rori.metadata.get("remote_server"),
                    private_key=rori.metadata.get("private_key"),
                )
            case _:
                raise RoriError(f"unknown rori type: {rori.type_}")
        return context
