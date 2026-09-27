"""
Tests for typing_engine module.
"""

import time
import unittest
from src.typing_engine import TypingEngine, TimedTypingEngine


class TestTypingEngine(unittest.TestCase):
    """Test cases for TypingEngine."""
    
    def test_init(self):
        """Test initialization."""
        engine = TypingEngine("Hello World")
        self.assertEqual(engine.get_words(), ["Hello", "World"])
        self.assertEqual(engine.get_current_index(), 0)
        self.assertFalse(engine.is_running())
    
    def test_start(self):
        """Test starting the engine."""
        engine = TypingEngine("Hello World")
        engine.start()
        self.assertTrue(engine.is_running())
        self.assertFalse(engine.is_complete())
    
    def test_submit_correct_word(self):
        """Test submitting a correct word."""
        engine = TypingEngine("Hello World")
        engine.start()
        
        result = engine.submit_word("Hello")
        self.assertTrue(result)
        self.assertEqual(engine.get_current_index(), 1)
        self.assertEqual(engine.get_current_word(), "World")
    
    def test_case_insensitive_comparison(self):
        """Test that word comparison is case-insensitive."""
        engine = TypingEngine("Hello World")
        engine.start()
        
        # lowercase should match uppercase word
        result = engine.submit_word("hello")
        self.assertTrue(result)
        self.assertEqual(engine.get_current_index(), 1)
        
        # uppercase should match lowercase word
        result = engine.submit_word("WORLD")
        self.assertTrue(result)
        self.assertEqual(engine.get_current_index(), 2)
    
    def test_submit_incorrect_word(self):
        """Test submitting an incorrect word."""
        engine = TypingEngine("Hello World")
        engine.start()
        
        result = engine.submit_word("Wrong")
        self.assertFalse(result)
        self.assertEqual(engine.get_current_index(), 0)
        self.assertEqual(engine.errors, 1)
    
    def test_complete_session(self):
        """Test completing a session."""
        engine = TypingEngine("Hello World")
        engine.start()
        
        engine.submit_word("Hello")
        engine.submit_word("World")
        
        self.assertTrue(engine.is_complete())
        self.assertFalse(engine.is_running())
        self.assertEqual(engine.get_current_index(), 2)
    
    def test_get_total_time(self):
        """Test getting total time."""
        engine = TypingEngine("Hello World")
        engine.start()
        
        time.sleep(0.1)
        engine.submit_word("Hello")
        engine.submit_word("World")
        
        total_time = engine.get_total_time()
        self.assertGreater(total_time, 0)
    
    def test_get_wpm(self):
        """Test getting WPM."""
        engine = TypingEngine("Hello World")
        engine.start()
        
        time.sleep(0.1)
        engine.submit_word("Hello")
        engine.submit_word("World")
        
        wpm = engine.get_wpm()
        self.assertGreater(wpm, 0)
    
    def test_get_accuracy(self):
        """Test getting accuracy."""
        engine = TypingEngine("Hello World")
        engine.start()
        
        engine.submit_word("Hello")
        engine.submit_word("Wrong")  # Error
        engine.submit_word("World")
        
        accuracy = engine.get_accuracy()
        self.assertLess(accuracy, 100.0)
        self.assertGreater(accuracy, 0)
    
    def test_get_word_time(self):
        """Test getting word time."""
        engine = TypingEngine("Hello World")
        engine.start()
        
        time.sleep(0.05)
        engine.submit_word("Hello")
        
        word_time = engine.get_word_time(0)
        self.assertIsNotNone(word_time)
        self.assertGreater(word_time, 0)
    
    def test_get_progress(self):
        """Test getting progress."""
        engine = TypingEngine("Hello World Test")
        engine.start()
        
        self.assertEqual(engine.get_progress(), 0.0)
        
        engine.submit_word("Hello")
        self.assertAlmostEqual(engine.get_progress(), 1/3)
        
        engine.submit_word("World")
        self.assertAlmostEqual(engine.get_progress(), 2/3)
    
    def test_russian_text(self):
        """Test with Russian text."""
        engine = TypingEngine("Привет мир")
        engine.start()
        
        result = engine.submit_word("Привет")
        self.assertTrue(result)
        self.assertEqual(engine.get_current_word(), "мир")
    
    def test_empty_text(self):
        """Test with empty text."""
        engine = TypingEngine("")
        engine.start()
        
        self.assertTrue(engine.is_complete())
        self.assertEqual(engine.get_current_word(), None)
    
    def test_get_current_word_length(self):
        """Test getting current word length."""
        engine = TypingEngine("Hello World")
        engine.start()
        
        self.assertEqual(engine.get_current_word_length(), 5)
        
        engine.submit_word("Hello")
        self.assertEqual(engine.get_current_word_length(), 5)


class TestTimedTypingEngine(unittest.TestCase):
    """Test cases for TimedTypingEngine."""
    
    def test_init(self):
        """Test initialization."""
        engine = TimedTypingEngine("Hello World", 60)
        self.assertEqual(engine.get_words(), ["Hello", "World"])
        self.assertEqual(engine.time_limit, 60)
        self.assertFalse(engine.is_running())
    
    def test_start(self):
        """Test starting the engine."""
        engine = TimedTypingEngine("Hello World", 60)
        engine.start()
        self.assertTrue(engine.is_running())
        self.assertFalse(engine.is_finished())
    
    def test_submit_word(self):
        """Test submitting a word."""
        engine = TimedTypingEngine("Hello World", 60)
        engine.start()
        
        result = engine.submit_word("Hello")
        self.assertTrue(result)
        self.assertEqual(engine.get_words_typed(), 1)
    
    def test_case_insensitive_comparison(self):
        """Test that word comparison is case-insensitive."""
        engine = TimedTypingEngine("Hello World", 60)
        engine.start()
        
        result = engine.submit_word("hello")
        self.assertTrue(result)
        self.assertEqual(engine.get_words_typed(), 1)
        
        result = engine.submit_word("WORLD")
        self.assertTrue(result)
        self.assertEqual(engine.get_words_typed(), 2)
    
    def test_time_remaining(self):
        """Test remaining time."""
        engine = TimedTypingEngine("Hello World", 60)
        engine.start()
        
        remaining = engine.get_remaining_time()
        self.assertGreater(remaining, 0)
        self.assertLessEqual(remaining, 60)
    
    def test_time_up(self):
        """Test time up condition."""
        engine = TimedTypingEngine("Hello World", 0.1)
        engine.start()
        
        time.sleep(0.15)
        self.assertTrue(engine.is_time_up())
    
    def test_submit_after_time_up(self):
        """Test submitting after time is up."""
        engine = TimedTypingEngine("Hello World", 0.1)
        engine.start()
        
        time.sleep(0.15)
        result = engine.submit_word("Hello")
        self.assertFalse(result)
    
    def test_complete_before_time_up(self):
        """Test completing before time is up."""
        engine = TimedTypingEngine("Hello", 60)
        engine.start()
        
        engine.submit_word("Hello")
        self.assertTrue(engine.is_finished())
        self.assertFalse(engine.is_running())
    
    def test_get_current_word_length(self):
        """Test getting current word length."""
        engine = TimedTypingEngine("Hello World", 60)
        engine.start()
        
        self.assertEqual(engine.get_current_word_length(), 5)
        
        engine.submit_word("Hello")
        self.assertEqual(engine.get_current_word_length(), 5)


if __name__ == '__main__':
    unittest.main()
