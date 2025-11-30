"""Password generation using Markov chains"""

import random
from typing import List, Dict, Optional, Tuple


class PasswordGenerator:
    """Generate password candidates from n-gram model
    
    Single Responsibility: Generate passwords
    """
    
    def __init__(self, ngram_model: Dict[str, Dict[str, int]]):
        """Initialize generator with n-gram model
        
        Args:
            ngram_model: N-gram frequency dictionary
        """
        self._model = ngram_model
        self._n = len(next(iter(ngram_model.keys()))) if ngram_model else 0
        self._generation_count = 0
    
    def generate(self, count: int, length: int, seed: Optional[str] = None) -> List[str]:
        """Generate passwords
        
        Args:
            count: Number of passwords to generate
            length: Length of each password
            seed: Optional seed string to start generation
            
        Returns:
            List of generated passwords
            
        Raises:
            ValueError: If count < 0, length < 1, or seed not in model
        """
        if count < 0:
            raise ValueError("count must be >= 0")
        
        if count == 0:
            return []
        
        if length < 1:
            raise ValueError("length must be >= 1")
        
        if not self._model:
            raise ValueError("N-gram model is empty")
        
        passwords = []
        
        for _ in range(count):
            password = self._generate_one(length, seed)
            passwords.append(password)
            self._generation_count += 1
        
        return passwords
    
    def _generate_one(self, length: int, seed: Optional[str] = None) -> str:
        """Generate a single password
        
        Args:
            length: Target password length
            seed: Optional seed string
            
        Returns:
            Generated password
        """
        if seed:
            if seed not in self._model:
                # Try to find a prefix that exists in the model
                found = False
                for i in range(len(seed) - self._n + 1):
                    prefix = seed[i:i + self._n]
                    if prefix in self._model:
                        password = prefix
                        found = True
                        break
                
                if not found:
                    raise ValueError(f"Seed '{seed}' not found in model")
            else:
                password = seed
        else:
            # Random starting prefix
            password = random.choice(list(self._model.keys()))
        
        # Generate until we reach target length
        max_restarts = 10  # Maximum number of times to restart generation
        restarts = 0
        
        while len(password) < length:
            # Get the last n characters as prefix
            prefix = password[-self._n:]
            
            if prefix not in self._model:
                # If we can't continue, restart with a different prefix
                if restarts < max_restarts and length - len(password) > 1:
                    password = random.choice(list(self._model.keys()))
                    restarts += 1
                    continue
                else:
                    # If we're close to target or tried many times, pad with available chars
                    all_chars = set()
                    for next_chars in self._model.values():
                        all_chars.update(next_chars.keys())
                    while len(password) < length:
                        password += random.choice(list(all_chars))
                    break
            
            # Get possible next characters and their counts
            next_chars = self._model[prefix]
            
            # Weighted random choice
            chars = list(next_chars.keys())
            weights = list(next_chars.values())
            next_char = random.choices(chars, weights=weights, k=1)[0]
            
            password += next_char
        
        # Ensure exact length
        if len(password) < length:
            # Should never happen, but pad just in case
            all_chars = set()
            for next_chars in self._model.values():
                all_chars.update(next_chars.keys())
            while len(password) < length:
                password += random.choice(list(all_chars))
        
        # Trim to exact length first
        password = password[:length]
        
        # If password ends with whitespace, replace trailing whitespace with non-space chars
        while password and password[-1].isspace():
            # Get non-whitespace characters from model
            all_chars = set()
            for next_chars in self._model.values():
                all_chars.update(char for char in next_chars.keys() if not char.isspace())
            
            if all_chars:
                # Replace last character
                password = password[:-1] + random.choice(list(all_chars))
            else:
                # Fallback: use any character
                all_chars_fallback = set()
                for next_chars in self._model.values():
                    all_chars_fallback.update(next_chars.keys())
                if all_chars_fallback:
                    password = password[:-1] + random.choice(list(all_chars_fallback))
                break
        
        return password
    
    def generate_with_entropy(
        self, count: int, min_entropy: float
    ) -> List[Tuple[str, float]]:
        """Generate with entropy scores
        
        Note: This is a placeholder for Phase 2
        
        Args:
            count: Number of passwords
            min_entropy: Minimum entropy threshold
            
        Returns:
            List of (password, entropy) tuples
        """
        raise NotImplementedError("Entropy generation in Phase 2")
    
    def set_random_seed(self, seed: int) -> None:
        """Enable deterministic generation
        
        Args:
            seed: Random seed for reproducible results
        """
        random.seed(seed)
    
    def get_generation_stats(self) -> Dict:
        """Return generation statistics
        
        Returns:
            Dictionary with stats
        """
        return {
            "total_generated": self._generation_count,
            "model_size": len(self._model),
            "ngram_size": self._n
        }
