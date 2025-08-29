import heapq
from .base import BaseQueue

class PriorityQueue(BaseQueue):
    def __init__(self):
        self.heap = []

    def enqueue(self, item, priority=0):
        heapq.heappush(self.heap, (priority, item))

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Priority Queue is empty")
        return heapq.heappop(self.heap)[1]

    def peek(self):
        return self.heap[0][1] if not self.is_empty() else None

    def is_empty(self):
        return len(self.heap) == 0

    def size(self):
        return len(self.heap)
