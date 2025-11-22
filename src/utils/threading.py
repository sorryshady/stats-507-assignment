"""Thread-safe queue management utilities."""

from queue import Queue, Empty
from typing import Optional
import threading


class ThreadSafeQueue:
    """Thread-safe queue wrapper with timeout support."""
    
    def __init__(self, maxsize: int = 0):
        """
        Initialize thread-safe queue.
        
        Args:
            maxsize: Maximum queue size (0 = unlimited)
        """
        self._queue = Queue(maxsize=maxsize)
        self._lock = threading.Lock()
    
    def put(self, item, block: bool = True, timeout: Optional[float] = None):
        """Put item in queue."""
        self._queue.put(item, block=block, timeout=timeout)
    
    def get(self, block: bool = True, timeout: Optional[float] = None):
        """Get item from queue."""
        try:
            return self._queue.get(block=block, timeout=timeout)
        except Empty:
            return None
    
    def empty(self) -> bool:
        """Check if queue is empty."""
        return self._queue.empty()
    
    def qsize(self) -> int:
        """Get queue size."""
        return self._queue.qsize()
    
    def clear(self):
        """Clear all items from queue."""
        with self._lock:
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                except Empty:
                    break

