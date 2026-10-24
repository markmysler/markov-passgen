"""Password generation using Markov chains"""

import random
from typing import Dict, List, Mapping, Optional, Set, Tuple

from markov_passgen.core.ngram_builder import END, START, NGramModel, is_line_model

# Upper bound for a line-mode candidate when no max_length is given
DEFAULT_MAX_LENGTH = 64

Distribution = Dict[str, float]


class PasswordGenerator:
    """Generate password candidates from n-gram model

    Single Responsibility: Generate passwords

    Works with both kinds of model NGramBuilder makes:

    - **line mode** (build_lines): each candidate starts like an entry of the
      corpus and ends where the model says entries end, so its length comes
      from the data (within min_length/max_length), unless an exact length is
      requested.
    - **stream mode** (build): text read as one stream has no ends, so every
      candidate has the requested length (12 if none is given).

    When the current context never occurred in the corpus, the generator
    backs off to shorter contexts (down to single-character frequencies)
    instead of padding with uniformly random characters.
    """

    def __init__(self, ngram_model: NGramModel):
        """Initialize generator with n-gram model

        Args:
            ngram_model: N-gram frequency dictionary
        """
        self._model = ngram_model
        self._n = len(next(iter(ngram_model.keys()))) if ngram_model else 0
        self._line_mode = bool(ngram_model) and is_line_model(ngram_model)
        self._generation_count = 0
        # Lower-order distributions for back-off, built on first use
        self._backoff: Optional[List[Dict[str, Distribution]]] = None

    def generate(self, count: int, length: Optional[int] = None, seed: Optional[str] = None,
                 transformer=None, min_length: Optional[int] = None,
                 max_length: Optional[int] = None) -> List[str]:
        """Generate passwords

        Args:
            count: Number of passwords to generate
            length: Exact length of each password. Line-mode models use the
                lengths in the data when this is None; stream-mode models
                default to 12.
            seed: Optional seed string to start generation
            transformer: Optional password transformer to apply
            min_length: Shortest candidate (line-mode models)
            max_length: Longest candidate (line-mode models; default 64)

        Returns:
            List of generated passwords

        Raises:
            ValueError: If count < 0, a length is < 1, min_length > max_length,
                or (stream mode) seed not in model
        """
        if count < 0:
            raise ValueError("count must be >= 0")

        if count == 0:
            return []

        if length is not None and length < 1:
            raise ValueError("length must be >= 1")
        if min_length is not None and min_length < 1:
            raise ValueError("min_length must be >= 1")
        if max_length is not None and max_length < 1:
            raise ValueError("max_length must be >= 1")
        if min_length is not None and max_length is not None and min_length > max_length:
            raise ValueError("min_length must be <= max_length")

        if not self._model:
            raise ValueError("N-gram model is empty")

        passwords = []

        for _ in range(count):
            if self._line_mode:
                password = self._generate_line(length, min_length, max_length, seed)
            else:
                password = self._generate_one(length if length is not None else 12, seed)

            # Apply transformer if provided
            if transformer is not None:
                password = transformer.transform(password)

            passwords.append(password)
            self._generation_count += 1

        return passwords

    def _generate_line(self, length: Optional[int], min_length: Optional[int],
                       max_length: Optional[int], seed: Optional[str]) -> str:
        """Generate one candidate from a line-mode model

        Samples until the model emits END, never before min_length and never
        past max_length (both equal to length when an exact length is set).
        """
        low = length if length is not None else (min_length or 1)
        high = length if length is not None else (max_length or DEFAULT_MAX_LENGTH)
        high = max(high, low)

        password = seed or ""
        context = START * self._n + password
        while len(password) < high:
            distribution = self._distribution(context[-self._n:], allow_end=len(password) >= low)
            next_char = self._choose(distribution)
            if next_char == END:
                break
            password += next_char
            context += next_char
        return password[:high]

    def _generate_one(self, length: int, seed: Optional[str] = None) -> str:
        """Generate a single password from a stream-mode model

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

        while len(password) < length:
            password += self._choose(self._distribution(password[-self._n:], allow_end=False))

        # Trim to exact length first
        password = password[:length]

        # Replace ALL leading and trailing whitespace with non-space chars
        # Get non-whitespace characters from model once
        all_nonspace_chars: Set[str] = set()
        for next_chars in self._model.values():
            all_nonspace_chars.update(char for char in next_chars.keys() if not char.isspace())

        if not all_nonspace_chars:
            # Fallback: use any characters if no non-space chars found
            all_nonspace_chars = set()
            for next_chars in self._model.values():
                all_nonspace_chars.update(next_chars.keys())

        # Replace all leading and trailing spaces
        if all_nonspace_chars:
            # Replace leading spaces
            while password and password[0].isspace():
                password = random.choice(list(all_nonspace_chars)) + password[1:]
            # Replace trailing spaces
            while password and password[-1].isspace():
                password = password[:-1] + random.choice(list(all_nonspace_chars))

        return password

    # ── Next-character distributions ─────────────────────────────────────

    def _distribution(self, context: str, allow_end: bool) -> Distribution:
        """What can follow context, backing off to shorter contexts

        Tries the full n-character context first, then its last n-1, n-2, ...
        characters, and finally plain character frequencies. A level that
        offers nothing usable (e.g. only END when END isn't allowed yet) is
        skipped.
        """
        candidates: List[Optional[Mapping[str, float]]] = [self._model.get(context)]
        tables = self._backoff_tables()
        for k in range(min(len(context), self._n) - 1, -1, -1):
            candidates.append(tables[k].get(context[len(context) - k:] if k else ""))
        for distribution in candidates:
            if not distribution:
                continue
            usable = {c: w for c, w in distribution.items() if allow_end or c != END}
            if usable:
                return usable
        raise ValueError("The model has no characters to generate from")

    def _backoff_tables(self) -> List[Dict[str, Distribution]]:
        """Distributions for contexts shorter than n, summed from the model

        tables[k][suffix] holds what follows contexts ending with that
        k-character suffix; tables[0][""] is the overall character frequency.
        """
        if self._backoff is None:
            tables: List[Dict[str, Distribution]] = [{} for _ in range(self._n)]
            for prefix, followers in self._model.items():
                for k in range(self._n):
                    suffix = prefix[len(prefix) - k:] if k else ""
                    merged = tables[k].setdefault(suffix, {})
                    for char, weight in followers.items():
                        merged[char] = merged.get(char, 0) + weight
            self._backoff = tables
        return self._backoff

    @staticmethod
    def _choose(distribution: Distribution) -> str:
        chars = list(distribution.keys())
        return random.choices(chars, weights=list(distribution.values()), k=1)[0]

    def generate_with_entropy(
        self, count: int, min_entropy: float, max_attempts: int = 10000
    ) -> List[Tuple[str, float]]:
        """Generate with entropy scores

        Args:
            count: Number of passwords
            min_entropy: Minimum entropy threshold
            max_attempts: Maximum generation attempts

        Returns:
            List of (password, entropy) tuples

        Raises:
            ValueError: If unable to generate enough passwords with min entropy
        """
        from markov_passgen.core.entropy_calculator import EntropyCalculator

        calculator = EntropyCalculator()
        results: List[Tuple[str, float]] = []
        attempts = 0

        # Generate passwords until we have enough or hit max attempts
        while len(results) < count and attempts < max_attempts:
            # Generate with varied lengths to increase entropy variance
            length = 12 + (attempts % 8)  # Length 12-19
            passwords = self.generate(1, length)

            for pwd in passwords:
                entropy = calculator.calculate_markov_entropy(pwd, self._model)
                if entropy >= min_entropy:
                    results.append((pwd, entropy))
                    if len(results) >= count:
                        break

            attempts += 1

        if len(results) < count:
            raise ValueError(
                f"Unable to generate {count} passwords with min entropy {min_entropy}. "
                f"Only generated {len(results)} after {attempts} attempts."
            )

        return results[:count]

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
