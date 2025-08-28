"""
CLI support for background A2A heartbeat and discovery tasks.
"""

import asyncio
import logging
import signal
import sys
import threading
import time
from typing import Optional

from broadie.a2a.discovery import DiscoveryClient
from broadie.a2a.heartbeat import Heartbeat
from broadie.config.settings import BroadieSettings

logger = logging.getLogger("broadie.a2a.cli")


class BackgroundTaskController:
    """Controller for managing background A2A tasks with graceful shutdown."""

    def __init__(self):
        self.heartbeat: Optional[Heartbeat] = None
        self.hb_thread: Optional[threading.Thread] = None
        self.disc_thread: Optional[threading.Thread] = None
        self.disc_stop_event = asyncio.Event()
        self._shutdown_complete = False

    def start_heartbeat(self, settings: BroadieSettings, agent_address: str):
        """Start heartbeat background task."""
        self.heartbeat = Heartbeat(
            settings=settings,
            agent_id=settings.a2a.agent_id,
            registry_url=settings.a2a.registry_url,
            api_key=None,
            interval=settings.a2a.heartbeat_interval,
            agent_address=agent_address,
            agent_name=settings.a2a.agent_name,
        )

        self.hb_thread = threading.Thread(
            target=lambda: asyncio.run(self.heartbeat.run()),
            daemon=False,  # Changed to False for proper shutdown
            name="a2a-heartbeat",
        )
        self.hb_thread.start()

    def start_discovery(self, settings: BroadieSettings):
        """Start discovery background task."""

        async def _disc_loop():
            disc = DiscoveryClient()
            while not self.disc_stop_event.is_set():
                try:
                    await disc.get_peers_from_registry(
                        settings.a2a.registry_url, api_key=None
                    )
                except Exception as e:
                    logger.error("Discovery error: %s", e)

                # Use wait_for with timeout to allow clean shutdown
                try:
                    await asyncio.wait_for(
                        self.disc_stop_event.wait(),
                        timeout=settings.a2a.discovery_interval,
                    )
                    break  # Stop event was set
                except asyncio.TimeoutError:
                    continue  # Continue loop after timeout

        self.disc_thread = threading.Thread(
            target=lambda: asyncio.run(_disc_loop()),
            daemon=False,  # Changed to False for proper shutdown
            name="a2a-discovery",
        )
        self.disc_thread.start()

    def stop(self, timeout: float = 5.0):
        """Stop all background tasks gracefully."""
        if self._shutdown_complete:
            return

        logger.info("Stopping A2A background tasks...")

        # Stop heartbeat
        if self.heartbeat:
            self.heartbeat.stop()

        # Stop discovery
        if not self.disc_stop_event.is_set():
            # Set the event in a new event loop if needed
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._set_stop_event())
                else:
                    asyncio.run(self._set_stop_event())
            except RuntimeError:
                asyncio.run(self._set_stop_event())

        # Wait for threads to complete
        threads_to_join = []
        if self.hb_thread and self.hb_thread.is_alive():
            threads_to_join.append(("heartbeat", self.hb_thread))
        if self.disc_thread and self.disc_thread.is_alive():
            threads_to_join.append(("discovery", self.disc_thread))

        for name, thread in threads_to_join:
            try:
                thread.join(timeout=timeout)
                if thread.is_alive():
                    logger.warning(f"{name} thread did not shutdown within {timeout}s")
                else:
                    logger.info(f"{name} thread stopped cleanly")
            except Exception as e:
                logger.error(f"Error stopping {name} thread: {e}")

        self._shutdown_complete = True
        logger.info("A2A background tasks stopped")

    async def _set_stop_event(self):
        """Set the discovery stop event."""
        self.disc_stop_event.set()


def start_background_tasks(
    agent_address: str = None,
) -> Optional[BackgroundTaskController]:
    """
    Start heartbeat and discovery loops in background threads.
    Returns BackgroundTaskController for graceful shutdown.
    """
    settings = BroadieSettings()
    if not settings.is_a2a_enabled():
        logger.info("A2A disabled; skipping heartbeat and discovery.")
        return None

    # Build agent address if not provided
    if not agent_address:
        host = settings.api_host if settings.api_host != "0.0.0.0" else "localhost"
        agent_address = f"http://{host}:{settings.api_port}"

    controller = BackgroundTaskController()

    # Start heartbeat
    controller.start_heartbeat(settings, agent_address)

    # Start discovery
    controller.start_discovery(settings)

    logger.info(
        "Started A2A background tasks: heartbeat every %ss, discovery every %ss",
        settings.a2a.heartbeat_interval,
        settings.a2a.discovery_interval,
    )
    return controller


def stop_background_tasks(controller: Optional[BackgroundTaskController]):
    """Stop background tasks gracefully."""
    if controller:
        try:
            controller.stop()
        except Exception as e:
            logger.error(f"Error during background task shutdown: {e}")


def setup_signal_handlers(controller: Optional[BackgroundTaskController]):
    """Set up signal handlers for graceful shutdown."""

    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        if controller:
            controller.stop()
        sys.exit(0)

    # Handle common termination signals
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C

    # Handle SIGHUP on Unix systems (not available on Windows)
    if hasattr(signal, "SIGHUP"):
        signal.signal(signal.SIGHUP, signal_handler)
