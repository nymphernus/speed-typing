"""
Timer module for tracking typing time.
"""

import time
from typing import Optional, Callable


class Timer:
    """Simple timer for tracking elapsed time."""
    
    def __init__(self):
        self._start_time: Optional[float] = None
        self._elapsed: float = 0.0
        self._is_running = False
    
    def start(self) -> None:
        """Start the timer."""
        self._start_time = time.time()
        self._is_running = True
    
    def stop(self) -> float:
        """
        Stop the timer.
        
        Returns:
            Elapsed time in seconds.
        """
        if self._start_time is not None:
            self._elapsed = time.time() - self._start_time
        self._is_running = False
        return self._elapsed
    
    def reset(self) -> None:
        """Reset the timer."""
        self._start_time = None
        self._elapsed = 0.0
        self._is_running = False
    
    def get_elapsed(self) -> float:
        """
        Get elapsed time in seconds.
        
        Returns:
            Elapsed time in seconds.
        """
        if self._is_running and self._start_time is not None:
            return time.time() - self._start_time
        return self._elapsed
    
    def is_running(self) -> bool:
        """Check if timer is running."""
        return self._is_running
    
    def get_formatted_time(self) -> str:
        """
        Get formatted time string (MM:SS).
        
        Returns:
            Formatted time string.
        """
        elapsed = self.get_elapsed()
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        return f"{minutes:02d}:{seconds:02d}"


class CountdownTimer:
    """Countdown timer for timed mode."""
    
    def __init__(self, time_limit: float, callback: Optional[Callable] = None):
        """
        Initialize countdown timer.
        
        Args:
            time_limit: Time limit in seconds.
            callback: Callback function when time is up.
        """
        self.time_limit = time_limit
        self._start_time: Optional[float] = None
        self._is_running = False
        self._callback = callback
    
    def start(self) -> None:
        """Start the countdown."""
        self._start_time = time.time()
        self._is_running = True
    
    def stop(self) -> None:
        """Stop the countdown."""
        self._is_running = False
    
    def reset(self) -> None:
        """Reset the countdown."""
        self._start_time = None
        self._is_running = False
    
    def get_remaining(self) -> float:
        """
        Get remaining time in seconds.
        
        Returns:
            Remaining time in seconds.
        """
        if self._start_time is None:
            return self.time_limit
        elapsed = time.time() - self._start_time
        return max(0, self.time_limit - elapsed)
    
    def is_running(self) -> bool:
        """Check if timer is running."""
        return self._is_running
    
    def is_time_up(self) -> bool:
        """Check if time is up."""
        return self.get_remaining() <= 0
    
    def get_formatted_remaining(self) -> str:
        """
        Get formatted remaining time string (MM:SS).
        
        Returns:
            Formatted time string.
        """
        remaining = self.get_remaining()
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def check_time_up(self) -> bool:
        """
        Check if time is up and call callback if so.
        
        Returns:
            True if time is up, False otherwise.
        """
        if self.is_time_up() and self._is_running:
            self._is_running = False
            if self._callback:
                self._callback()
            return True
        return False
