"""Utility functions for AgentCorrect."""

import time


class Timer:
    """Simple timer for performance tracking."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start the timer."""
        self.start_time = time.time()
    
    def stop(self):
        """Stop the timer."""
        self.end_time = time.time()
    
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        if self.start_time is None:
            return 0
        
        end = self.end_time if self.end_time else time.time()
        return (end - self.start_time) * 1000