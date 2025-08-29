# ---------------------------------------------------------------------
# Gufo Liftbridge: Liftbridge context manager
# ---------------------------------------------------------------------
# Copyright (C) 2022-25, Gufo Labs
# See LICENSE.md for details
# ---------------------------------------------------------------------
"""liftbridge context manager."""

# Python modules
import asyncio
import logging
import os
import subprocess
import threading
from tempfile import TemporaryDirectory
from types import TracebackType
from typing import Optional, Type

logger = logging.getLogger("gufo.liftbridge.liftbridge")


class Liftbridge(object):
    """
    Liftbridge context manager for testing.

    Example:
        ``` py
        with Lifrbridge():
            # Any liftbridge code
        ```
    """

    def __init__(
        self,
        path: str = "/usr/local/bin/liftbridge",
        broker: str = "127.0.0.1:9292",
    ) -> None:
        self._path = path
        self._broker = broker
        self._data: Optional[TemporaryDirectory[str]] = None
        self._proc: Optional[subprocess.Popen[str]] = None

    def get_config(self) -> str:
        """Get service config."""
        return f"""
listen: {self._broker}
cursors:
    stream.auto.pause.time: 0
    stream.partitions: 1
"""

    def _start(self) -> None:
        logger.info("Starting liftbridge instance")
        # Create data directory
        self._data = TemporaryDirectory(prefix="liftbridge-")
        # Write config
        cfg = os.path.join(self._data.name, ".liftbridge.yml")
        with open(cfg, "w") as fp:
            fp.write(self.get_config())
        # Run liftbridge
        args = [
            self._path,
            "-c",
            cfg,
            "-d",
            self._data.name,
            "--embedded-nats",
            "--raft-bootstrap-seed",
        ]
        logger.debug("Running %s", " ".join(args))
        self._proc = subprocess.Popen(  # noqa: S603
            args,
            stdout=subprocess.PIPE,
            encoding="utf-8",
            text=True,
        )
        self._wait()
        self._consume_stdout()

    def _stop(self) -> None:
        """Terminate liftbridge instance."""
        if self._proc:
            logger.info("Stopping liftbridge")
            self._proc.kill()
        if self._data:
            self._data.cleanup()

    def _wait(self) -> None:
        async def wait_for_leader() -> None:
            from .client import LiftbridgeClient

            async with LiftbridgeClient([self._broker]) as client:
                await client.get_metadata()

        asyncio.run(asyncio.wait_for(wait_for_leader(), 10.0))

    def _consume_stdout(self) -> None:
        def inner() -> None:
            if self._proc and self._proc.stdout:
                for line in self._proc.stdout:
                    logger.debug("snmpd: %s", line[:-1])

        t = threading.Thread(target=inner)
        t.daemon = True
        t.start()

    def __enter__(self) -> "Liftbridge":
        """Context manager entry."""
        self._start()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Context manager exit."""
        self._stop()

    @property
    def broker(self) -> str:
        """Current brocker."""
        return self._broker
