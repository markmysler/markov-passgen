"""Case transformation utilities"""

from markov_passgen.transformers.text_cleaner import BaseTextCleaner


class CaseTransformer(BaseTextCleaner):
    """Transform text case (uppercase, lowercase, title case)"""
    
    def __init__(self, mode: str = "lower"):
        """Initialize case transformer
        
        Args:
            mode: Transformation mode - 'lower', 'upper', 'title', 'capitalize'
            
        Raises:
            ValueError: If mode is invalid
        """
        valid_modes = ['lower', 'upper', 'title', 'capitalize']
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {valid_modes}")
        self.mode = mode
    
    def clean(self, text: str) -> str:
        """Transform text case
        
        Args:
            text: Input text
            
        Returns:
            Transformed text
        """
        if not text:
            return text
        
        if self.mode == 'lower':
            return text.lower()
        elif self.mode == 'upper':
            return text.upper()
        elif self.mode == 'title':
            return text.title()
        elif self.mode == 'capitalize':
            return text.capitalize()
        
        return text
