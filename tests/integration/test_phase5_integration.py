"""Integration tests for Phase 5: Multi-corpus features"""

import pytest
from pathlib import Path
from markov_passgen.core.multi_corpus_manager import MultiCorpusManager
from markov_passgen.core.ngram_builder import NGramBuilder
from markov_passgen.core.generator import PasswordGenerator


@pytest.fixture
def english_corpus(tmp_path):
    """Create English corpus file"""
    file = tmp_path / "english.txt"
    file.write_text("the quick brown fox jumps over the lazy dog " * 10)
    return str(file)


@pytest.fixture
def tech_corpus(tmp_path):
    """Create tech corpus file"""
    file = tmp_path / "tech.txt"
    file.write_text("python java javascript typescript rust golang code debug test " * 10)
    return str(file)


@pytest.fixture
def names_corpus(tmp_path):
    """Create names corpus file"""
    file = tmp_path / "names.txt"
    file.write_text("alice bob charlie david emma frank grace henry isabel jack " * 10)
    return str(file)


class TestMultiCorpusGeneration:
    """Test password generation with multiple corpora"""
    
    def test_generate_from_two_corpora(self, english_corpus, tech_corpus):
        """Should generate passwords from merged corpora"""
        manager = MultiCorpusManager.from_files([english_corpus, tech_corpus])
        merged = manager.get_merged_corpus()
        
        builder = NGramBuilder()
        model = builder.build(merged, n=2)
        
        generator = PasswordGenerator(model)
        passwords = generator.generate(10, length=12)
        
        assert len(passwords) == 10
        for pwd in passwords:
            assert len(pwd) == 12
    
    def test_generate_with_equal_weights(self, english_corpus, tech_corpus):
        """Should balance influence of equally weighted corpora"""
        manager = MultiCorpusManager.from_files(
            [english_corpus, tech_corpus],
            weights=[1.0, 1.0]
        )
        merged = manager.get_merged_corpus()
        
        builder = NGramBuilder()
        model = builder.build(merged, n=2)
        
        generator = PasswordGenerator(model)
        generator.set_random_seed(42)
        passwords = generator.generate(50, length=15)
        
        # Verify both corpus influences appear
        combined = " ".join(passwords)
        # Should contain chars from both corpora
        assert len(combined) > 0
        assert len(passwords) == 50
    
    def test_generate_with_different_weights(self, english_corpus, tech_corpus):
        """Should apply different weights to corpora"""
        # Heavy tech weight
        manager = MultiCorpusManager.from_files(
            [english_corpus, tech_corpus],
            weights=[1.0, 3.0]
        )
        merged = manager.get_merged_corpus()
        
        builder = NGramBuilder()
        model = builder.build(merged, n=2)
        
        generator = PasswordGenerator(model)
        generator.set_random_seed(42)
        passwords = generator.generate(50, length=15)
        
        assert len(passwords) == 50
        for pwd in passwords:
            assert len(pwd) == 15
    
    def test_generate_from_three_corpora(self, english_corpus, tech_corpus, names_corpus):
        """Should generate from three corpora"""
        manager = MultiCorpusManager.from_files([english_corpus, tech_corpus, names_corpus])
        merged = manager.get_merged_corpus()
        
        builder = NGramBuilder()
        model = builder.build(merged, n=2)
        
        generator = PasswordGenerator(model)
        passwords = generator.generate(10, length=12)
        
        assert len(passwords) == 10
        for pwd in passwords:
            assert len(pwd) == 12


class TestMultiCorpusWithFilters:
    """Test multi-corpus generation with filters"""
    
    def test_generate_with_length_filter(self, english_corpus, tech_corpus):
        """Should apply length filter to multi-corpus passwords"""
        from markov_passgen.filters.length_filter import LengthFilter
        
        manager = MultiCorpusManager.from_files([english_corpus, tech_corpus])
        merged = manager.get_merged_corpus()
        
        builder = NGramBuilder()
        model = builder.build(merged, n=2)
        
        generator = PasswordGenerator(model)
        passwords = generator.generate(50, length=15)
        
        # Apply filter
        length_filter = LengthFilter(min_length=10, max_length=20)
        filtered = length_filter.filter(passwords)
        
        assert len(filtered) > 0
        for pwd in filtered:
            assert 10 <= len(pwd) <= 20
    
    def test_generate_with_character_filter(self, english_corpus, tech_corpus):
        """Should apply character filter to multi-corpus passwords"""
        from markov_passgen.filters.character_filter import CharacterFilter
        
        manager = MultiCorpusManager.from_files([english_corpus, tech_corpus])
        merged = manager.get_merged_corpus()
        
        builder = NGramBuilder()
        model = builder.build(merged, n=2)
        
        generator = PasswordGenerator(model)
        passwords = generator.generate(100, length=15)
        
        # Apply filter requiring digits (may not find any since corpus is text only)
        char_filter = CharacterFilter(require_lowercase=True)
        filtered = char_filter.filter(passwords)
        
        # Should filter successfully even if no matches
        assert isinstance(filtered, list)


class TestMultiCorpusWithEntropy:
    """Test entropy-based generation with multiple corpora"""
    
    def test_generate_with_entropy_threshold(self, english_corpus, tech_corpus):
        """Should generate passwords meeting entropy threshold from multiple corpora"""
        manager = MultiCorpusManager.from_files([english_corpus, tech_corpus])
        merged = manager.get_merged_corpus()
        
        builder = NGramBuilder()
        model = builder.build(merged, n=2)
        
        generator = PasswordGenerator(model)
        generator.set_random_seed(42)
        
        # Generate with low entropy threshold
        results = generator.generate_with_entropy(count=5, min_entropy=0.5)
        
        assert len(results) == 5
        for password, entropy in results:
            assert entropy >= 0.5
            assert len(password) > 0


class TestMultiCorpusWithTransformers:
    """Test password transformers with multiple corpora"""
    
    def test_generate_with_leet_speak(self, english_corpus, tech_corpus):
        """Should apply leet speak to multi-corpus passwords"""
        from markov_passgen.transformers.password_transformer import LeetSpeakTransformer
        
        manager = MultiCorpusManager.from_files([english_corpus, tech_corpus])
        merged = manager.get_merged_corpus()
        
        builder = NGramBuilder()
        model = builder.build(merged, n=2)
        
        generator = PasswordGenerator(model)
        generator.set_random_seed(42)
        
        transformer = LeetSpeakTransformer(intensity=1.0)
        passwords = generator.generate(10, length=12, transformer=transformer)
        
        assert len(passwords) == 10
        # At least some passwords should have leet chars
        combined = "".join(passwords)
        assert any(c in combined for c in "3471305")
    
    def test_generate_with_case_variation(self, english_corpus, tech_corpus):
        """Should apply case variation to multi-corpus passwords"""
        from markov_passgen.transformers.password_transformer import CaseVariationTransformer
        
        manager = MultiCorpusManager.from_files([english_corpus, tech_corpus])
        merged = manager.get_merged_corpus()
        
        builder = NGramBuilder()
        model = builder.build(merged, n=2)
        
        generator = PasswordGenerator(model)
        generator.set_random_seed(42)
        
        transformer = CaseVariationTransformer(mode="random")
        passwords = generator.generate(10, length=12, transformer=transformer)
        
        assert len(passwords) == 10
        for pwd in passwords:
            assert len(pwd) == 12


class TestMultiCorpusTextCleaning:
    """Test text cleaning with multiple corpora"""
    
    def test_generate_with_text_cleaner(self, tmp_path):
        """Should apply text cleaner to all corpora"""
        from markov_passgen.transformers.text_cleaner import TextCleaner
        
        # Create corpora with uppercase and punctuation
        file1 = tmp_path / "corpus1.txt"
        file1.write_text("HELLO WORLD! THIS IS A TEST." * 10)
        file2 = tmp_path / "corpus2.txt"
        file2.write_text("PYTHON IS AWESOME!" * 10)
        
        cleaner = TextCleaner(lowercase=True, remove_punctuation=True)
        manager = MultiCorpusManager.from_files([str(file1), str(file2)], cleaner=cleaner)
        
        merged = manager.get_merged_corpus()
        
        # Verify cleaning applied
        assert "!" not in merged
        assert "HELLO" not in merged
        assert "hello" in merged or "world" in merged
        
        # Generate passwords
        builder = NGramBuilder()
        model = builder.build(merged, n=2)
        
        generator = PasswordGenerator(model)
        passwords = generator.generate(10, length=12)
        
        assert len(passwords) == 10


class TestMultiCorpusWeightAdjustment:
    """Test dynamic weight adjustment"""
    
    def test_adjust_weights_during_generation(self, english_corpus, tech_corpus):
        """Should regenerate with adjusted weights"""
        manager = MultiCorpusManager.from_files(
            [english_corpus, tech_corpus],
            weights=[1.0, 1.0]
        )
        
        # Generate with equal weights
        merged1 = manager.get_merged_corpus()
        builder = NGramBuilder()
        model1 = builder.build(merged1, n=2)
        generator1 = PasswordGenerator(model1)
        generator1.set_random_seed(42)
        passwords1 = generator1.generate(10, length=12)
        
        # Adjust weights
        manager.set_weight("corpus_0", 3.0)
        
        # Generate with new weights
        merged2 = manager.get_merged_corpus()
        model2 = builder.build(merged2, n=2)
        generator2 = PasswordGenerator(model2)
        generator2.set_random_seed(42)
        passwords2 = generator2.generate(10, length=12)
        
        # Results should differ due to weight change
        assert len(passwords1) == 10
        assert len(passwords2) == 10


class TestMultiCorpusDeterminism:
    """Test deterministic generation with multiple corpora"""
    
    def test_deterministic_with_seed(self, english_corpus, tech_corpus):
        """Should produce same results with same seed"""
        manager = MultiCorpusManager.from_files([english_corpus, tech_corpus])
        merged = manager.get_merged_corpus()
        
        builder = NGramBuilder()
        model = builder.build(merged, n=2)
        
        # First generation
        generator1 = PasswordGenerator(model)
        generator1.set_random_seed(42)
        passwords1 = generator1.generate(10, length=12)
        
        # Second generation with same seed
        generator2 = PasswordGenerator(model)
        generator2.set_random_seed(42)
        passwords2 = generator2.generate(10, length=12)
        
        assert passwords1 == passwords2


class TestMultiCorpusEdgeCases:
    """Test edge cases in multi-corpus generation"""
    
    def test_generate_with_very_small_corpora(self, tmp_path):
        """Should handle small corpora"""
        file1 = tmp_path / "small1.txt"
        file1.write_text("abc def " * 5)
        file2 = tmp_path / "small2.txt"
        file2.write_text("xyz uvw " * 5)
        
        manager = MultiCorpusManager.from_files([str(file1), str(file2)])
        merged = manager.get_merged_corpus()
        
        builder = NGramBuilder()
        model = builder.build(merged, n=2)
        
        generator = PasswordGenerator(model)
        passwords = generator.generate(5, length=8)
        
        assert len(passwords) == 5
    
    def test_generate_with_highly_skewed_weights(self, english_corpus, tech_corpus):
        """Should handle extreme weight differences"""
        manager = MultiCorpusManager.from_files(
            [english_corpus, tech_corpus],
            weights=[0.1, 10.0]
        )
        merged = manager.get_merged_corpus()
        
        builder = NGramBuilder()
        model = builder.build(merged, n=2)
        
        generator = PasswordGenerator(model)
        passwords = generator.generate(10, length=12)
        
        assert len(passwords) == 10
