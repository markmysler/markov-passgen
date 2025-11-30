"""Length-based password filtering"""

from typing import List
from markov_passgen.filters.base_filter import BaseFilter


class LengthFilter(BaseFilter):
    """Filter by password length
    
    Single Responsibility: Filter passwords by length constraints
    """
    
    def __init__(self, min_length: int = 0, max_length: int = 1000):
        """Initialize filter
        
        Args:
            min_length: Minimum password length (inclusive)
            max_length: Maximum password length (inclusive)
            
        Raises:
            ValueError: If min_length > max_length or negative values
        """
        if min_length < 0:
            raise ValueError("min_length cannot be negative")
        
        if max_length < 0:
            raise ValueError("max_length cannot be negative")
        
        if min_length > max_length:
            raise ValueError("min_length cannot be greater than max_length")
        
        self.min_length = min_length
        self.max_length = max_length
    
    def filter(self, passwords: List[str]) -> List[str]:
        """Filter passwords by length
        
        Args:
            passwords: List of passwords to filter
            
        Returns:
            Passwords that meet length requirements
        """
        return [
            pwd for pwd in passwords
            if self.min_length <= len(pwd) <= self.max_length
        ]
