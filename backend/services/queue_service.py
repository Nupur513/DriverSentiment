import queue
from abc import ABC, abstractmethod

class AbstractQueue(ABC):
    """
    Abstract Base Class (Interface) for a queue.
    This allows us to swap the implementation (e.g., from in-memory to Kafka)
    without changing the services that use it.
    """
    
    @abstractmethod
    def put(self, item):
        """Put an item into the queue."""
        pass
        
    @abstractmethod
    def get(self):
        """Get an item from the queue (blocking)."""
        pass
        
    @abstractmethod
    def task_done(self):
        """Indicate that a formerly enqueued task is complete."""
        pass

class InMemoryQueue(AbstractQueue):
    """
    A thread-safe, in-memory queue implementation.
    Wraps Python's standard `queue.Queue`.
    """
    def __init__(self):
        self.queue = queue.Queue()
        
    def put(self, item):
        self.queue.put(item)
        
    def get(self):
        # This will block until an item is available
        return self.queue.get()
        
    def task_done(self):
        self.queue.task_done()