"""Corpus loading and validation"""

from typing import List, Dict, Optional


class CorpusLoader:
    """Load and validate text corpus from files or streams
    
    Single Responsibility: Load and validate text corpus
    """
    
    def __init__(self):
        self._last_corpus = ""
    
    def load_from_file(self, filepath: str, cleaner=None) -> str:
        """Load corpus from single file
        
        Args:
            filepath: Path to text file
            cleaner: Optional text cleaner instance for preprocessing
            
        Returns:
            File contents as string (optionally cleaned)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            UnicodeDecodeError: If file has invalid encoding
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply text cleaning if provided
        if cleaner is not None:
            content = cleaner.clean(content)
        
        self._last_corpus = content
        return content
    
    def load_from_files(self, filepaths: List[str], cleaner=None) -> str:
        """Load and merge multiple corpus files
        
        Args:
            filepaths: List of file paths
            cleaner: Optional text cleaner instance for preprocessing
            
        Returns:
            Merged corpus as string
            
        Raises:
            FileNotFoundError: If any file doesn't exist
        """
        corpora = []
        for filepath in filepaths:
            corpus = self.load_from_file(filepath, cleaner=cleaner)
            corpora.append(corpus)
        merged = " ".join(corpora)
        self._last_corpus = merged
        return merged
    
    def validate_corpus(self, text: str) -> bool:
        """Ensure corpus meets minimum requirements
        
        Args:
            text: Corpus text to validate
            
        Returns:
            True if corpus is valid (>= 100 characters), False otherwise
        """
        if not text:
            return False
        # Strip whitespace for counting
        stripped = text.strip()
        return len(stripped) >= 100
    
    def get_corpus_stats(self) -> Dict[str, int]:
        """Return character count, word count, unique chars
        
        Returns:
            Dictionary with corpus statistics
        """
        text = self._last_corpus.strip()
        words = text.split()
        unique_chars = set(text)
        
        return {
            "char_count": len(text),
            "word_count": len(words),
            "unique_chars": len(unique_chars)
        }
