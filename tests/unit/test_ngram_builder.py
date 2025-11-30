"""Unit tests for NGramBuilder"""

import pytest
import tempfile
import os
import json
from markov_passgen.core.ngram_builder import NGramBuilder


class TestNGramBuilder:
    """Test cases for NGramBuilder class"""
    
    def test_build_with_valid_corpus(self):
        """Test building n-gram model with valid corpus"""
        builder = NGramBuilder()
        text = "hello world"
        model = builder.build(text, n=2)
        
        assert isinstance(model, dict)
        assert len(model) > 0
        # Check that some bigrams exist
        assert "he" in model
        assert "el" in model
    
    def test_build_with_empty_corpus(self):
        """Test building with empty corpus raises ValueError"""
        builder = NGramBuilder()
        with pytest.raises(ValueError, match="empty"):
            builder.build("", n=2)
    
    def test_build_with_invalid_n(self):
        """Test building with n < 2 or n > 5 raises ValueError"""
        builder = NGramBuilder()
        with pytest.raises(ValueError, match="n must be between 2 and 5"):
            builder.build("hello", n=0)
        
        with pytest.raises(ValueError, match="n must be between 2 and 5"):
            builder.build("hello", n=1)
        
        with pytest.raises(ValueError, match="n must be between 2 and 5"):
            builder.build("hello world", n=6)
    
    def test_build_corpus_shorter_than_n(self):
        """Test building when corpus length < n"""
        builder = NGramBuilder()
        with pytest.raises(ValueError, match="must be >= n"):
            builder.build("hi", n=5)
    
    def test_get_next_char_probabilities(self):
        """Test getting probabilities for a prefix"""
        builder = NGramBuilder()
        text = "aaab"  # "aa" -> "a" (count 1), "aa" -> "b" (count 1)
        builder.build(text, n=2)
        
        probs = builder.get_next_char_probabilities("aa")
        assert isinstance(probs, dict)
        assert len(probs) > 0
        # Should have probabilities that sum to ~1.0
        assert abs(sum(probs.values()) - 1.0) < 0.01
    
    def test_get_next_char_probabilities_invalid_prefix(self):
        """Test getting probabilities for non-existent prefix"""
        builder = NGramBuilder()
        builder.build("hello", n=2)
        
        probs = builder.get_next_char_probabilities("xyz")
        assert probs == {}
    
    def test_build_different_n_values(self):
        """Test building with different n-gram sizes"""
        builder = NGramBuilder()
        text = "hello world testing"
        
        # Test n=2 (bigrams)
        model2 = builder.build(text, n=2)
        assert len(list(model2.keys())[0]) == 2
        
        # Test n=3 (trigrams)
        model3 = builder.build(text, n=3)
        assert len(list(model3.keys())[0]) == 3
    
    def test_save_and_load_model(self):
        """Test saving and loading model to/from JSON"""
        builder = NGramBuilder()
        text = "hello world"
        original_model = builder.build(text, n=2)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            builder.save_model(temp_path)
            
            # Load in new builder
            builder2 = NGramBuilder()
            loaded_model = builder2.load_model(temp_path)
            
            assert loaded_model == original_model
        finally:
            os.unlink(temp_path)
    
    def test_add_to_model(self):
        """Test incrementally updating model"""
        builder = NGramBuilder()
        builder.build("hello", n=2)
        initial_size = len(builder._model)
        
        builder.add_to_model(" world")
        updated_size = len(builder._model)
        
        # Should have more n-grams after adding text
        assert updated_size >= initial_size
    
    def test_add_to_model_without_build(self):
        """Test add_to_model without building first raises error"""
        builder = NGramBuilder()
        with pytest.raises(ValueError, match="not initialized"):
            builder.add_to_model("text")
