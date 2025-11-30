"""Password transformation utilities"""

import random
import string
from abc import ABC, abstractmethod
from typing import List, Dict


class BasePasswordTransformer(ABC):
    """Abstract base class for password transformations"""
    
    @abstractmethod
    def transform(self, password: str) -> str:
        """Transform a password
        
        Args:
            password: Input password
            
        Returns:
            Transformed password
        """
        pass
    
    def transform_batch(self, passwords: List[str]) -> List[str]:
        """Transform multiple passwords
        
        Args:
            passwords: List of passwords
            
        Returns:
            List of transformed passwords
        """
        return [self.transform(pwd) for pwd in passwords]


class LeetSpeakTransformer(BasePasswordTransformer):
    """Transform passwords using leet speak substitutions
    
    Common substitutions:
    - a/A -> 4
    - e/E -> 3
    - i/I -> 1
    - o/O -> 0
    - s/S -> 5
    - t/T -> 7
    """
    
    def __init__(self, intensity: float = 0.5):
        """Initialize leet speak transformer
        
        Args:
            intensity: Probability of applying substitution (0.0 to 1.0)
        """
        if not 0.0 <= intensity <= 1.0:
            raise ValueError("Intensity must be between 0.0 and 1.0")
        
        self.intensity = intensity
        self.substitutions = {
            'a': '4', 'A': '4',
            'e': '3', 'E': '3',
            'i': '1', 'I': '1',
            'o': '0', 'O': '0',
            's': '5', 'S': '5',
            't': '7', 'T': '7',
            'g': '9', 'G': '9',
            'b': '8', 'B': '8'
        }
    
    def transform(self, password: str) -> str:
        """Apply leet speak transformation
        
        Args:
            password: Input password
            
        Returns:
            Leet speak transformed password
        """
        result = []
        for char in password:
            if char in self.substitutions and random.random() < self.intensity:
                result.append(self.substitutions[char])
            else:
                result.append(char)
        return ''.join(result)


class CaseVariationTransformer(BasePasswordTransformer):
    """Transform passwords with case variations
    
    Modes:
    - random: Random case for each letter
    - alternating: Alternate between upper and lower
    - capitalize: Capitalize first letter of each word
    """
    
    def __init__(self, mode: str = "random"):
        """Initialize case variation transformer
        
        Args:
            mode: Variation mode - 'random', 'alternating', 'capitalize'
            
        Raises:
            ValueError: If mode is invalid
        """
        valid_modes = ['random', 'alternating', 'capitalize']
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {valid_modes}")
        self.mode = mode
    
    def transform(self, password: str) -> str:
        """Apply case variation
        
        Args:
            password: Input password
            
        Returns:
            Case-varied password
        """
        if self.mode == 'random':
            return self._random_case(password)
        elif self.mode == 'alternating':
            return self._alternating_case(password)
        elif self.mode == 'capitalize':
            return self._capitalize_words(password)
        return password
    
    def _random_case(self, password: str) -> str:
        """Apply random case to each letter"""
        result = []
        for char in password:
            if char.isalpha():
                result.append(char.upper() if random.random() < 0.5 else char.lower())
            else:
                result.append(char)
        return ''.join(result)
    
    def _alternating_case(self, password: str) -> str:
        """Apply alternating case"""
        result = []
        upper = True
        for char in password:
            if char.isalpha():
                result.append(char.upper() if upper else char.lower())
                upper = not upper
            else:
                result.append(char)
        return ''.join(result)
    
    def _capitalize_words(self, password: str) -> str:
        """Capitalize first letter of each word"""
        words = password.split()
        return ' '.join(word.capitalize() for word in words)


class SubstitutionTransformer(BasePasswordTransformer):
    """Transform passwords using custom character substitutions"""
    
    def __init__(self, substitutions: Dict[str, str] = None, probability: float = 1.0):
        """Initialize substitution transformer
        
        Args:
            substitutions: Dictionary mapping characters to replacements
            probability: Probability of applying each substitution (0.0 to 1.0)
            
        Raises:
            ValueError: If probability is out of range
        """
        if not 0.0 <= probability <= 1.0:
            raise ValueError("Probability must be between 0.0 and 1.0")
        
        self.substitutions = substitutions or {}
        self.probability = probability
    
    def transform(self, password: str) -> str:
        """Apply custom substitutions
        
        Args:
            password: Input password
            
        Returns:
            Transformed password
        """
        result = []
        for char in password:
            if char in self.substitutions and random.random() < self.probability:
                result.append(self.substitutions[char])
            else:
                result.append(char)
        return ''.join(result)
    
    def add_substitution(self, from_char: str, to_char: str) -> None:
        """Add a character substitution
        
        Args:
            from_char: Character to replace
            to_char: Replacement character
        """
        self.substitutions[from_char] = to_char
    
    @staticmethod
    def special_chars_transformer(probability: float = 1.0) -> 'SubstitutionTransformer':
        """Create transformer that adds special characters
        
        Args:
            probability: Substitution probability
            
        Returns:
            Configured SubstitutionTransformer
        """
        substitutions = {
            'a': '@',
            's': '$',
            'i': '!',
            'l': '|'
        }
        return SubstitutionTransformer(substitutions, probability)


class TransformerChain(BasePasswordTransformer):
    """Chain multiple transformers together"""
    
    def __init__(self):
        """Initialize empty transformer chain"""
        self.transformers: List[BasePasswordTransformer] = []
    
    def add(self, transformer: BasePasswordTransformer) -> 'TransformerChain':
        """Add transformer to chain
        
        Args:
            transformer: Transformer to add
            
        Returns:
            Self for method chaining
        """
        self.transformers.append(transformer)
        return self
    
    def transform(self, password: str) -> str:
        """Apply all transformers in sequence
        
        Args:
            password: Input password
            
        Returns:
            Fully transformed password
        """
        result = password
        for transformer in self.transformers:
            result = transformer.transform(result)
        return result
    
    def clear(self) -> None:
        """Remove all transformers"""
        self.transformers.clear()
