"""
Document parser module.
Extracts text from .docx, .doc, and .txt files.
Keeps only English and Russian text.
"""

import re
from pathlib import Path


def extract_text(filepath: str) -> str:
    """
    Extract text from a document file.
    
    Supports: .docx, .doc, .txt
    
    Args:
        filepath: Path to the document file.
        
    Returns:
        Extracted text containing only English and Russian characters.
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file format is not supported.
    """
    path = Path(filepath)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    suffix = path.suffix.lower()
    
    if suffix == '.docx':
        return _extract_from_docx(filepath)
    elif suffix == '.doc':
        return _extract_from_doc(filepath)
    elif suffix == '.txt':
        return _extract_from_txt(filepath)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def _extract_from_docx(filepath: str) -> str:
    """Extract text from .docx file using python-docx."""
    from docx import Document
    
    doc = Document(filepath)
    paragraphs = [para.text for para in doc.paragraphs]
    full_text = '\n'.join(paragraphs)
    
    return _clean_text(full_text)


def _extract_from_doc(filepath: str) -> str:
    """Extract text from .doc file using olefile."""
    import olefile
    
    ole = olefile.OleFileIO(filepath)
    
    try:
        # Read the WordDocument stream
        word_stream = ole.openstream('WordDocument').read()
        
        # Try UTF-16LE first (most common for modern .doc files)
        text = _try_decode(word_stream, 'utf-16-le')
        if text:
            return _clean_text(text)
        
        # Try CP1251 (Russian encoding)
        text = _try_decode(word_stream, 'cp1251')
        if text:
            return _clean_text(text)
        
        # Fallback: latin-1
        text = word_stream.decode('latin-1', errors='ignore')
        return _clean_text(text)
    finally:
        ole.close()


def _extract_from_txt(filepath: str) -> str:
    """Extract text from .txt file."""
    # Try UTF-8 first, then CP1251
    for encoding in ['utf-8', 'cp1251', 'latin-1']:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                text = f.read()
            return _clean_text(text)
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    # Fallback
    with open(filepath, 'r', errors='ignore') as f:
        text = f.read()
    return _clean_text(text)


def _try_decode(data: bytes, encoding: str) -> str | None:
    """Try to decode bytes with given encoding. Returns None if result is not readable."""
    try:
        text = data.decode(encoding, errors='ignore')
        # Check if the result contains reasonable text
        sample = text[:2000]
        if not sample:
            return None
        
        # Count printable characters
        printable = sum(1 for c in sample if c.isprintable() or c in '\n\r\t')
        ratio = printable / len(sample) if sample else 0
        
        if ratio > 0.6:
            return text
        return None
    except (UnicodeDecodeError, LookupError):
        return None


def _clean_text(text: str) -> str:
    """
    Clean text by keeping only English, Russian, digits, and basic punctuation.
    
    Args:
        text: Raw text.
        
    Returns:
        Cleaned text.
    """
    # Keep: ASCII printable, Cyrillic (Russian), basic punctuation
    # Remove: control characters, special symbols, etc.
    allowed = re.compile(r'[^a-zA-Zа-яА-ЯёЁ0-9\s.,!?;:\'\"()\-\n\r\t]')
    cleaned = allowed.sub('', text)
    
    # Normalize whitespace
    cleaned = re.sub(r' {2,}', ' ', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    cleaned = re.sub(r'[ \t]+\n', '\n', cleaned)
    
    return cleaned.strip()


def split_into_words(text: str) -> list[str]:
    """
    Split text into words, keeping only English and Russian words.
    
    Args:
        text: Input text.
        
    Returns:
        List of words.
    """
    # Split by whitespace
    raw_words = text.split()
    
    words = []
    for raw_word in raw_words:
        # Remove punctuation from word boundaries
        cleaned = re.sub(r'^[^a-zA-Zа-яА-ЯёЁ0-9]+|[^a-zA-Zа-яА-ЯёЁ0-9]+$', '', raw_word)
        if cleaned:
            words.append(cleaned)
    
    return words
