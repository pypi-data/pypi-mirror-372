from collections import deque
import json
import os
from .fifo import FIFOQueue

class PersistentQueue(FIFOQueue):
    def __init__(self, filepath='queue_data.json'):
        super().__init__()
        self.filepath = filepath
        self._load()

    def enqueue(self, item):
        super().enqueue(item)
        self._save()

    def dequeue(self):
        item = super().dequeue()
        self._save()
        return item

    def _save(self):
        with open(self.filepath, 'w') as f:
            json.dump(list(self.queue), f)

    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                self.queue = deque(data)
