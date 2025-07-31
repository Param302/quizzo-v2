import subprocess
import time
import signal
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CeleryManager:

    def __init__(self):
        self.worker_process: Optional[subprocess.Popen] = None
        self.beat_process: Optional[subprocess.Popen] = None

    def start_worker(self) -> bool:
        try:
            cmd = ["celery", "-A", "app.celery_app:make_celery()", "worker",
                   "--loglevel=warning", "--concurrency=2"]
            self.worker_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )
            return True
        except Exception as e:
            logger.error(f"Failed to start Celery worker: {e}")
            return False

    def start_beat(self) -> bool:
        try:
            cmd = ["celery", "-A", "app.celery_app:make_celery()", "beat",
                   "--loglevel=warning"]
            self.beat_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )
            return True
        except Exception as e:
            logger.error(f"Failed to start Celery beat: {e}")
            return False

    def start_all(self) -> bool:
        return self.start_worker() and self.start_beat()

    def stop_all(self):
        for process in [self.worker_process, self.beat_process]:
            if process:
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    process.wait(timeout=5)
                except (subprocess.TimeoutExpired, ProcessLookupError):
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    except ProcessLookupError:
                        pass

        self.worker_process = None
        self.beat_process = None

    def is_running(self) -> dict:
        worker_running = self.worker_process is not None and self.worker_process.poll() is None
        beat_running = self.beat_process is not None and self.beat_process.poll() is None

        return {
            'worker': worker_running,
            'beat': beat_running,
            'both': worker_running and beat_running
        }

    def check_redis(self) -> bool:
        try:
            import redis
            from app.config import Config

            r = redis.from_url(Config.CELERY_BROKER_URL)
            r.ping()
            return True
        except Exception:
            return False


# Global instance
celery_manager = CeleryManager()
