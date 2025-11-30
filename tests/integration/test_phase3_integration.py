"""Integration tests for Phase 3 text processing"""

import pytest
import tempfile
import os
from markov_passgen.core.corpus_loader import CorpusLoader
from markov_passgen.core.ngram_builder import NGramBuilder
from markov_passgen.core.generator import PasswordGenerator
from markov_passgen.transformers.text_cleaner import TextCleaner
from markov_passgen.transformers.case_transformer import CaseTransformer
from markov_passgen.transformers.character_transformer import CharacterTransformer


class TestTextProcessingPipeline:
    """Test complete pipeline with text processing"""
    
    def test_corpus_with_lowercase(self):
        """Test: Load corpus with lowercase preprocessing"""
        corpus_text = "The QUICK Brown FOX Jumps" * 20
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write(corpus_text)
            filepath = f.name
        
        try:
            loader = CorpusLoader()
            cleaner = TextCleaner(lowercase=True)
            text = loader.load_from_file(filepath, cleaner=cleaner)
            
            # Verify all lowercase
            assert text == text.lower()
            assert "QUICK" not in text
            assert "quick" in text
        finally:
            os.unlink(filepath)
    
    def test_corpus_with_punctuation_removal(self):
        """Test: Load corpus with punctuation removal"""
        corpus_text = "Hello, World! How are you? I'm fine." * 20
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write(corpus_text)
            filepath = f.name
        
        try:
            loader = CorpusLoader()
            cleaner = TextCleaner(remove_punctuation=True)
            text = loader.load_from_file(filepath, cleaner=cleaner)
            
            # Verify no punctuation
            assert "," not in text
            assert "!" not in text
            assert "?" not in text
            assert "'" not in text
        finally:
            os.unlink(filepath)
    
    def test_corpus_with_digit_removal(self):
        """Test: Load corpus with digit removal"""
        corpus_text = "Test123 with456 numbers789 everywhere" * 20
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write(corpus_text)
            filepath = f.name
        
        try:
            loader = CorpusLoader()
            cleaner = TextCleaner(remove_digits=True)
            text = loader.load_from_file(filepath, cleaner=cleaner)
            
            # Verify no digits
            assert not any(char.isdigit() for char in text)
            assert "Test" in text
            assert "with" in text
        finally:
            os.unlink(filepath)
    
    def test_corpus_with_multiple_transformations(self):
        """Test: Apply multiple transformations to corpus"""
        corpus_text = "Hello123, WORLD456! Test789?" * 20
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write(corpus_text)
            filepath = f.name
        
        try:
            loader = CorpusLoader()
            cleaner = TextCleaner(
                lowercase=True,
                remove_punctuation=True,
                remove_digits=True,
                normalize_whitespace=True
            )
            text = loader.load_from_file(filepath, cleaner=cleaner)
            
            # Verify all transformations applied
            assert text == text.lower()
            assert not any(char.isdigit() for char in text)
            assert "," not in text
            assert "!" not in text
            assert "  " not in text  # No double spaces
        finally:
            os.unlink(filepath)
    
    def test_generation_with_cleaned_corpus(self):
        """Test: Generate passwords from cleaned corpus"""
        corpus_text = "The QUICK Brown FOX123 Jumps!!!" * 50
        
        # Clean corpus
        cleaner = TextCleaner(
            lowercase=True,
            remove_punctuation=True,
            remove_digits=True,
            normalize_whitespace=True
        )
        cleaned = cleaner.clean(corpus_text)
        
        # Build model and generate
        builder = NGramBuilder()
        model = builder.build(cleaned, n=2)
        
        generator = PasswordGenerator(model)
        passwords = generator.generate(count=20, length=10)
        
        assert len(passwords) == 20
        for pwd in passwords:
            assert len(pwd) == 10
            # Should all be lowercase since corpus was cleaned
            assert pwd == pwd.lower() or any(c.isupper() for c in model.keys())
    
    def test_multiple_files_with_cleaning(self):
        """Test: Load multiple files with cleaning"""
        files = []
        contents = [
            "FIRST Corpus123!!!" * 20,
            "SECOND Corpus456???" * 20,
            "THIRD Corpus789..." * 20
        ]
        
        try:
            for content in contents:
                with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
                    f.write(content)
                    files.append(f.name)
            
            loader = CorpusLoader()
            cleaner = TextCleaner(
                lowercase=True,
                remove_punctuation=True,
                remove_digits=True
            )
            merged = loader.load_from_files(files, cleaner=cleaner)
            
            # Verify cleaning applied to all
            assert merged == merged.lower()
            assert not any(char.isdigit() for char in merged)
            assert "first" in merged
            assert "second" in merged
            assert "third" in merged
        finally:
            for filepath in files:
                if os.path.exists(filepath):
                    os.unlink(filepath)
    
    def test_case_transformer_with_generation(self):
        """Test: Use CaseTransformer with generation pipeline"""
        corpus_text = "hello world test quick brown fox" * 30
        
        # Transform to uppercase
        transformer = CaseTransformer(mode='upper')
        transformed = transformer.clean(corpus_text)
        
        # Build and generate
        builder = NGramBuilder()
        model = builder.build(transformed, n=2)
        
        generator = PasswordGenerator(model)
        passwords = generator.generate(count=10, length=8)
        
        assert len(passwords) == 10
    
    def test_character_transformer_with_generation(self):
        """Test: Use CharacterTransformer with generation pipeline"""
        corpus_text = "Hello123 World456 Test789!!!" * 30
        
        # Keep only letters
        transformer = CharacterTransformer(
            allow_letters=True,
            allow_digits=False,
            allow_spaces=True,
            allow_punctuation=False
        )
        transformed = transformer.clean(corpus_text)
        
        # Verify only letters and spaces
        assert not any(char.isdigit() for char in transformed)
        assert "!" not in transformed
        
        # Build and generate
        builder = NGramBuilder()
        model = builder.build(transformed, n=2)
        
        generator = PasswordGenerator(model)
        passwords = generator.generate(count=10, length=8)
        
        assert len(passwords) == 10


class TestTextCleanerEdgeCases:
    """Test edge cases for text cleaning"""
    
    def test_whitespace_normalization_with_tabs_newlines(self):
        """Test: Normalize tabs and newlines to spaces"""
        cleaner = TextCleaner(normalize_whitespace=True)
        text = "Hello\t\tWorld\n\nTest"
        result = cleaner.clean(text)
        assert result == "Hello World Test"
    
    def test_unicode_text(self):
        """Test: Handle Unicode text"""
        cleaner = TextCleaner(lowercase=True)
        text = "Héllo Wörld Tëst"
        result = cleaner.clean(text)
        assert "héllo" in result.lower()
    
    def test_mixed_case_with_digits(self):
        """Test: Mixed case with digits"""
        cleaner = TextCleaner(lowercase=True, remove_digits=True)
        text = "Test123ABC456def789"
        result = cleaner.clean(text)
        assert result == "testabcdef"
    
    def test_only_punctuation_and_digits(self):
        """Test: Text with only punctuation and digits fails"""
        cleaner = TextCleaner(
            remove_punctuation=True,
            remove_digits=True
        )
        with pytest.raises(ValueError):
            cleaner.clean("123!@#456$%^")
    
    def test_preserve_spaces_between_words(self):
        """Test: Spaces between words are preserved"""
        cleaner = TextCleaner(
            lowercase=True,
            remove_punctuation=True
        )
        text = "Hello, World! How are you?"
        result = cleaner.clean(text)
        assert result == "hello world how are you"
        assert result.count(" ") == 4
