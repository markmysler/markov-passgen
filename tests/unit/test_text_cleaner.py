"""Unit tests for text cleaning and transformation"""

import pytest
from markov_passgen.transformers.text_cleaner import TextCleaner, BaseTextCleaner
from markov_passgen.transformers.case_transformer import CaseTransformer
from markov_passgen.transformers.character_transformer import CharacterTransformer


class TestTextCleaner:
    """Test TextCleaner class"""
    
    def test_lowercase_conversion(self):
        """Test: Convert text to lowercase"""
        cleaner = TextCleaner(lowercase=True)
        text = "Hello WORLD Test"
        result = cleaner.clean(text)
        assert result == "hello world test"
    
    def test_remove_punctuation(self):
        """Test: Remove all punctuation"""
        cleaner = TextCleaner(remove_punctuation=True)
        text = "Hello, World! Test?"
        result = cleaner.clean(text)
        assert result == "Hello World Test"
    
    def test_remove_digits(self):
        """Test: Remove all digits"""
        cleaner = TextCleaner(remove_digits=True)
        text = "Test123 with456 numbers789"
        result = cleaner.clean(text)
        assert result == "Test with numbers"
    
    def test_normalize_whitespace(self):
        """Test: Normalize multiple spaces to single"""
        cleaner = TextCleaner(normalize_whitespace=True)
        text = "Hello    World   Test"
        result = cleaner.clean(text)
        assert result == "Hello World Test"
    
    def test_multiple_operations(self):
        """Test: Apply multiple cleaning operations"""
        cleaner = TextCleaner(
            lowercase=True,
            remove_punctuation=True,
            normalize_whitespace=True
        )
        text = "Hello,   WORLD!   Test?"
        result = cleaner.clean(text)
        assert result == "hello world test"
    
    def test_all_operations(self):
        """Test: Apply all cleaning operations"""
        cleaner = TextCleaner(
            lowercase=True,
            remove_punctuation=True,
            remove_digits=True,
            normalize_whitespace=True
        )
        text = "Hello123,   WORLD456!   Test789?"
        result = cleaner.clean(text)
        assert result == "hello world test"
    
    def test_empty_text(self):
        """Test: Empty text returns empty"""
        cleaner = TextCleaner(lowercase=True)
        assert cleaner.clean("") == ""
    
    def test_whitespace_trimming(self):
        """Test: Leading/trailing whitespace is trimmed"""
        cleaner = TextCleaner(lowercase=True)
        text = "  Hello World  "
        result = cleaner.clean(text)
        assert result == "hello world"
    
    def test_empty_after_cleaning(self):
        """Test: ValueError if text is empty after cleaning"""
        cleaner = TextCleaner(remove_punctuation=True, remove_digits=True)
        with pytest.raises(ValueError, match="Text is empty after cleaning"):
            cleaner.clean("123!@#")
    
    def test_lowercase_only_static(self):
        """Test: Static lowercase_only method"""
        result = TextCleaner.lowercase_only("Hello WORLD")
        assert result == "hello world"
    
    def test_remove_punctuation_only_static(self):
        """Test: Static remove_punctuation_only method"""
        result = TextCleaner.remove_punctuation_only("Hello, World!")
        assert result == "Hello World"
    
    def test_remove_digits_only_static(self):
        """Test: Static remove_digits_only method"""
        result = TextCleaner.remove_digits_only("Test123")
        assert result == "Test"
    
    def test_normalize_whitespace_only_static(self):
        """Test: Static normalize_whitespace_only method"""
        result = TextCleaner.normalize_whitespace_only("Hello    World")
        assert result == "Hello World"
    
    def test_no_operations(self):
        """Test: No operations returns trimmed text"""
        cleaner = TextCleaner()
        text = "  Hello World  "
        result = cleaner.clean(text)
        assert result == "Hello World"


class TestCaseTransformer:
    """Test CaseTransformer class"""
    
    def test_lowercase_mode(self):
        """Test: Lowercase transformation"""
        transformer = CaseTransformer(mode='lower')
        result = transformer.clean("Hello WORLD Test")
        assert result == "hello world test"
    
    def test_uppercase_mode(self):
        """Test: Uppercase transformation"""
        transformer = CaseTransformer(mode='upper')
        result = transformer.clean("Hello world test")
        assert result == "HELLO WORLD TEST"
    
    def test_title_mode(self):
        """Test: Title case transformation"""
        transformer = CaseTransformer(mode='title')
        result = transformer.clean("hello world test")
        assert result == "Hello World Test"
    
    def test_capitalize_mode(self):
        """Test: Capitalize transformation"""
        transformer = CaseTransformer(mode='capitalize')
        result = transformer.clean("hello world test")
        assert result == "Hello world test"
    
    def test_invalid_mode(self):
        """Test: Invalid mode raises ValueError"""
        with pytest.raises(ValueError, match="Invalid mode"):
            CaseTransformer(mode='invalid')
    
    def test_empty_text(self):
        """Test: Empty text returns empty"""
        transformer = CaseTransformer(mode='lower')
        assert transformer.clean("") == ""


class TestCharacterTransformer:
    """Test CharacterTransformer class"""
    
    def test_letters_only(self):
        """Test: Keep only letters"""
        transformer = CharacterTransformer(
            allow_letters=True,
            allow_digits=False,
            allow_spaces=False,
            allow_punctuation=False
        )
        result = transformer.clean("Hello123 World!")
        assert result == "HelloWorld"
    
    def test_digits_only(self):
        """Test: Keep only digits"""
        transformer = CharacterTransformer(
            allow_letters=False,
            allow_digits=True,
            allow_spaces=False,
            allow_punctuation=False
        )
        result = transformer.clean("Test123Hello456")
        assert result == "123456"
    
    def test_letters_and_spaces(self):
        """Test: Keep letters and spaces"""
        transformer = CharacterTransformer(
            allow_letters=True,
            allow_digits=False,
            allow_spaces=True,
            allow_punctuation=False
        )
        result = transformer.clean("Hello123 World456!")
        assert result == "Hello World"
    
    def test_alphanumeric(self):
        """Test: Keep letters and digits"""
        transformer = CharacterTransformer(
            allow_letters=True,
            allow_digits=True,
            allow_spaces=False,
            allow_punctuation=False
        )
        result = transformer.clean("Hello123 World456!")
        assert result == "Hello123World456"
    
    def test_empty_after_filtering(self):
        """Test: ValueError if text is empty after filtering"""
        transformer = CharacterTransformer(
            allow_letters=True,
            allow_digits=False,
            allow_spaces=False,
            allow_punctuation=False
        )
        with pytest.raises(ValueError, match="Text is empty after filtering"):
            transformer.clean("123!@#")
    
    def test_letters_only_static(self):
        """Test: Static letters_only method"""
        result = CharacterTransformer.letters_only("Hello123 World!")
        assert result == "HelloWorld"
    
    def test_alphanumeric_only_static(self):
        """Test: Static alphanumeric_only method"""
        result = CharacterTransformer.alphanumeric_only("Hello123 World!")
        assert result == "Hello123World"
    
    def test_empty_text(self):
        """Test: Empty text returns empty"""
        transformer = CharacterTransformer()
        assert transformer.clean("") == ""
    
    def test_all_character_types(self):
        """Test: Allow all character types"""
        transformer = CharacterTransformer(
            allow_letters=True,
            allow_digits=True,
            allow_spaces=True,
            allow_punctuation=True
        )
        text = "Hello123 World!"
        result = transformer.clean(text)
        assert result == text
