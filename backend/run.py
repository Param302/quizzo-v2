import os
import sys
import signal
import atexit
from app import create_app
from app.services.celery_manager import celery_manager

app = create_app()


def cleanup():
    if celery_manager.is_running()['both']:
        celery_manager.stop_all()


def signal_handler(signum, frame):
    cleanup()
    sys.exit(0)


if __name__ == "__main__":
    auto_start_celery = os.getenv(
        'AUTO_START_CELERY', 'false').lower() == 'true'

    if auto_start_celery:
        if not celery_manager.check_redis_connection():
            print("Error: Redis is not accessible. Please start Redis server first.")
            sys.exit(1)

        if not celery_manager.start_all():
            print("Failed to start Celery processes")
            sys.exit(1)

        atexit.register(cleanup)
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    app.run(debug=True, use_reloader=False if auto_start_celery else True)
