"""N-gram model builder for Markov chains"""

from typing import Dict
import json


class NGramBuilder:
    """Build n-gram frequency dictionary from corpus
    
    Single Responsibility: Build n-gram model
    """
    
    def __init__(self):
        self._model: Dict[str, Dict[str, int]] = {}
    
    def build(self, text: str, n: int = 2) -> Dict[str, Dict[str, int]]:
        """Create n-gram model
        
        Args:
            text: Input text corpus
            n: N-gram size (default: 2 for bigrams, range: 2-5)
            
        Returns:
            N-gram frequency dictionary: {"prefix": {"next_char": count, ...}}
            
        Raises:
            ValueError: If n < 2 or n > 5, text is empty, or text shorter than n
        """
        if n < 2 or n > 5:
            raise ValueError("n must be between 2 and 5")
        
        if not text:
            raise ValueError("Text corpus cannot be empty")
        
        if len(text) < n:
            raise ValueError(f"Text length ({len(text)}) must be >= n ({n})")
        
        model: Dict[str, Dict[str, int]] = {}
        
        # Build n-gram model by sliding window
        for i in range(len(text) - n):
            prefix = text[i:i + n]
            next_char = text[i + n]
            
            if prefix not in model:
                model[prefix] = {}
            
            if next_char not in model[prefix]:
                model[prefix][next_char] = 0
            
            model[prefix][next_char] += 1
        
        self._model = model
        return model
    
    def get_next_char_probabilities(self, prefix: str) -> Dict[str, float]:
        """Get weighted next char options
        
        Args:
            prefix: N-gram prefix to look up
            
        Returns:
            Dictionary of character to probability: {"a": 0.5, "b": 0.3, ...}
            Empty dict if prefix not found
        """
        if prefix not in self._model:
            return {}
        
        char_counts = self._model[prefix]
        total = sum(char_counts.values())
        
        probabilities = {
            char: count / total 
            for char, count in char_counts.items()
        }
        
        return probabilities
    
    def add_to_model(self, text: str) -> None:
        """Incrementally update model
        
        Args:
            text: Additional text to add to model
        """
        # Get n from existing model (use first key length)
        if not self._model:
            raise ValueError("Model not initialized. Call build() first.")
        
        n = len(next(iter(self._model.keys())))
        
        # Build new model and merge
        for i in range(len(text) - n):
            prefix = text[i:i + n]
            next_char = text[i + n]
            
            if prefix not in self._model:
                self._model[prefix] = {}
            
            if next_char not in self._model[prefix]:
                self._model[prefix][next_char] = 0
            
            self._model[prefix][next_char] += 1
    
    def save_model(self, filepath: str) -> None:
        """Serialize model to JSON
        
        Args:
            filepath: Path to save model
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self._model, f, indent=2)
    
    def load_model(self, filepath: str) -> Dict[str, Dict[str, int]]:
        """Deserialize model from JSON
        
        Args:
            filepath: Path to model file
            
        Returns:
            Loaded model dictionary
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            self._model = json.load(f)
        return self._model
