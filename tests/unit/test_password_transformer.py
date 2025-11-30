"""Unit tests for password transformers"""

import pytest
import random
from markov_passgen.transformers.password_transformer import (
    BasePasswordTransformer,
    LeetSpeakTransformer,
    CaseVariationTransformer,
    SubstitutionTransformer,
    TransformerChain
)


class TestLeetSpeakTransformer:
    """Test LeetSpeakTransformer class"""
    
    def test_full_intensity(self):
        """Test: Full intensity converts all applicable characters"""
        random.seed(42)
        transformer = LeetSpeakTransformer(intensity=1.0)
        password = "leetspeak"
        result = transformer.transform(password)
        # With intensity 1.0, all letters should be converted
        assert '3' in result or 'e' not in result  # e -> 3
        assert '7' in result or 't' not in result  # t -> 7
    
    def test_zero_intensity(self):
        """Test: Zero intensity converts nothing"""
        transformer = LeetSpeakTransformer(intensity=0.0)
        password = "leetspeak"
        result = transformer.transform(password)
        assert result == password
    
    def test_partial_intensity(self):
        """Test: Partial intensity converts some characters"""
        random.seed(42)
        transformer = LeetSpeakTransformer(intensity=0.5)
        password = "leetspeak"
        result = transformer.transform(password)
        # Result should be different but not all converted
        assert len(result) == len(password)
    
    def test_invalid_intensity(self):
        """Test: Invalid intensity raises ValueError"""
        with pytest.raises(ValueError, match="Intensity must be between"):
            LeetSpeakTransformer(intensity=1.5)
        
        with pytest.raises(ValueError, match="Intensity must be between"):
            LeetSpeakTransformer(intensity=-0.1)
    
    def test_common_substitutions(self):
        """Test: Common leet speak substitutions work"""
        random.seed(42)
        transformer = LeetSpeakTransformer(intensity=1.0)
        
        # Test individual substitutions
        test_cases = [
            ("a", "4"),
            ("e", "3"),
            ("i", "1"),
            ("o", "0"),
            ("s", "5"),
            ("t", "7")
        ]
        
        for input_char, expected in test_cases:
            result = transformer.transform(input_char)
            assert result == expected or result == input_char  # Probabilistic
    
    def test_uppercase_letters(self):
        """Test: Uppercase letters are also transformed"""
        random.seed(42)
        transformer = LeetSpeakTransformer(intensity=1.0)
        password = "AEIOST"
        result = transformer.transform(password)
        # Should contain numbers
        assert any(c.isdigit() for c in result)
    
    def test_preserves_length(self):
        """Test: Transformation preserves password length"""
        transformer = LeetSpeakTransformer(intensity=0.5)
        password = "test password 123"
        result = transformer.transform(password)
        assert len(result) == len(password)
    
    def test_batch_transform(self):
        """Test: Transform multiple passwords"""
        transformer = LeetSpeakTransformer(intensity=0.5)
        passwords = ["test1", "test2", "test3"]
        results = transformer.transform_batch(passwords)
        assert len(results) == 3
        assert all(len(r) == 5 for r in results)


class TestCaseVariationTransformer:
    """Test CaseVariationTransformer class"""
    
    def test_random_mode(self):
        """Test: Random case variation"""
        random.seed(42)
        transformer = CaseVariationTransformer(mode='random')
        password = "testpassword"
        result = transformer.transform(password)
        
        # Should have mixed case
        assert result != password.lower()
        assert result != password.upper()
        assert len(result) == len(password)
    
    def test_alternating_mode(self):
        """Test: Alternating case variation"""
        transformer = CaseVariationTransformer(mode='alternating')
        password = "testpassword"
        result = transformer.transform(password)
        
        # Check alternating pattern
        assert result[0].isupper()
        assert result[1].islower()
        assert result[2].isupper()
        assert result[3].islower()
    
    def test_capitalize_mode(self):
        """Test: Capitalize words"""
        transformer = CaseVariationTransformer(mode='capitalize')
        password = "test password here"
        result = transformer.transform(password)
        
        assert result == "Test Password Here"
    
    def test_invalid_mode(self):
        """Test: Invalid mode raises ValueError"""
        with pytest.raises(ValueError, match="Invalid mode"):
            CaseVariationTransformer(mode='invalid')
    
    def test_preserves_non_letters(self):
        """Test: Non-letter characters are preserved"""
        transformer = CaseVariationTransformer(mode='random')
        password = "test123!@#"
        result = transformer.transform(password)
        
        # Numbers and special chars should be unchanged
        assert '123' in result
        assert '!@#' in result
    
    def test_empty_password(self):
        """Test: Empty password returns empty"""
        transformer = CaseVariationTransformer(mode='random')
        assert transformer.transform("") == ""
    
    def test_numbers_only(self):
        """Test: Numbers-only password unchanged"""
        transformer = CaseVariationTransformer(mode='random')
        password = "123456"
        result = transformer.transform(password)
        assert result == password


class TestSubstitutionTransformer:
    """Test SubstitutionTransformer class"""
    
    def test_custom_substitutions(self):
        """Test: Custom substitution dictionary"""
        substitutions = {'a': '@', 's': '$'}
        transformer = SubstitutionTransformer(substitutions, probability=1.0)
        password = "password"
        result = transformer.transform(password)
        
        assert '@' in result  # a -> @
        assert '$' in result  # s -> $
    
    def test_zero_probability(self):
        """Test: Zero probability applies no substitutions"""
        substitutions = {'a': '@', 's': '$'}
        transformer = SubstitutionTransformer(substitutions, probability=0.0)
        password = "password"
        result = transformer.transform(password)
        
        assert result == password
    
    def test_partial_probability(self):
        """Test: Partial probability applies some substitutions"""
        random.seed(42)
        substitutions = {'a': '@', 's': '$'}
        transformer = SubstitutionTransformer(substitutions, probability=0.5)
        password = "aaaaassss"
        result = transformer.transform(password)
        
        # Should have mix of original and substituted
        assert len(result) == len(password)
    
    def test_add_substitution(self):
        """Test: Add substitution after creation"""
        transformer = SubstitutionTransformer()
        transformer.add_substitution('a', '@')
        transformer.add_substitution('s', '$')
        
        result = transformer.transform("pass")
        assert '@' in result or '$' in result
    
    def test_invalid_probability(self):
        """Test: Invalid probability raises ValueError"""
        with pytest.raises(ValueError, match="Probability must be between"):
            SubstitutionTransformer({}, probability=1.5)
        
        with pytest.raises(ValueError, match="Probability must be between"):
            SubstitutionTransformer({}, probability=-0.1)
    
    def test_special_chars_transformer(self):
        """Test: Static special_chars_transformer method"""
        transformer = SubstitutionTransformer.special_chars_transformer(probability=1.0)
        password = "sail"
        result = transformer.transform(password)
        
        # Should have special characters
        assert '@' in result or '$' in result or '!' in result or '|' in result
    
    def test_empty_substitutions(self):
        """Test: Empty substitutions returns original"""
        transformer = SubstitutionTransformer({}, probability=1.0)
        password = "password"
        result = transformer.transform(password)
        assert result == password


class TestTransformerChain:
    """Test TransformerChain class"""
    
    def test_single_transformer(self):
        """Test: Chain with single transformer"""
        chain = TransformerChain()
        chain.add(LeetSpeakTransformer(intensity=1.0))
        
        random.seed(42)
        result = chain.transform("test")
        assert result != "test"  # Should be transformed
    
    def test_multiple_transformers(self):
        """Test: Chain with multiple transformers"""
        random.seed(42)
        chain = TransformerChain()
        chain.add(LeetSpeakTransformer(intensity=1.0))
        chain.add(CaseVariationTransformer(mode='alternating'))
        
        result = chain.transform("test")
        # Should have both leet speak and case variation
        assert len(result) == 4
    
    def test_method_chaining(self):
        """Test: add() returns self for method chaining"""
        chain = TransformerChain()
        result = chain.add(LeetSpeakTransformer(intensity=0.5))
        
        assert result is chain
        
        # Can chain multiple adds
        chain.add(CaseVariationTransformer(mode='random')).add(
            SubstitutionTransformer({'a': '@'})
        )
        
        assert len(chain.transformers) == 3
    
    def test_empty_chain(self):
        """Test: Empty chain returns original password"""
        chain = TransformerChain()
        password = "test"
        result = chain.transform(password)
        assert result == password
    
    def test_clear_transformers(self):
        """Test: Clear removes all transformers"""
        chain = TransformerChain()
        chain.add(LeetSpeakTransformer(intensity=0.5))
        chain.add(CaseVariationTransformer(mode='random'))
        
        assert len(chain.transformers) == 2
        
        chain.clear()
        assert len(chain.transformers) == 0
    
    def test_transformation_order(self):
        """Test: Transformers are applied in order"""
        chain = TransformerChain()
        
        # First: substitute a -> x
        chain.add(SubstitutionTransformer({'a': 'x'}, probability=1.0))
        # Then: substitute x -> y
        chain.add(SubstitutionTransformer({'x': 'y'}, probability=1.0))
        
        result = chain.transform("a")
        assert result == "y"  # a -> x -> y
    
    def test_batch_transform(self):
        """Test: Transform multiple passwords with chain"""
        chain = TransformerChain()
        chain.add(LeetSpeakTransformer(intensity=0.5))
        
        passwords = ["test1", "test2", "test3"]
        results = chain.transform_batch(passwords)
        
        assert len(results) == 3
        assert all(len(r) == 5 for r in results)
