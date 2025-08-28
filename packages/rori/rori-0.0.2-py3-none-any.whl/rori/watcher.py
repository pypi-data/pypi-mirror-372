import asyncio
import signal
import sys
from dataclasses import dataclass
from typing import Iterable

from loguru import logger

from rori import config
from rori.manager import RoriManager
from rori.models import Rori, Status


@dataclass
class HealthCheck:
    rori: Rori
    healthy: bool
    fails: int = 0

    def __eq__(self, other) -> bool:
        return self.rori.hid == other.rori.hid

    def __lshift__(self, other):
        """Update current health check using << operator."""
        if isinstance(other, (list, tuple)):
            for item in other:
                if isinstance(item, HealthCheck) and self == item:
                    return self << item
            return self
        elif isinstance(other, HealthCheck) and self == other:
            # TODO: reset fails counter if other is healthy
            return HealthCheck(
                rori=self.rori,
                healthy=self.healthy,
                fails=0 if self.healthy else other.fails + 1,
            )
        return NotImplemented


class RoriWatcher:
    def __init__(self):
        self.manager = RoriManager(rori_dir=config.RORI_DIR)
        self._running = False
        self._stop_event = asyncio.Event()

        self.check_interval = config.RORIW_INTERVAL
        self.max_fails = config.RORIW_MAX_FAILS
        self._semaphore = asyncio.Semaphore(config.RORIW_CONCURRENCY)

    async def run_forever(self):
        if self._running:
            logger.warning("watcher is already running")
            return

        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGTERM, self.stop)

        self._running = True
        self._stop_event.clear()
        try:
            await self._run()
        except asyncio.CancelledError:
            logger.info("watcher was cancelled")
        except Exception as e:
            logger.error(f"watcher failed: {e}")
            sys.exit(1)
        finally:
            self._running = False

    async def _run(self):
        prev = []
        while self._running and not self._stop_event.is_set():
            logger.debug("checking health of roris")

            def filter_fn(rori: Rori) -> bool:
                """
                Filter function for active roris.
                and rori.status in (Status.INACTIVE, Status.ERROR)
                """
                return rori.desired_state == Status.ACTIVE and not rori.is_system

            roris = self.manager.get_roris(filter_fn=filter_fn)
            # results = await self.check_health(roris)
            # Update fails counter based on prev iteration
            results = [
                hc << prev
                for hc in await self.check_health(roris)
                if isinstance(hc, HealthCheck)
            ]
            unhealthy_roris = [res.rori for res in results if not res.healthy]
            if unhealthy_roris:
                await self.restart_unhealthy(results)
            else:
                logger.info("no rories to process at this iteration")
            prev = results
            await asyncio.sleep(self.check_interval)

    async def check_health(self, roris: Iterable[Rori]):
        tasks = []
        for rori in roris:
            tasks.append(asyncio.create_task(self._check_rori(rori), name=rori.name))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        errors = [res for res in results if isinstance(res, Exception)]
        if errors:
            logger.error(f"got some errors during the health check: {errors}")
        return results

    async def restart_unhealthy(self, checks: list[HealthCheck]):
        """
        Restart those expected to be active, but currently unhealthy.
        Do not touch if in backoff state.
        """
        tasks = []
        for check in checks:
            if check.fails < self.max_fails:
                tasks.append(asyncio.create_task(self._restart_rori(check.rori)))
                continue

            if check.rori.desired_state != Status.BACKOFF:
                logger.error(f"putting {check.rori} in backoff state")
                self.manager._db.set_desired_state(
                    rori_id=check.rori.hid, state=Status.BACKOFF
                )

        logger.info(f"restarting {len(tasks)}/{len(checks)} unhealthy roris")
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_rori(self, rori: Rori) -> HealthCheck:
        async with self._semaphore:
            logger.debug(f"checking health of {rori.name}")
            healthy = await self.check_port_connection(rori.port_to, timeout=3.0)
            return HealthCheck(rori=rori, healthy=healthy)

    async def check_port_connection(self, port: int, timeout: float) -> bool:
        """Check if a port is accepting connections."""
        try:
            host = "localhost"
            future = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(future, timeout=timeout)

            # Close the connection immediately
            writer.close()
            await writer.wait_closed()

            return True

        except (
            asyncio.TimeoutError,
            ConnectionRefusedError,
            ConnectionError,
            OSError,
        ) as e:
            logger.debug(f"port {port} check failed: {e}")
            return False

    async def _restart_rori(self, rori: Rori) -> None:
        async with self._semaphore:
            logger.debug(f"restarting unhealthy {rori.name}")
            # self.manager.restart(rori)
            # NOTE: shouldn't be noticable, but not to block event loop
            await asyncio.to_thread(self.manager.restart, rori)

    def stop(self, *args, **kwargs):
        """Stop the monitoring loop."""
        if not self._running:
            return

        logger.info("stopping port forward health monitoring")
        self._stop_event.set()


async def main():
    watcher = RoriWatcher()
    try:
        await watcher.run_forever()
    except KeyboardInterrupt:
        logger.info("Ctrl+C detected, stopping")
    finally:
        logger.info("actual stop is here")
        watcher.stop()


def entrypoint():
    asyncio.run(main())


if __name__ == "__main__":
    entrypoint()
