# nuvom/worker.py

"""
Thread‑based worker pool with graceful lifecycle management.

Key points
----------
• SIGINT / SIGTERM set a global `_shutdown_event`
• Workers drain personal queues before exit
• Dispatcher balances load & respects retry delays with backoff
• Plugin shutdown executed after workers drain
• Robust exception handling in workers to prevent silent crashes
"""

from __future__ import annotations

import queue
import signal
import threading
import time
from typing import List, Optional

from nuvom.config import get_settings
from nuvom.execution.job_runner import JobRunner
from nuvom.log import get_logger
from nuvom.queue import get_queue_backend
from nuvom.registry.auto_register import auto_register_from_manifest
from nuvom.plugins.loader import load_plugins, shutdown_plugins

# ------------------------------------------------------------------ #
_shutdown_event = threading.Event()  # Global stop‑flag for all threads
logger = get_logger()
# ------------------------------------------------------------------ #

class WorkerThread(threading.Thread):
    """
    Dedicated worker that pulls jobs from an *in‑memory* queue injected
    by the dispatcher. Completes outstanding work before exit.

    Parameters
    ----------
    worker_id : int
        Logical identifier for logs.
    job_timeout : int
        Default timeout forwarded to JobRunner.
    queue_maxsize : int
        Upper‑bound for the personal queue (0 = unbounded).
    """

    def __init__(self, worker_id: int, job_timeout: int, queue_maxsize: int = 0) -> None:
        super().__init__(daemon=True, name=f"Worker-{worker_id}")
        self.worker_id = worker_id
        self.job_timeout = job_timeout
        self._job_queue: queue.Queue = queue.Queue(maxsize=queue_maxsize)
        self._in_flight = 0
        self._lock = threading.Lock()

    # --------------------------- public helpers --------------------------- #
    def submit(self, job) -> None:
        """Push a job into this worker’s personal queue."""
        self._job_queue.put(job)

    def load(self) -> int:
        """Return current number of active jobs."""
        with self._lock:
            return self._in_flight

    def is_full(self) -> bool:
        """Return True if the personal queue is full."""
        return self._job_queue.full()

    # ----------------------------- thread body --------------------------- #
    def run(self) -> None:  # noqa: D401
        logger.info("[Worker-%s] Online.", self.worker_id)

        while True:
            # Break when global shutdown requested AND personal queue empty
            if _shutdown_event.is_set() and self._job_queue.empty():
                logger.info("[Worker-%s] Drained – shutting down.", self.worker_id)
                break

            try:
                job = self._job_queue.get(timeout=0.25)
            except queue.Empty:
                continue

            with self._lock:
                self._in_flight += 1

            logger.debug(
                "[Worker-%s] Executing job %s (%s)", self.worker_id, job.id, job.func_name
            )

            try:
                # Resilient execution: catch all to prevent silent thread death
                try:
                    JobRunner(job, self.worker_id, self.job_timeout).run()
                except Exception as e:
                    logger.error(
                        "[Worker-%s] Job %s execution failed: %s",
                        self.worker_id, job.id, e, exc_info=True
                    )
            finally:
                with self._lock:
                    self._in_flight -= 1

            logger.debug(
                "[Worker-%s] Completed %s → %s", self.worker_id, job.func_name, getattr(job, "result", None)
            )


class DispatcherThread(threading.Thread):
    """
    Dispatcher polls the *shared queue backend* and assigns jobs to the
    least‑loaded worker. Respects retry delay and halts on shutdown.
    """

    def __init__(
        self,
        workers: List[WorkerThread],
        batch_size: int,
        job_timeout: int,
        retry_backoff: float = 0.5,
    ) -> None:
        super().__init__(daemon=True, name="Dispatcher")
        self.workers = workers
        self.batch_size = batch_size
        self.job_timeout = job_timeout
        self.queue = get_queue_backend()
        self.retry_backoff = retry_backoff

    def _should_retry_later(self, job) -> bool:
        """Return True if job has a future retry timestamp."""
        ts: Optional[float] = getattr(job, "next_retry_at", None)
        return isinstance(ts, (int, float)) and ts > time.time()

    def run(self) -> None:  # noqa: D401
        logger.info("[Dispatcher] Started.")

        while not _shutdown_event.is_set():
            jobs = self.queue.pop_batch(self.batch_size, timeout=1)
            if not jobs:
                continue

            for job in jobs:
                # Retry‑delay handling
                if self._should_retry_later(job):
                    self.queue.enqueue(job)
                    # Sleep briefly to avoid busy spinning on retry jobs
                    time.sleep(self.retry_backoff)
                    continue

                # Select least loaded worker who is NOT full
                candidates = [w for w in self.workers if not w.is_full()]
                if not candidates:
                    logger.warning("[Dispatcher] All worker queues full, re-enqueueing job %s", job.id)
                    self.queue.enqueue(job)
                    time.sleep(self.retry_backoff)
                    continue

                target = min(candidates, key=lambda w: w.load())
                target.submit(job)
                logger.debug("[Dispatcher] Job %s → Worker-%s", job.id, target.worker_id)

        logger.info("[Dispatcher] Shutdown signal received – exiting.")


# ------------------------------------------------------------------ #
# Graceful Pool Entrypoint
# ------------------------------------------------------------------ #
def _install_signal_handlers() -> None:
    """Map SIGINT/SIGTERM to the global _shutdown_event."""

    def _handler(signum, _frame):  # noqa: D401
        logger.warning(
            "[Signal] %s received – initiating graceful shutdown.",
            signal.Signals(signum).name,
        )
        _shutdown_event.set()

    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)


def start_worker_pool(shutdown_timeout: float = 10.0) -> None:
    """
    Bootstrap the worker pool, run until Ctrl‑C / SIGTERM,
    then drain gracefully and exit.

    Args:
        shutdown_timeout (float): Max seconds to wait for workers to drain.
    """
    auto_register_from_manifest()
    _install_signal_handlers()

    cfg = get_settings()
    workers: List[WorkerThread] = [
        WorkerThread(
            i,
            job_timeout=cfg.job_timeout_secs,
            queue_maxsize=cfg.queue_maxsize,
        )
        for i in range(cfg.max_workers)
    ]
    for w in workers:
        w.start()

    dispatcher = DispatcherThread(
        workers,
        batch_size=cfg.batch_size,
        job_timeout=cfg.job_timeout_secs,
    )
    dispatcher.start()

    # Define runtime metrics_provider closure
    def metrics_provider():
        """Expose internal queue and worker stats for metrics plugins."""        
        stats =  {
            "queue_size": dispatcher.queue.qsize() if dispatcher and dispatcher.queue else 0,
            "worker_count": len(workers),
            "inflight_jobs": sum(w.load() for w in workers),
        }
        return stats
    
    # Pass live metrics to plugins
    load_plugins(extras={"metrics_provider": metrics_provider})
    
    try:
        while dispatcher.is_alive():
            dispatcher.join(timeout=0.5)
    finally:
        _shutdown_event.set()  # Ensure global flag is set for any path
        logger.info("[Pool] Awaiting %d worker threads…", len(workers))

        # Wait with timeout for workers to finish cleanly
        end_time = time.time() + shutdown_timeout
        for w in workers:
            remaining = max(0, end_time - time.time())
            w.join(timeout=remaining)

        logger.info("[Pool] All workers stopped cleanly or timeout reached.")

        # Shut down all loaded plugins
        shutdown_plugins()
        logger.info("[Pool] Plugin shutdown complete.")
