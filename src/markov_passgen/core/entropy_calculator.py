"""Password entropy calculation"""

import math
from typing import Dict, Mapping, Set


class EntropyCalculator:
    """Calculate password entropy scores

    Single Responsibility: Calculate entropy metrics

    Three different measures, easy to mix up:

    - calculate_shannon_entropy: bits per character of the string's own
      letter distribution. Bounded by log2(length) (about 3.6 for 12
      characters); says nothing about how guessable the string is.
    - calculate_markov_entropy: average bits per character the model needs
      to produce the string. Comparable across lengths.
    - calculate_markov_bits: total bits for the whole string under the
      model, i.e. -log2 of its probability. The meaningful "how surprising
      is this candidate to the model" score: higher is less predictable.
    """

    def calculate_shannon_entropy(self, password: str) -> float:
        """Calculate Shannon entropy

        Measures how evenly the string uses its own characters (bits per
        character), not how hard it is to guess.
        Formula: -Σ(p(x) * log2(p(x)))

        Args:
            password: Password string to analyze

        Returns:
            Shannon entropy in bits

        Raises:
            ValueError: If password is empty
        """
        if not password:
            raise ValueError("Password cannot be empty")

        # Count character frequencies
        char_counts: Dict[str, int] = {}
        for char in password:
            char_counts[char] = char_counts.get(char, 0) + 1

        # Calculate probabilities and entropy
        length = len(password)
        entropy = 0.0

        for count in char_counts.values():
            probability = count / length
            entropy -= probability * math.log2(probability)

        return entropy

    def calculate_markov_entropy(self, password: str, ngram_model: Mapping[str, Mapping[str, float]]) -> float:
        """Calculate Markov-based entropy (average bits per character)

        Average surprisal per transition under the n-gram model: higher means
        less predictable per character. For a whole-string score use
        calculate_markov_bits.

        Args:
            password: Password string to analyze
            ngram_model: N-gram frequency dictionary

        Returns:
            Markov entropy in bits

        Raises:
            ValueError: If password is empty or model is empty
        """
        if not password:
            raise ValueError("Password cannot be empty")

        if not ngram_model:
            raise ValueError("N-gram model cannot be empty")

        # Get n from model
        n = len(next(iter(ngram_model.keys())))

        if len(password) < n:
            # For short passwords, fall back to Shannon entropy
            return self.calculate_shannon_entropy(password)

        entropy = 0.0
        transitions = 0

        # Calculate entropy for each transition
        for i in range(len(password) - n):
            prefix = password[i:i + n]
            next_char = password[i + n]

            if prefix in ngram_model:
                next_chars = ngram_model[prefix]
                total = sum(next_chars.values())

                if next_char in next_chars:
                    probability = next_chars[next_char] / total
                    entropy -= math.log2(probability)
                    transitions += 1
                else:
                    # Character not in model - high entropy (assume uniform dist)
                    # Use log2 of total possible chars as estimate
                    all_chars: Set[str] = set()
                    for chars_dict in ngram_model.values():
                        all_chars.update(chars_dict.keys())
                    entropy += math.log2(len(all_chars))
                    transitions += 1
            else:
                # Prefix not in model - high entropy
                all_chars = set()
                for chars_dict in ngram_model.values():
                    all_chars.update(chars_dict.keys())
                entropy += math.log2(len(all_chars))
                transitions += 1

        # Return average entropy per transition
        if transitions > 0:
            return entropy / transitions
        else:
            return self.calculate_shannon_entropy(password)

    def calculate_markov_bits(self, password: str, ngram_model: Mapping[str, Mapping[str, float]]) -> float:
        """Total bits for the whole string under the model: -log2 P(password)

        Uses the same back-off as generation, so a string the model can't
        produce directly still gets a finite score. For a line-mode model
        the probability includes starting and ending where the string does.

        Args:
            password: String to score
            ngram_model: N-gram model (NGramBuilder.build or build_lines)

        Returns:
            Bits (higher = less likely under the model)

        Raises:
            ValueError: If password or model is empty
        """
        from markov_passgen.core.generator import PasswordGenerator
        from markov_passgen.core.ngram_builder import END, START, is_line_model

        if not password:
            raise ValueError("Password cannot be empty")
        if not ngram_model:
            raise ValueError("N-gram model cannot be empty")

        generator = PasswordGenerator(ngram_model)
        n = len(next(iter(ngram_model.keys())))
        line_mode = is_line_model(ngram_model)

        if line_mode:
            context, steps = START * n, list(password) + [END]
        else:
            # A stream has no start: score what follows the first n characters
            context, steps = password[:n], list(password[n:])

        bits = 0.0
        for char in steps:
            distribution = generator._distribution(context[-n:], allow_end=line_mode)
            weight = distribution.get(char, 0.0)
            if weight <= 0:
                # Never seen even as a single character: charge a uniform pick
                bits += math.log2(len(distribution) + 1)
            else:
                bits -= math.log2(weight / sum(distribution.values()))
            context += char
        return bits

    def estimate_crack_time(self, password: str, attempts_per_second: int = 1_000_000_000) -> str:
        """Estimate crack time in human-readable format

        Args:
            password: Password to analyze
            attempts_per_second: Hash rate (default: 1 billion/sec)

        Returns:
            Human-readable time estimate (e.g., "2.5 years", "3 centuries")
        """
        if not password:
            raise ValueError("Password cannot be empty")

        # Calculate character space
        has_lowercase = any(c.islower() for c in password)
        has_uppercase = any(c.isupper() for c in password)
        has_digits = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)

        charset_size = 0
        if has_lowercase:
            charset_size += 26
        if has_uppercase:
            charset_size += 26
        if has_digits:
            charset_size += 10
        if has_special:
            charset_size += 32  # Common special chars

        if charset_size == 0:
            charset_size = 1

        # Total combinations
        combinations = charset_size ** len(password)

        # Average time to crack (half the keyspace)
        seconds = (combinations / 2) / attempts_per_second

        # Convert to human-readable format
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            return f"{seconds / 60:.1f} minutes"
        elif seconds < 86400:
            return f"{seconds / 3600:.1f} hours"
        elif seconds < 31536000:
            return f"{seconds / 86400:.1f} days"
        elif seconds < 3153600000:  # 100 years
            return f"{seconds / 31536000:.1f} years"
        elif seconds < 31536000000:  # 1000 years
            return f"{seconds / 3153600000:.1f} centuries"
        else:
            return f"{seconds / 31536000000:.1f} millennia"
