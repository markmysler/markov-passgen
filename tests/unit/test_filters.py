"""Unit tests for filter classes"""

import pytest
from markov_passgen.filters.length_filter import LengthFilter
from markov_passgen.filters.character_filter import CharacterFilter
from markov_passgen.filters.filter_chain import FilterChain


class TestLengthFilter:
    """Test cases for LengthFilter"""
    
    def test_filter_by_min_length(self):
        """Test filtering by minimum length"""
        filter_obj = LengthFilter(min_length=8)
        passwords = ["short", "longenough", "verylongpassword"]
        result = filter_obj.filter(passwords)
        assert len(result) == 2
        assert "short" not in result
    
    def test_filter_by_max_length(self):
        """Test filtering by maximum length"""
        filter_obj = LengthFilter(max_length=10)
        passwords = ["short", "longenough", "verylongpassword"]
        result = filter_obj.filter(passwords)
        assert len(result) == 2
        assert "verylongpassword" not in result
    
    def test_filter_by_range(self):
        """Test filtering by length range"""
        filter_obj = LengthFilter(min_length=5, max_length=12)
        passwords = ["abc", "hello", "longenough", "verylongpassword"]
        result = filter_obj.filter(passwords)
        assert len(result) == 2
        assert set(result) == {"hello", "longenough"}
    
    def test_filter_negative_min_length(self):
        """Test negative min_length raises error"""
        with pytest.raises(ValueError, match="negative"):
            LengthFilter(min_length=-1)
    
    def test_filter_negative_max_length(self):
        """Test negative max_length raises error"""
        with pytest.raises(ValueError, match="negative"):
            LengthFilter(max_length=-1)
    
    def test_filter_min_greater_than_max(self):
        """Test min > max raises error"""
        with pytest.raises(ValueError, match="greater than"):
            LengthFilter(min_length=10, max_length=5)


class TestCharacterFilter:
    """Test cases for CharacterFilter"""
    
    def test_require_digits(self):
        """Test filtering for passwords with digits"""
        filter_obj = CharacterFilter(require_digits=True)
        passwords = ["nodigits", "has123digits", "also456"]
        result = filter_obj.filter(passwords)
        assert len(result) == 2
        assert "nodigits" not in result
    
    def test_require_uppercase(self):
        """Test filtering for passwords with uppercase"""
        filter_obj = CharacterFilter(require_uppercase=True)
        passwords = ["lowercase", "HasUpper", "ALLCAPS"]
        result = filter_obj.filter(passwords)
        assert len(result) == 2
        assert "lowercase" not in result
    
    def test_require_lowercase(self):
        """Test filtering for passwords with lowercase"""
        filter_obj = CharacterFilter(require_lowercase=True)
        passwords = ["ALLCAPS", "HasLower", "alllower"]
        result = filter_obj.filter(passwords)
        assert len(result) == 2
        assert "ALLCAPS" not in result
    
    def test_require_special(self):
        """Test filtering for passwords with special characters"""
        filter_obj = CharacterFilter(require_special=True)
        passwords = ["nospecial", "has!special", "also@#$"]
        result = filter_obj.filter(passwords)
        assert len(result) == 2
        assert "nospecial" not in result
    
    def test_multiple_requirements(self):
        """Test multiple character requirements"""
        filter_obj = CharacterFilter(
            require_digits=True,
            require_uppercase=True
        )
        passwords = ["nodigits", "NoDigits", "Has123Digits", "has123noupper"]
        result = filter_obj.filter(passwords)
        assert len(result) == 1
        assert result[0] == "Has123Digits"
    
    def test_must_include(self):
        """Test must_include characters"""
        filter_obj = CharacterFilter(must_include="@#")
        passwords = ["no special", "has@char", "has@#both"]
        result = filter_obj.filter(passwords)
        assert len(result) == 1
        assert result[0] == "has@#both"
    
    def test_must_not_include(self):
        """Test must_not_include characters"""
        filter_obj = CharacterFilter(must_not_include="0O")
        passwords = ["good", "has0zero", "hasOchar", "alsobad0O"]
        result = filter_obj.filter(passwords)
        assert len(result) == 1
        assert result[0] == "good"
    
    def test_require_digits_filter_method(self):
        """Test require_digits_filter method"""
        filter_obj = CharacterFilter()
        passwords = ["nodigits", "has123"]
        result = filter_obj.require_digits_filter(passwords)
        assert len(result) == 1
        assert result[0] == "has123"
    
    def test_require_uppercase_filter_method(self):
        """Test require_uppercase_filter method"""
        filter_obj = CharacterFilter()
        passwords = ["lowercase", "HasUpper"]
        result = filter_obj.require_uppercase_filter(passwords)
        assert len(result) == 1
        assert result[0] == "HasUpper"
    
    def test_require_special_filter_method(self):
        """Test require_special_filter method"""
        filter_obj = CharacterFilter()
        passwords = ["nospecial", "has!special"]
        result = filter_obj.require_special_filter(passwords)
        assert len(result) == 1
        assert result[0] == "has!special"


class TestFilterChain:
    """Test cases for FilterChain"""
    
    def test_add_filter(self):
        """Test adding filters to chain"""
        chain = FilterChain()
        chain.add_filter(LengthFilter(min_length=5))
        assert len(chain) == 1
    
    def test_apply_single_filter(self):
        """Test applying single filter"""
        chain = FilterChain()
        chain.add_filter(LengthFilter(min_length=8))
        
        passwords = ["short", "longenough"]
        result = chain.apply(passwords)
        assert len(result) == 1
        assert result[0] == "longenough"
    
    def test_apply_multiple_filters(self):
        """Test applying multiple filters in sequence"""
        chain = FilterChain()
        chain.add_filter(LengthFilter(min_length=8))
        chain.add_filter(CharacterFilter(require_digits=True))
        
        passwords = ["short", "nodigits", "hasnumber8", "long1234"]
        result = chain.apply(passwords)
        assert len(result) == 2
        assert "hasnumber8" in result
        assert "long1234" in result
    
    def test_filter_chain_ordering(self):
        """Test that filter order matters"""
        passwords = ["abc", "abcd1234", "xyz"]
        
        # Chain 1: length then digits
        chain1 = FilterChain()
        chain1.add_filter(LengthFilter(min_length=5))
        chain1.add_filter(CharacterFilter(require_digits=True))
        result1 = chain1.apply(passwords)
        
        # Chain 2: digits then length
        chain2 = FilterChain()
        chain2.add_filter(CharacterFilter(require_digits=True))
        chain2.add_filter(LengthFilter(min_length=5))
        result2 = chain2.apply(passwords)
        
        # Both should give same result
        assert result1 == result2
    
    def test_empty_chain(self):
        """Test applying empty filter chain"""
        chain = FilterChain()
        passwords = ["test1", "test2"]
        result = chain.apply(passwords)
        assert result == passwords
    
    def test_clear_filters(self):
        """Test clearing filter chain"""
        chain = FilterChain()
        chain.add_filter(LengthFilter(min_length=5))
        chain.add_filter(CharacterFilter(require_digits=True))
        assert len(chain) == 2
        
        chain.clear()
        assert len(chain) == 0
    
    def test_method_chaining(self):
        """Test that add_filter returns self for chaining"""
        chain = FilterChain()
        result = chain.add_filter(LengthFilter(min_length=5))
        assert result is chain
    
    def test_filter_eliminates_all(self):
        """Test when filters eliminate all passwords"""
        chain = FilterChain()
        chain.add_filter(LengthFilter(min_length=100))
        
        passwords = ["short", "medium", "longenough"]
        result = chain.apply(passwords)
        assert len(result) == 0
