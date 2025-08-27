import random
from typing import Any, Optional, List


class Queue(list):
    """A queue class that extends Python's list with additional queue operations."""
    
    def __init__(self, *elements):
        """
        Initialize the queue with elements.
        
        Args:
            *elements: The elements to initialize the queue with.
        """
        super().__init__(elements)
    
    @property
    def size(self) -> int:
        """Get the size of the queue."""
        return len(self)
    
    @property
    def first(self) -> Optional[Any]:
        """Get the first element in the queue."""
        return self[0] if self else None
    
    @property
    def last(self) -> Optional[Any]:
        """Get the last element in the queue."""
        return self[-1] if self else None
    
    def add(self, track: Any) -> 'Queue':
        """
        Add a track to the end of the queue.
        
        Args:
            track: The track to add.
            
        Returns:
            self for method chaining.
        """
        self.append(track)
        return self
    
    def remove(self, track: Any) -> bool:
        """
        Remove a specific track from the queue.
        
        Args:
            track: The track to remove.
            
        Returns:
            True if the track was removed, False if not found.
        """
        try:
            super().remove(track)
            return True
        except ValueError:
            return False
    
    def clear(self) -> None:
        """Clear all tracks from the queue."""
        super().clear()
    
    def shuffle(self) -> 'Queue':
        """
        Shuffle the tracks in the queue.
        
        Returns:
            self for method chaining.
        """
        random.shuffle(self)
        return self
    
    def peek(self) -> Optional[Any]:
        """Peek at the element at the front of the queue without removing it."""
        return self.first
    
    def to_array(self) -> List[Any]:
        """Get all tracks in the queue as a new list."""
        return self.copy()
    
    def at(self, index: int) -> Optional[Any]:
        """
        Get a track at a specific index.
        
        Args:
            index: The index of the track to retrieve.
            
        Returns:
            The track at the specified index or None if out of bounds.
        """
        try:
            return self[index]
        except IndexError:
            return None
    
    def dequeue(self) -> Optional[Any]:
        """Remove and return the first track from the queue."""
        return self.pop(0) if self else None
    
    def is_empty(self) -> bool:
        """
        Check if the queue is empty.
        
        Returns:
            True if the queue is empty, False otherwise.
        """
        return len(self) == 0
    
    def enqueue(self, track: Any) -> 'Queue':
        """
        Add a track to the end of the queue (alias for add).
        
        Args:
            track: The track to add.
            
        Returns:
            self for method chaining.
        """
        return self.add(track)