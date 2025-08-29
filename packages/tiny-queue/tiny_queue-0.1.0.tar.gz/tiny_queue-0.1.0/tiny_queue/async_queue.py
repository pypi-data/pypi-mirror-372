import asyncio
from .base import BaseQueue

class AsyncQueue(BaseQueue):
    def __init__(self):
        self.queue = asyncio.Queue()

    async def enqueue(self, item):
        await self.queue.put(item)

    async def dequeue(self):
        return await self.queue.get()

    def peek(self):
        raise NotImplementedError("Peek not supported in asyncio.Queue")

    def is_empty(self):
        return self.queue.empty()

    def size(self):
        return self.queue.qsize()
