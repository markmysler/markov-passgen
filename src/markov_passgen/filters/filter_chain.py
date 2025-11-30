"""Filter chain for composable filtering"""

from typing import List
from markov_passgen.filters.base_filter import BaseFilter


class FilterChain:
    """Apply multiple filters in sequence
    
    Single Responsibility: Compose and apply multiple filters
    """
    
    def __init__(self):
        """Initialize empty filter chain"""
        self.filters: List[BaseFilter] = []
    
    def add_filter(self, filter_obj: BaseFilter) -> 'FilterChain':
        """Add filter to chain
        
        Args:
            filter_obj: Filter to add
            
        Returns:
            Self for method chaining
        """
        self.filters.append(filter_obj)
        return self
    
    def apply(self, passwords: List[str]) -> List[str]:
        """Apply all filters in sequence
        
        Args:
            passwords: List of passwords to filter
            
        Returns:
            Passwords that pass all filters
        """
        result = passwords
        
        for filter_obj in self.filters:
            result = filter_obj.filter(result)
            
            # Early exit if no passwords remain
            if not result:
                break
        
        return result
    
    def clear(self) -> None:
        """Remove all filters from chain"""
        self.filters.clear()
    
    def __len__(self) -> int:
        """Get number of filters in chain"""
        return len(self.filters)
