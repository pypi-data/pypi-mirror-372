from abc import ABC, abstractmethod

class BaseQueue(ABC):
    @abstractmethod
    def enqueue(self, item): pass

    @abstractmethod
    def dequeue(self): pass

    @abstractmethod
    def peek(self): pass

    @abstractmethod
    def is_empty(self): pass

    @abstractmethod
    def size(self): pass
