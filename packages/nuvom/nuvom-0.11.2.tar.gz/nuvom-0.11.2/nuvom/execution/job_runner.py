# nuvom/execution/job_runner.py

"""
JobRunner executes a single job with timeout handling, lifecycle hooks, retries, 
and result/error persistence. Uses a thread pool for task execution isolation.
"""
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from nuvom.result_store import set_result, set_error
from nuvom.queue import get_queue_backend
from nuvom.log import get_logger
from nuvom.job import Job
from nuvom.config import get_settings

logger = get_logger()

class JobRunner:
    def __init__(self, job, worker_id: int, default_timeout: int):
        self.job = job
        self.worker_id = worker_id
        self.default_timeout = default_timeout
        self.q = get_queue_backend()

    def run(self) -> Job:
        timeout_secs = self.job.timeout_secs or self.default_timeout
        job = self.job

        retries_left = job.retries_left if job.retries_left is not None else job.max_retries
        job.retries_left = retries_left

        job.mark_running()
        logger.debug(f"[Runner-{self.worker_id}] Job '{job.func_name}' → RUNNING (timeout={timeout_secs}s)")

        if job.before_job:
            try:
                job.before_job()
                logger.debug(f"[Runner-{self.worker_id}] before_job hook OK")
            except Exception as e:
                logger.warning(f"[Runner-{self.worker_id}] before_job failed: {e}")

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(job.run)
            try:
                result = future.result(timeout=timeout_secs)

                if job.after_job:
                    try:
                        job.after_job(result)
                        logger.debug(f"[Runner-{self.worker_id}] after_job hook OK")
                    except Exception as e:
                        logger.warning(f"[Runner-{self.worker_id}] after_job failed: {e}")

                if job.store_result:
                    set_result(
                        job_id=job.id,
                        func_name=job.func_name,
                        result=result,
                        args=job.args,
                        kwargs=job.kwargs,
                        retries_left=job.retries_left,
                        attempts=job.max_retries - job.retries_left,
                        created_at=job.created_at,
                        completed_at=time.time(),
                    )
                    logger.debug(f"[Runner-{self.worker_id}] Stored result for '{job.func_name}'")

                job.mark_success(result)
                
                if self.q.name == 'sqlite':
                    self.q.mark_done(job.id)

                logger.info(f"[Runner-{self.worker_id}] Job '{job.func_name}' → SUCCESS")
                return job

            except FutureTimeoutError:
                policy = job.timeout_policy or get_settings().timeout_policy
                logger.warning(f"[Runner-{self.worker_id}] Job '{job.func_name}' TIMED OUT (policy={policy})")

                if policy == "retry" and job.retries_left > 0:
                    job.retries_left -= 1
                    delay = job.retry_delay_secs or get_settings().retry_delay_secs
                    job.next_retry_at = time.time() + delay
                    logger.info(f"[Runner-{self.worker_id}] Retrying in {delay}s")
                    self.q.enqueue(job)
                    return job

                elif policy == "ignore":
                    logger.info(f"[Runner-{self.worker_id}] Timeout ignored → storing None")
                    if job.store_result:
                        set_result(
                            job_id=job.id,
                            func_name=job.func_name,
                            result=None,
                            args=job.args,
                            kwargs=job.kwargs,
                            retries_left=job.retries_left,
                            attempts=job.max_retries - job.retries_left,
                            created_at=job.created_at,
                            completed_at=time.time(),
                        )
                    job.mark_success(None)
                    return job

                else:
                    return self._handle_failure("Job execution timed out.")

            except Exception as e:
                return self._handle_failure(e)

    def _handle_failure(self, error) -> Job:
        job = self.job

        if job.on_error:
            try:
                job.on_error(error)
                logger.debug(f"[Runner-{self.worker_id}] on_error hook OK")
            except Exception as e:
                logger.warning(f"[Runner-{self.worker_id}] on_error hook failed: {e}")

        job.mark_failed(error)

        if job.store_result:
            set_error(
                job_id=job.id,
                func_name=job.func_name,
                error=error,
                args=job.args,
                kwargs=job.kwargs,
                retries_left=job.retries_left,
                attempts=job.max_retries - job.retries_left,
                created_at=job.created_at,
                completed_at=time.time(),
            )
            logger.debug(f"[Runner-{self.worker_id}] Stored error for '{job.func_name}'")

        if job.retries_left > 0:
            job.retries_left -= 1
            retry_count = job.max_retries - job.retries_left
            delay = job.retry_delay_secs or get_settings().retry_delay_secs
            job.next_retry_at = time.time() + delay

            logger.warning(f"[Runner-{self.worker_id}] Retrying '{job.func_name}' (retry {retry_count}/{job.max_retries})")
            self.q.enqueue(job)
        else:
            logger.error(f"[Runner-{self.worker_id}] Job '{job.func_name}' FAILED permanently: {error}")

        return job
