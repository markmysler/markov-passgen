"""Multi-corpus management and weighting"""

from typing import Dict, List, Optional

from markov_passgen.core.corpus_loader import CorpusLoader


class MultiCorpusManager:
    """Manage multiple corpus sources with optional weighting

    Allows loading multiple corpora and combining them with configurable
    weights to control the influence of each source on the n-gram model.
    """

    def __init__(self):
        """Initialize multi-corpus manager"""
        self._loader = CorpusLoader()
        self._corpora: Dict[str, str] = {}
        self._weights: Dict[str, float] = {}

    def add_corpus(self, name: str, filepath: str, weight: float = 1.0, cleaner=None) -> None:
        """Add a corpus source

        Args:
            name: Unique identifier for this corpus
            filepath: Path to corpus file
            weight: Relative weight for this corpus (default 1.0)
            cleaner: Optional text cleaner to apply

        Raises:
            ValueError: If weight is not positive or name already exists
            FileNotFoundError: If file doesn't exist
        """
        if weight <= 0:
            raise ValueError("Weight must be positive")

        if name in self._corpora:
            raise ValueError(f"Corpus '{name}' already exists")

        # Load corpus
        corpus_text = self._loader.load_from_file(filepath, cleaner=cleaner)

        # Store corpus and weight
        self._corpora[name] = corpus_text
        self._weights[name] = weight

    def add_corpus_text(self, name: str, text: str, weight: float = 1.0) -> None:
        """Add corpus from text directly

        Args:
            name: Unique identifier for this corpus
            text: Corpus text
            weight: Relative weight for this corpus (default 1.0)

        Raises:
            ValueError: If weight is not positive or name already exists
        """
        if weight <= 0:
            raise ValueError("Weight must be positive")

        if name in self._corpora:
            raise ValueError(f"Corpus '{name}' already exists")

        self._corpora[name] = text
        self._weights[name] = weight

    def remove_corpus(self, name: str) -> None:
        """Remove a corpus

        Args:
            name: Corpus identifier

        Raises:
            KeyError: If corpus doesn't exist
        """
        if name not in self._corpora:
            raise KeyError(f"Corpus '{name}' not found")

        del self._corpora[name]
        del self._weights[name]

    def build_model(self, n: int = 2, per_line: bool = True) -> Dict[str, Dict[str, float]]:
        """Build one n-gram model from all corpora, weighted by share

        Each corpus is modelled on its own, then its counts are scaled so
        that it makes up its weight's share of the merged model: weights
        0.5/0.3/0.2 mean half, 30% and 20% of all transitions, whatever the
        corpora's sizes. Exact for any weights, and no text is copied.

        Args:
            n: N-gram size (2-5)
            per_line: Treat each line as one entry (NGramBuilder.build_lines);
                False reads each corpus as one stream (NGramBuilder.build)

        Returns:
            Merged n-gram model (counts are floats)

        Raises:
            ValueError: If no corpora have been added
        """
        from markov_passgen.core.ngram_builder import NGramBuilder

        if not self._corpora:
            raise ValueError("No corpora have been added")

        builder = NGramBuilder()
        models = {
            name: (builder.build_lines(text, n) if per_line else builder.build(text, n))
            for name, text in self._corpora.items()
        }
        totals = {name: sum(sum(f.values()) for f in model.values()) for name, model in models.items()}
        total_weight = sum(self._weights.values())
        # Keep magnitudes count-like: the merged model has as many transitions in total as its parts
        scale_base = sum(totals.values())

        merged: Dict[str, Dict[str, float]] = {}
        for name, model in models.items():
            factor = (self._weights[name] / total_weight) * scale_base / totals[name]
            for prefix, followers in model.items():
                target = merged.setdefault(prefix, {})
                for char, count in followers.items():
                    target[char] = target.get(char, 0.0) + count * factor
        return merged

    def get_merged_corpus(self) -> str:
        """Get merged corpus with weights applied

        Kept for compatibility; build_model weights exactly and is what the
        CLI uses. Here weights are approximated by repeating each corpus
        max(1, int(share * 10)) times.

        Returns:
            Merged corpus text with weights applied by repetition

        Raises:
            ValueError: If no corpora have been added
        """
        if not self._corpora:
            raise ValueError("No corpora have been added")

        # Normalize weights
        total_weight = sum(self._weights.values())
        normalized_weights = {
            name: weight / total_weight
            for name, weight in self._weights.items()
        }

        # Build merged corpus by repeating each corpus proportionally
        merged_parts = []
        for name, text in self._corpora.items():
            # Calculate repetitions based on normalized weight
            # Use at least 1 repetition, scale up proportionally
            repetitions = max(1, int(normalized_weights[name] * 10))
            merged_parts.append(text * repetitions)

        return " ".join(merged_parts)

    def get_corpus_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for each corpus

        Returns:
            Dictionary mapping corpus names to their stats
        """
        stats = {}
        for name, text in self._corpora.items():
            words = text.split()
            stats[name] = {
                "char_count": len(text),
                "word_count": len(words),
                "unique_chars": len(set(text)),
                "weight": self._weights[name]
            }
        return stats

    def list_corpora(self) -> List[str]:
        """Get list of corpus names

        Returns:
            List of corpus identifiers
        """
        return list(self._corpora.keys())

    def get_weight(self, name: str) -> float:
        """Get weight for a corpus

        Args:
            name: Corpus identifier

        Returns:
            Corpus weight

        Raises:
            KeyError: If corpus doesn't exist
        """
        if name not in self._weights:
            raise KeyError(f"Corpus '{name}' not found")
        return self._weights[name]

    def set_weight(self, name: str, weight: float) -> None:
        """Update weight for a corpus

        Args:
            name: Corpus identifier
            weight: New weight value

        Raises:
            ValueError: If weight is not positive
            KeyError: If corpus doesn't exist
        """
        if weight <= 0:
            raise ValueError("Weight must be positive")

        if name not in self._weights:
            raise KeyError(f"Corpus '{name}' not found")

        self._weights[name] = weight

    def clear(self) -> None:
        """Remove all corpora"""
        self._corpora.clear()
        self._weights.clear()

    def count(self) -> int:
        """Get number of corpora

        Returns:
            Number of loaded corpora
        """
        return len(self._corpora)

    @staticmethod
    def from_files(filepaths: List[str], weights: Optional[List[float]] = None,
                   cleaner=None) -> 'MultiCorpusManager':
        """Create manager from list of files

        Args:
            filepaths: List of corpus file paths
            weights: Optional list of weights (default: all 1.0)
            cleaner: Optional text cleaner to apply to all

        Returns:
            Configured MultiCorpusManager

        Raises:
            ValueError: If weights length doesn't match filepaths
        """
        manager = MultiCorpusManager()

        if weights is None:
            weights = [1.0] * len(filepaths)

        if len(weights) != len(filepaths):
            raise ValueError("Number of weights must match number of files")

        for i, (filepath, weight) in enumerate(zip(filepaths, weights)):
            name = f"corpus_{i}"
            manager.add_corpus(name, filepath, weight, cleaner)

        return manager
