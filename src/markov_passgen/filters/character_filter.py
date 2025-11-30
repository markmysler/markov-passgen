"""Character-based password filtering"""

import re
from typing import List, Optional
from markov_passgen.filters.base_filter import BaseFilter


class CharacterFilter(BaseFilter):
    """Filter by character requirements
    
    Single Responsibility: Filter passwords by character composition
    """
    
    def __init__(
        self,
        require_digits: bool = False,
        require_uppercase: bool = False,
        require_lowercase: bool = False,
        require_special: bool = False,
        must_include: Optional[str] = None,
        must_not_include: Optional[str] = None
    ):
        """Initialize filter
        
        Args:
            require_digits: Must contain at least one digit
            require_uppercase: Must contain at least one uppercase letter
            require_lowercase: Must contain at least one lowercase letter
            require_special: Must contain at least one special character
            must_include: Characters that must be present
            must_not_include: Characters that must not be present
        """
        self.require_digits = require_digits
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_special = require_special
        self.must_include = must_include or ""
        self.must_not_include = must_not_include or ""
    
    def filter(self, passwords: List[str]) -> List[str]:
        """Filter passwords by character requirements
        
        Args:
            passwords: List of passwords to filter
            
        Returns:
            Passwords that meet all character requirements
        """
        filtered = []
        
        for pwd in passwords:
            if self._meets_requirements(pwd):
                filtered.append(pwd)
        
        return filtered
    
    def _meets_requirements(self, password: str) -> bool:
        """Check if password meets all requirements
        
        Args:
            password: Password to check
            
        Returns:
            True if all requirements are met
        """
        # Check digit requirement
        if self.require_digits and not any(c.isdigit() for c in password):
            return False
        
        # Check uppercase requirement
        if self.require_uppercase and not any(c.isupper() for c in password):
            return False
        
        # Check lowercase requirement
        if self.require_lowercase and not any(c.islower() for c in password):
            return False
        
        # Check special character requirement
        if self.require_special and not any(not c.isalnum() for c in password):
            return False
        
        # Check must_include characters
        if self.must_include:
            for char in self.must_include:
                if char not in password:
                    return False
        
        # Check must_not_include characters
        if self.must_not_include:
            for char in self.must_not_include:
                if char in password:
                    return False
        
        return True
    
    def require_digits_filter(self, passwords: List[str]) -> List[str]:
        """Filter to only passwords with digits
        
        Args:
            passwords: List of passwords
            
        Returns:
            Passwords containing at least one digit
        """
        return [pwd for pwd in passwords if any(c.isdigit() for c in pwd)]
    
    def require_uppercase_filter(self, passwords: List[str]) -> List[str]:
        """Filter to only passwords with uppercase letters
        
        Args:
            passwords: List of passwords
            
        Returns:
            Passwords containing at least one uppercase letter
        """
        return [pwd for pwd in passwords if any(c.isupper() for c in pwd)]
    
    def require_special_filter(self, passwords: List[str]) -> List[str]:
        """Filter to only passwords with special characters
        
        Args:
            passwords: List of passwords
            
        Returns:
            Passwords containing at least one special character
        """
        return [pwd for pwd in passwords if any(not c.isalnum() for c in pwd)]
