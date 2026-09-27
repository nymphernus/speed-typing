"""
Tests for timer module.
"""

import time
import unittest
from src.timer import Timer, CountdownTimer


class TestTimer(unittest.TestCase):
    """Test cases for Timer."""
    
    def test_init(self):
        """Test initialization."""
        timer = Timer()
        self.assertFalse(timer.is_running())
        self.assertEqual(timer.get_elapsed(), 0.0)
    
    def test_start(self):
        """Test starting the timer."""
        timer = Timer()
        timer.start()
        self.assertTrue(timer.is_running())
    
    def test_stop(self):
        """Test stopping the timer."""
        timer = Timer()
        timer.start()
        time.sleep(0.05)
        elapsed = timer.stop()
        
        self.assertFalse(timer.is_running())
        self.assertGreater(elapsed, 0)
    
    def test_reset(self):
        """Test resetting the timer."""
        timer = Timer()
        timer.start()
        time.sleep(0.05)
        timer.reset()
        
        self.assertFalse(timer.is_running())
        self.assertEqual(timer.get_elapsed(), 0.0)
    
    def test_get_elapsed_while_running(self):
        """Test getting elapsed time while running."""
        timer = Timer()
        timer.start()
        time.sleep(0.05)
        
        elapsed = timer.get_elapsed()
        self.assertGreater(elapsed, 0)
        
        timer.stop()
    
    def test_get_formatted_time(self):
        """Test formatted time output."""
        timer = Timer()
        timer.start()
        time.sleep(1.1)
        
        formatted = timer.get_formatted_time()
        self.assertRegex(formatted, r'^\d{2}:\d{2}$')
        
        timer.stop()


class TestCountdownTimer(unittest.TestCase):
    """Test cases for CountdownTimer."""
    
    def test_init(self):
        """Test initialization."""
        timer = CountdownTimer(60)
        self.assertFalse(timer.is_running())
        self.assertEqual(timer.get_remaining(), 60)
    
    def test_start(self):
        """Test starting the countdown."""
        timer = CountdownTimer(60)
        timer.start()
        self.assertTrue(timer.is_running())
    
    def test_remaining_time(self):
        """Test remaining time."""
        timer = CountdownTimer(60)
        timer.start()
        time.sleep(0.1)
        
        remaining = timer.get_remaining()
        self.assertLess(remaining, 60)
        self.assertGreater(remaining, 59)
    
    def test_time_up(self):
        """Test time up condition."""
        timer = CountdownTimer(0.1)
        timer.start()
        time.sleep(0.15)
        
        self.assertTrue(timer.is_time_up())
    
    def test_callback(self):
        """Test callback on time up."""
        callback_called = [False]
        
        def on_time_up():
            callback_called[0] = True
        
        timer = CountdownTimer(0.1, on_time_up)
        timer.start()
        time.sleep(0.15)
        
        timer.check_time_up()
        self.assertTrue(callback_called[0])
    
    def test_get_formatted_remaining(self):
        """Test formatted remaining time."""
        timer = CountdownTimer(65)
        timer.start()
        
        formatted = timer.get_formatted_remaining()
        self.assertRegex(formatted, r'^\d{2}:\d{2}$')
    
    def test_stop(self):
        """Test stopping the countdown."""
        timer = CountdownTimer(60)
        timer.start()
        timer.stop()
        
        self.assertFalse(timer.is_running())


if __name__ == '__main__':
    unittest.main()
