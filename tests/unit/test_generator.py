"""Unit tests for PasswordGenerator"""

import pytest
from markov_passgen.core.ngram_builder import NGramBuilder
from markov_passgen.core.generator import PasswordGenerator


class TestPasswordGenerator:
    """Test cases for PasswordGenerator class"""
    
    def test_generate_n_passwords(self):
        """Test generating N passwords"""
        # Build simple model
        builder = NGramBuilder()
        text = "hello world test password generation"
        model = builder.build(text, n=2)
        
        generator = PasswordGenerator(model)
        passwords = generator.generate(count=10, length=8)
        
        assert len(passwords) == 10
        for pwd in passwords:
            assert isinstance(pwd, str)
    
    def test_generate_with_length(self):
        """Test all passwords have correct length"""
        builder = NGramBuilder()
        text = "abcdefghijklmnopqrstuvwxyz" * 5
        model = builder.build(text, n=2)
        
        generator = PasswordGenerator(model)
        passwords = generator.generate(count=5, length=12)
        
        for pwd in passwords:
            assert len(pwd) == 12
    
    def test_generate_zero_count(self):
        """Test generating 0 passwords returns empty list"""
        builder = NGramBuilder()
        model = builder.build("hello world", n=2)
        generator = PasswordGenerator(model)
        
        passwords = generator.generate(count=0, length=10)
        assert passwords == []
    
    def test_generate_negative_count(self):
        """Test negative count raises ValueError"""
        builder = NGramBuilder()
        model = builder.build("hello world", n=2)
        generator = PasswordGenerator(model)
        
        with pytest.raises(ValueError, match="count must be >= 0"):
            generator.generate(count=-1, length=10)
    
    def test_generate_invalid_length(self):
        """Test length < 1 raises ValueError"""
        builder = NGramBuilder()
        model = builder.build("hello world", n=2)
        generator = PasswordGenerator(model)
        
        with pytest.raises(ValueError, match="length must be >= 1"):
            generator.generate(count=10, length=0)
    
    def test_generate_with_empty_model(self):
        """Test generating from empty model raises error"""
        generator = PasswordGenerator({})
        
        with pytest.raises(ValueError, match="empty"):
            generator.generate(count=10, length=8)
    
    def test_generate_with_seed_word(self):
        """Test generation with seed word"""
        builder = NGramBuilder()
        text = "hello world testing passwords"
        model = builder.build(text, n=2)
        
        generator = PasswordGenerator(model)
        passwords = generator.generate(count=5, length=10, seed="he")
        
        assert len(passwords) == 5
        # Passwords should be valid
        for pwd in passwords:
            assert len(pwd) == 10
    
    def test_set_random_seed(self):
        """Test deterministic generation with random seed"""
        builder = NGramBuilder()
        text = "abcdefghijklmnopqrstuvwxyz" * 10
        model = builder.build(text, n=2)
        
        # Generate with seed
        generator1 = PasswordGenerator(model)
        generator1.set_random_seed(42)
        passwords1 = generator1.generate(count=5, length=10)
        
        # Generate again with same seed
        generator2 = PasswordGenerator(model)
        generator2.set_random_seed(42)
        passwords2 = generator2.generate(count=5, length=10)
        
        # Should be identical
        assert passwords1 == passwords2
    
    def test_get_generation_stats(self):
        """Test getting generation statistics"""
        builder = NGramBuilder()
        model = builder.build("hello world testing", n=2)
        
        generator = PasswordGenerator(model)
        generator.generate(count=10, length=8)
        
        stats = generator.get_generation_stats()
        assert stats["total_generated"] == 10
        assert stats["model_size"] > 0
        assert stats["ngram_size"] == 2
    
    def test_generate_various_lengths(self):
        """Test generating passwords of various lengths"""
        builder = NGramBuilder()
        text = "the quick brown fox jumps over the lazy dog" * 5
        model = builder.build(text, n=3)
        
        generator = PasswordGenerator(model)
        
        for length in [5, 10, 15, 20]:
            passwords = generator.generate(count=3, length=length)
            for pwd in passwords:
                assert len(pwd) == length
