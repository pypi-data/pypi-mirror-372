import logging
from time import time

logging.basicConfig(level=logging.INFO)

class MonitorMixin:
    def log_enqueue(self, item):
        logging.info(f"[{time()}] Enqueued: {item}")

    def log_dequeue(self, item):
        logging.info(f"[{time()}] Dequeued: {item}")
