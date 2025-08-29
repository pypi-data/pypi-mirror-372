from collections import deque
from .base import BaseQueue

class FIFOQueue(BaseQueue):
    def __init__(self):
        self.queue = deque()

    def enqueue(self, item):
        self.queue.append(item)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.queue.popleft()

    def peek(self):
        return self.queue[0] if not self.is_empty() else None

    def is_empty(self):
        return len(self.queue) == 0

    def size(self):
        return len(self.queue)
