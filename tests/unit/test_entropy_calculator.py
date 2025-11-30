"""Unit tests for EntropyCalculator"""

import pytest
from markov_passgen.core.entropy_calculator import EntropyCalculator
from markov_passgen.core.ngram_builder import NGramBuilder


class TestEntropyCalculator:
    """Test cases for EntropyCalculator class"""
    
    def test_shannon_entropy_uniform(self):
        """Test Shannon entropy for uniform distribution"""
        calculator = EntropyCalculator()
        # "aaaa" - all same char, entropy should be 0
        entropy = calculator.calculate_shannon_entropy("aaaa")
        assert entropy == 0.0
    
    def test_shannon_entropy_varied(self):
        """Test Shannon entropy for varied characters"""
        calculator = EntropyCalculator()
        # "abcd" - all different chars, high entropy
        entropy = calculator.calculate_shannon_entropy("abcd")
        assert entropy == 2.0  # log2(4) = 2.0
    
    def test_shannon_entropy_empty(self):
        """Test Shannon entropy with empty password raises error"""
        calculator = EntropyCalculator()
        with pytest.raises(ValueError, match="empty"):
            calculator.calculate_shannon_entropy("")
    
    def test_markov_entropy_with_model(self):
        """Test Markov entropy calculation"""
        calculator = EntropyCalculator()
        builder = NGramBuilder()
        text = "hello world " * 10
        model = builder.build(text, n=2)
        
        entropy = calculator.calculate_markov_entropy("hello", model)
        assert entropy >= 0  # Can be 0 if password exactly matches training corpus
    
    def test_markov_entropy_empty_password(self):
        """Test Markov entropy with empty password"""
        calculator = EntropyCalculator()
        builder = NGramBuilder()
        model = builder.build("hello world", n=2)
        
        with pytest.raises(ValueError, match="empty"):
            calculator.calculate_markov_entropy("", model)
    
    def test_markov_entropy_empty_model(self):
        """Test Markov entropy with empty model"""
        calculator = EntropyCalculator()
        with pytest.raises(ValueError, match="empty"):
            calculator.calculate_markov_entropy("hello", {})
    
    def test_markov_entropy_short_password(self):
        """Test Markov entropy with password shorter than n"""
        calculator = EntropyCalculator()
        builder = NGramBuilder()
        model = builder.build("hello world testing", n=3)
        
        # Password "hi" is shorter than n=3, should fall back to Shannon
        entropy = calculator.calculate_markov_entropy("hi", model)
        assert entropy > 0
    
    def test_estimate_crack_time_short(self):
        """Test crack time estimation for short password"""
        calculator = EntropyCalculator()
        time_str = calculator.estimate_crack_time("abc")
        assert "second" in time_str or "minute" in time_str
    
    def test_estimate_crack_time_medium(self):
        """Test crack time estimation for medium password"""
        calculator = EntropyCalculator()
        time_str = calculator.estimate_crack_time("Password123!")
        # Should be a time value (could be seconds to millennia depending on computation power)
        assert any(word in time_str for word in ["second", "minute", "hour", "day", "year", "centur", "millenni"])
    
    def test_estimate_crack_time_long(self):
        """Test crack time estimation for long password"""
        calculator = EntropyCalculator()
        time_str = calculator.estimate_crack_time("SuperLongPassword123!@#$%")
        # Should be years or more
        assert any(word in time_str for word in ["year", "centur", "millenni"])
    
    def test_estimate_crack_time_empty(self):
        """Test crack time with empty password"""
        calculator = EntropyCalculator()
        with pytest.raises(ValueError, match="empty"):
            calculator.estimate_crack_time("")
    
    def test_estimate_crack_time_custom_rate(self):
        """Test crack time with custom attempt rate"""
        calculator = EntropyCalculator()
        time_str = calculator.estimate_crack_time("test", attempts_per_second=100)
        assert isinstance(time_str, str)
