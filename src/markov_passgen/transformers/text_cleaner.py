"""Text cleaning and preprocessing utilities"""

import re
import string
from abc import ABC, abstractmethod


class BaseTextCleaner(ABC):
    """Abstract base class for text cleaning operations"""
    
    @abstractmethod
    def clean(self, text: str) -> str:
        """Clean the input text
        
        Args:
            text: Input text to clean
            
        Returns:
            Cleaned text
        """
        pass


class TextCleaner(BaseTextCleaner):
    """Comprehensive text cleaning and preprocessing
    
    Supports:
    - Lowercase conversion
    - Punctuation removal
    - Digit removal
    - Whitespace normalization
    """
    
    def __init__(
        self,
        lowercase: bool = False,
        remove_punctuation: bool = False,
        remove_digits: bool = False,
        normalize_whitespace: bool = False
    ):
        """Initialize text cleaner
        
        Args:
            lowercase: Convert all text to lowercase
            remove_punctuation: Remove all punctuation marks
            remove_digits: Remove all digit characters
            normalize_whitespace: Normalize multiple spaces to single space
        """
        self.lowercase = lowercase
        self.remove_punctuation = remove_punctuation
        self.remove_digits = remove_digits
        self.normalize_whitespace = normalize_whitespace
    
    def clean(self, text: str) -> str:
        """Clean text according to configured options
        
        Args:
            text: Input text to clean
            
        Returns:
            Cleaned text
            
        Raises:
            ValueError: If text is empty after cleaning
        """
        if not text:
            return text
        
        result = text
        
        # Apply transformations in order
        if self.lowercase:
            result = result.lower()
        
        if self.remove_punctuation:
            result = self._remove_punctuation(result)
        
        if self.remove_digits:
            result = self._remove_digits(result)
        
        if self.normalize_whitespace:
            result = self._normalize_whitespace(result)
        
        # Trim leading/trailing whitespace
        result = result.strip()
        
        if not result:
            raise ValueError("Text is empty after cleaning")
        
        return result
    
    def _remove_punctuation(self, text: str) -> str:
        """Remove all punctuation marks
        
        Args:
            text: Input text
            
        Returns:
            Text without punctuation
        """
        # Create translation table to remove punctuation
        translator = str.maketrans('', '', string.punctuation)
        return text.translate(translator)
    
    def _remove_digits(self, text: str) -> str:
        """Remove all digit characters
        
        Args:
            text: Input text
            
        Returns:
            Text without digits
        """
        return ''.join(char for char in text if not char.isdigit())
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace (multiple spaces to single space)
        
        Args:
            text: Input text
            
        Returns:
            Text with normalized whitespace
        """
        # Replace multiple whitespace with single space
        return re.sub(r'\s+', ' ', text)
    
    @staticmethod
    def lowercase_only(text: str) -> str:
        """Convenience method: lowercase only
        
        Args:
            text: Input text
            
        Returns:
            Lowercased text
        """
        cleaner = TextCleaner(lowercase=True)
        return cleaner.clean(text)
    
    @staticmethod
    def remove_punctuation_only(text: str) -> str:
        """Convenience method: remove punctuation only
        
        Args:
            text: Input text
            
        Returns:
            Text without punctuation
        """
        cleaner = TextCleaner(remove_punctuation=True)
        return cleaner.clean(text)
    
    @staticmethod
    def remove_digits_only(text: str) -> str:
        """Convenience method: remove digits only
        
        Args:
            text: Input text
            
        Returns:
            Text without digits
        """
        cleaner = TextCleaner(remove_digits=True)
        return cleaner.clean(text)
    
    @staticmethod
    def normalize_whitespace_only(text: str) -> str:
        """Convenience method: normalize whitespace only
        
        Args:
            text: Input text
            
        Returns:
            Text with normalized whitespace
        """
        cleaner = TextCleaner(normalize_whitespace=True)
        return cleaner.clean(text)
