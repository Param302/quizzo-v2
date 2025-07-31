import subprocess
import time
import signal
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CeleryManager:
    """
    Simple Celery process manager for automatic startup with Flask.
    """

    def __init__(self):
        self.worker_process: Optional[subprocess.Popen] = None
        self.beat_process: Optional[subprocess.Popen] = None

    def start_worker(self) -> bool:
        """Start Celery worker process"""
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
        """Start Celery beat scheduler process"""
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
        """Start both worker and beat scheduler"""
        worker_ok = self.start_worker()
        time.sleep(2)
        beat_ok = self.start_beat()
        return worker_ok and beat_ok

    def stop_all(self):
        """Stop all Celery processes"""
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
        """Check if Celery processes are running"""
        worker_running = self.worker_process is not None and self.worker_process.poll() is None
        beat_running = self.beat_process is not None and self.beat_process.poll() is None

        return {
            'worker': worker_running,
            'beat': beat_running,
            'both': worker_running and beat_running
        }

    def check_redis_connection(self) -> bool:
        """Check if Redis is accessible"""
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
