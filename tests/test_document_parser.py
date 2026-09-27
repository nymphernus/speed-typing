"""
Tests for document_parser module.
"""

import os
import tempfile
import unittest
from src.document_parser import extract_text, split_into_words, _clean_text


class TestDocumentParser(unittest.TestCase):
    """Test cases for document parser."""
    
    def test_clean_text_english(self):
        """Test cleaning English text."""
        text = "Hello, World! This is a test."
        result = _clean_text(text)
        self.assertEqual(result, "Hello, World! This is a test.")
    
    def test_clean_text_russian(self):
        """Test cleaning Russian text."""
        text = "Привет, мир! Это тест."
        result = _clean_text(text)
        self.assertEqual(result, "Привет, мир! Это тест.")
    
    def test_clean_text_mixed(self):
        """Test cleaning mixed English/Russian text."""
        text = "Hello Привет World мир"
        result = _clean_text(text)
        self.assertEqual(result, "Hello Привет World мир")
    
    def test_clean_text_removes_special_chars(self):
        """Test that special characters are removed."""
        text = "Hello\x00World\x01Test"
        result = _clean_text(text)
        self.assertNotIn('\x00', result)
        self.assertNotIn('\x01', result)
    
    def test_clean_text_normalizes_whitespace(self):
        """Test whitespace normalization."""
        text = "Hello    World\n\n\n\nTest"
        result = _clean_text(text)
        self.assertNotIn('    ', result)
        self.assertNotIn('\n\n\n', result)
    
    def test_split_into_words_english(self):
        """Test splitting English text into words."""
        text = "The quick brown fox"
        words = split_into_words(text)
        self.assertEqual(words, ["The", "quick", "brown", "fox"])
    
    def test_split_into_words_russian(self):
        """Test splitting Russian text into words."""
        text = "Съешь же ещё этих мягких французских булок"
        words = split_into_words(text)
        self.assertEqual(words, ["Съешь", "же", "ещё", "этих", "мягких", "французских", "булок"])
    
    def test_split_into_words_with_punctuation(self):
        """Test splitting text with punctuation."""
        text = "Hello, world! How are you?"
        words = split_into_words(text)
        self.assertEqual(words, ["Hello", "world", "How", "are", "you"])
    
    def test_split_into_words_empty(self):
        """Test splitting empty text."""
        words = split_into_words("")
        self.assertEqual(words, [])
    
    def test_extract_from_txt(self):
        """Test extracting text from .txt file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("Hello World\nПривет мир")
            filepath = f.name
        
        try:
            result = extract_text(filepath)
            self.assertIn("Hello", result)
            self.assertIn("World", result)
            self.assertIn("Привет", result)
            self.assertIn("мир", result)
        finally:
            os.unlink(filepath)
    
    def test_extract_from_nonexistent_file(self):
        """Test extracting from non-existent file."""
        with self.assertRaises(FileNotFoundError):
            extract_text("nonexistent_file.txt")
    
    def test_extract_from_unsupported_format(self):
        """Test extracting from unsupported format."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            filepath = f.name
        
        try:
            with self.assertRaises(ValueError):
                extract_text(filepath)
        finally:
            os.unlink(filepath)
    
    def test_extract_from_docx(self):
        """Test extracting text from .docx file."""
        try:
            from docx import Document
        except ImportError:
            self.skipTest("python-docx not installed")
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
            filepath = f.name
        
        try:
            doc = Document()
            doc.add_paragraph("Hello World")
            doc.add_paragraph("Привет мир")
            doc.save(filepath)
            
            result = extract_text(filepath)
            self.assertIn("Hello", result)
            self.assertIn("World", result)
            self.assertIn("Привет", result)
            self.assertIn("мир", result)
        finally:
            os.unlink(filepath)


if __name__ == '__main__':
    unittest.main()
