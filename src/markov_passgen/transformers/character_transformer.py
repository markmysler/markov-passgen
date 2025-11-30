"""Character filtering and transformation utilities"""

from markov_passgen.transformers.text_cleaner import BaseTextCleaner


class CharacterTransformer(BaseTextCleaner):
    """Filter text to include only specific character types"""
    
    def __init__(
        self,
        allow_letters: bool = True,
        allow_digits: bool = True,
        allow_spaces: bool = True,
        allow_punctuation: bool = True
    ):
        """Initialize character transformer
        
        Args:
            allow_letters: Keep alphabetic characters
            allow_digits: Keep digit characters
            allow_spaces: Keep space characters
            allow_punctuation: Keep punctuation characters
        """
        self.allow_letters = allow_letters
        self.allow_digits = allow_digits
        self.allow_spaces = allow_spaces
        self.allow_punctuation = allow_punctuation
    
    def clean(self, text: str) -> str:
        """Filter text to allowed characters
        
        Args:
            text: Input text
            
        Returns:
            Filtered text
            
        Raises:
            ValueError: If text is empty after filtering
        """
        if not text:
            return text
        
        result = []
        for char in text:
            if self.allow_letters and char.isalpha():
                result.append(char)
            elif self.allow_digits and char.isdigit():
                result.append(char)
            elif self.allow_spaces and char.isspace():
                result.append(char)
            elif self.allow_punctuation and not char.isalnum() and not char.isspace():
                result.append(char)
        
        filtered = ''.join(result)
        
        if not filtered:
            raise ValueError("Text is empty after filtering")
        
        return filtered
    
    @staticmethod
    def letters_only(text: str) -> str:
        """Keep only letters
        
        Args:
            text: Input text
            
        Returns:
            Text with only letters
        """
        transformer = CharacterTransformer(
            allow_letters=True,
            allow_digits=False,
            allow_spaces=False,
            allow_punctuation=False
        )
        return transformer.clean(text)
    
    @staticmethod
    def alphanumeric_only(text: str) -> str:
        """Keep only letters and digits
        
        Args:
            text: Input text
            
        Returns:
            Text with only letters and digits
        """
        transformer = CharacterTransformer(
            allow_letters=True,
            allow_digits=True,
            allow_spaces=False,
            allow_punctuation=False
        )
        return transformer.clean(text)
