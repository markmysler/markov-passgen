"""Base filter interface"""

from abc import ABC, abstractmethod
from typing import List


class BaseFilter(ABC):
    """Abstract base class for password filters"""
    
    @abstractmethod
    def filter(self, passwords: List[str]) -> List[str]:
        """Apply filter to password list
        
        Args:
            passwords: List of passwords to filter
            
        Returns:
            Filtered password list
        """
        pass
