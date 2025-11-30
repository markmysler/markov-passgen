"""Unit tests for CorpusLoader"""

import pytest
import tempfile
import os
from markov_passgen.core.corpus_loader import CorpusLoader


class TestCorpusLoader:
    """Test cases for CorpusLoader class"""
    
    def test_load_valid_file(self):
        """Test loading a valid text file"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("This is a test corpus with enough text to be valid. " * 3)
            temp_path = f.name
        
        try:
            loader = CorpusLoader()
            text = loader.load_from_file(temp_path)
            assert len(text) > 0
            assert "test corpus" in text
        finally:
            os.unlink(temp_path)
    
    def test_load_nonexistent_file(self):
        """Test loading non-existent file raises FileNotFoundError"""
        loader = CorpusLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_from_file("nonexistent_file_xyz123.txt")
    
    def test_validate_valid_corpus(self):
        """Test validation of valid corpus"""
        loader = CorpusLoader()
        valid_text = "a" * 100  # 100 characters
        assert loader.validate_corpus(valid_text) is True
    
    def test_validate_empty_corpus(self):
        """Test validation of empty corpus returns False"""
        loader = CorpusLoader()
        assert loader.validate_corpus("") is False
    
    def test_validate_short_corpus(self):
        """Test validation of corpus shorter than 100 chars"""
        loader = CorpusLoader()
        short_text = "short"  # Only 5 characters
        assert loader.validate_corpus(short_text) is False
    
    def test_get_corpus_stats(self):
        """Test corpus statistics"""
        loader = CorpusLoader()
        test_text = "hello world test"
        loader._last_corpus = test_text
        
        stats = loader.get_corpus_stats()
        assert stats["char_count"] == 16
        assert stats["word_count"] == 3
        assert stats["unique_chars"] > 0
    
    def test_load_from_files_multiple(self):
        """Test loading and merging multiple files"""
        # Create two temporary files
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f1:
            f1.write("First corpus. " * 10)
            path1 = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f2:
            f2.write("Second corpus. " * 10)
            path2 = f2.name
        
        try:
            loader = CorpusLoader()
            merged = loader.load_from_files([path1, path2])
            assert "First corpus" in merged
            assert "Second corpus" in merged
        finally:
            os.unlink(path1)
            os.unlink(path2)
    
    def test_load_utf8_file(self):
        """Test loading file with UTF-8 special characters"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("Special chars: café, naïve, 日本語 " * 5)
            temp_path = f.name
        
        try:
            loader = CorpusLoader()
            text = loader.load_from_file(temp_path)
            assert "café" in text
            assert "naïve" in text
        finally:
            os.unlink(temp_path)
