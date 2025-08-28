"""Port forward health monitoring module."""

import asyncio
import os
import sys
import time
from functools import partial

from rori.manager import RoriManager

print = partial(print, flush=True)


class Forker:
    def forking_method(self):
        pid = os.fork()
        if pid == 0:
            os.setsid()
            print(f"This is child with pid {os.getpid()}")
            # some blocking stuff
            time.sleep(3)
            # sys.exit(0)
            # avoid parent cleanup
            os._exit(0)
        print(f"This is parent with pid {os.getpid()}")


class Runner:
    def __init__(self):
        self.forker = Forker()

    async def run(self):
        while True:
            await asyncio.to_thread(self.forker.forking_method)
            await asyncio.sleep(10)


async def main():
    runner = Runner()
    print(f"Main process with pid {os.getpid()}")
    try:
        await runner.run()
    except asyncio.CancelledError:
        print("Task was cancelled")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Ctrl+C detected, stopping")
