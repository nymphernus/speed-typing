"""
Typing engine module.
Manages typing session state, word tracking, and statistics.
"""

import time
from typing import Optional


class TypingEngine:
    """Manages a typing session."""
    
    def __init__(self, text: str):
        """
        Initialize typing engine.
        
        Args:
            text: The text to type.
        """
        self.words = self._split_into_words(text)
        self.current_index = 0
        self.word_start_time: Optional[float] = None
        self.total_start_time: Optional[float] = None
        self.total_end_time: Optional[float] = None
        self.word_times: dict[int, float] = {}
        self.errors = 0
        self._is_running = False
    
    @staticmethod
    def _split_into_words(text: str) -> list[str]:
        """Split text into words."""
        import re
        raw_words = text.split()
        words = []
        for raw_word in raw_words:
            cleaned = re.sub(r'^[^a-zA-Zа-яА-ЯёЁ0-9]+|[^a-zA-Zа-яА-ЯёЁ0-9]+$', '', raw_word)
            if cleaned:
                words.append(cleaned)
        return words
    
    def start(self) -> None:
        """Start the typing session."""
        self.total_start_time = time.time()
        self.word_start_time = time.time()
        self._is_running = True
    
    def submit_word(self, typed_word: str) -> bool:
        """
        Submit a word. Comparison is case-insensitive.
        
        Args:
            typed_word: The word that was typed.
            
        Returns:
            True if the word is correct, False otherwise.
        """
        if not self._is_running or self.current_index >= len(self.words):
            return False
        
        current_word = self.words[self.current_index]
        word_time = time.time() - self.word_start_time
        self.word_times[self.current_index] = word_time
        
        if typed_word.lower() == current_word.lower():
            self.current_index += 1
            self.word_start_time = time.time()
            
            if self.current_index >= len(self.words):
                self.total_end_time = time.time()
                self._is_running = False
            
            return True
        else:
            self.errors += 1
            return False
    
    def get_current_word(self) -> Optional[str]:
        """Get the current word to type."""
        if self.current_index < len(self.words):
            return self.words[self.current_index]
        return None
    
    def get_total_time(self) -> float:
        """Get total time spent typing in seconds."""
        if self.total_start_time is None:
            return 0.0
        end = self.total_end_time or time.time()
        return end - self.total_start_time
    
    def get_wpm(self) -> float:
        """Get words per minute."""
        total_time = self.get_total_time()
        if total_time == 0:
            return 0.0
        return (self.current_index / total_time) * 60
    
    def get_accuracy(self) -> float:
        """Get accuracy as a percentage."""
        if self.current_index == 0:
            return 100.0
        total_attempts = self.current_index + self.errors
        if total_attempts == 0:
            return 100.0
        return (self.current_index / total_attempts) * 100
    
    def get_word_time(self, word_index: int) -> Optional[float]:
        """Get time spent on a specific word."""
        return self.word_times.get(word_index)
    
    def get_average_word_time(self) -> float:
        """Get average time per word."""
        if not self.word_times:
            return 0.0
        return sum(self.word_times.values()) / len(self.word_times)
    
    def is_complete(self) -> bool:
        """Check if all words have been typed."""
        return self.current_index >= len(self.words)
    
    def is_running(self) -> bool:
        """Check if the session is running."""
        return self._is_running
    
    def get_progress(self) -> float:
        """Get progress as a fraction (0.0 to 1.0)."""
        if not self.words:
            return 0.0
        return self.current_index / len(self.words)
    
    def get_words(self) -> list[str]:
        """Get all words."""
        return self.words.copy()
    
    def get_current_index(self) -> int:
        """Get current word index."""
        return self.current_index
    
    def get_current_word_length(self) -> int:
        """Get length of the current word."""
        word = self.get_current_word()
        return len(word) if word else 0


class TimedTypingEngine:
    """Typing engine with time limit."""
    
    def __init__(self, text: str, time_limit: float):
        """
        Initialize timed typing engine.
        
        Args:
            text: The text to type.
            time_limit: Time limit in seconds.
        """
        self.words = TypingEngine._split_into_words(text)
        self.time_limit = time_limit
        self.current_index = 0
        self.start_time: Optional[float] = None
        self.word_times: dict[int, float] = {}
        self.word_start_time: Optional[float] = None
        self.errors = 0
        self._is_running = False
        self._is_finished = False
    
    def start(self) -> None:
        """Start the timed session."""
        self.start_time = time.time()
        self.word_start_time = time.time()
        self._is_running = True
        self._is_finished = False
    
    def submit_word(self, typed_word: str) -> bool:
        """
        Submit a word. Comparison is case-insensitive.
        
        Args:
            typed_word: The word that was typed.
            
        Returns:
            True if the word is correct, False otherwise.
        """
        if not self._is_running or self._is_finished:
            return False
        
        if self.is_time_up():
            self._is_finished = True
            self._is_running = False
            return False
        
        current_word = self.words[self.current_index]
        word_time = time.time() - self.word_start_time
        self.word_times[self.current_index] = word_time
        
        if typed_word.lower() == current_word.lower():
            self.current_index += 1
            self.word_start_time = time.time()
            
            if self.current_index >= len(self.words):
                self._is_finished = True
                self._is_running = False
            
            return True
        else:
            self.errors += 1
            return False
    
    def get_remaining_time(self) -> float:
        """Get remaining time in seconds."""
        if self.start_time is None:
            return self.time_limit
        elapsed = time.time() - self.start_time
        return max(0, self.time_limit - elapsed)
    
    def is_time_up(self) -> bool:
        """Check if time is up."""
        return self.get_remaining_time() <= 0
    
    def get_current_word(self) -> Optional[str]:
        """Get the current word to type."""
        if self.current_index < len(self.words):
            return self.words[self.current_index]
        return None
    
    def get_words_typed(self) -> int:
        """Get number of words typed."""
        return self.current_index
    
    def get_current_word_length(self) -> int:
        """Get length of the current word."""
        word = self.get_current_word()
        return len(word) if word else 0
    
    def get_errors(self) -> int:
        """Get number of errors."""
        return self.errors
    
    def is_running(self) -> bool:
        """Check if the session is running."""
        return self._is_running
    
    def is_finished(self) -> bool:
        """Check if the session is finished."""
        return self._is_finished
    
    def get_words(self) -> list[str]:
        """Get all words."""
        return self.words.copy()
