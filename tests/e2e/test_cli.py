"""End-to-end tests for CLI"""

import pytest
import tempfile
import os
from click.testing import CliRunner
from markov_passgen.cli import main


class TestCLI:
    """End-to-end tests for command-line interface"""
    
    def test_full_generation_workflow(self):
        """Test complete workflow: corpus -> generate -> output"""
        # Create sample corpus file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            corpus_text = "the quick brown fox jumps over the lazy dog " * 20
            f.write(corpus_text)
            corpus_path = f.name
        
        # Create temporary output file path
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            output_path = f.name
        
        try:
            runner = CliRunner()
            result = runner.invoke(main, [
                'generate',
                '--corpus', corpus_path,
                '--count', '10',
                '--length', '8',
                '--random-seed', '42',  # Use fixed seed for deterministic testing
                '--output', output_path
            ])
            
            # Check command succeeded
            assert result.exit_code == 0
            
            # Check output file exists and has content
            assert os.path.exists(output_path)
            
            with open(output_path, 'r', encoding='utf-8') as f:
                passwords = f.readlines()
            
            # Should have 10 passwords
            assert len(passwords) == 10
            
            # Each password should be 8 characters (plus newline)
            for i, pwd in enumerate(passwords):
                pwd_stripped = pwd.strip()
                assert len(pwd_stripped) == 8, f"Password {i+1} '{pwd_stripped}' has length {len(pwd_stripped)}, expected 8"
        
        finally:
            os.unlink(corpus_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_cli_help(self):
        """Test CLI help command"""
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert 'Markov Chain Password Generator' in result.output
    
    def test_generate_help(self):
        """Test generate subcommand help"""
        runner = CliRunner()
        result = runner.invoke(main, ['generate', '--help'])
        assert result.exit_code == 0
        assert 'Generate passwords from corpus' in result.output
    
    def test_invalid_corpus_file(self):
        """Test with non-existent corpus file"""
        runner = CliRunner()
        result = runner.invoke(main, [
            'generate',
            '--corpus', 'nonexistent_file.txt',
            '--count', '10',
            '--length', '8'
        ])
        
        # Should fail
        assert result.exit_code != 0
    
    def test_small_corpus(self):
        """Test with corpus that's too small"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("small")  # Only 5 characters
            corpus_path = f.name
        
        try:
            runner = CliRunner()
            result = runner.invoke(main, [
                'generate',
                '--corpus', corpus_path,
                '--count', '5',
                '--length', '8'
            ])
            
            # Should fail validation
            assert result.exit_code != 0
            assert 'at least 100 characters' in result.output
        
        finally:
            os.unlink(corpus_path)
    
    def test_large_batch_generation(self):
        """Test generating larger batch of passwords"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            corpus_text = "abcdefghijklmnopqrstuvwxyz " * 50
            f.write(corpus_text)
            corpus_path = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            output_path = f.name
        
        try:
            runner = CliRunner()
            result = runner.invoke(main, [
                'generate',
                '--corpus', corpus_path,
                '--count', '100',
                '--length', '12',
                '--output', output_path
            ])
            
            assert result.exit_code == 0
            
            with open(output_path, 'r', encoding='utf-8') as f:
                passwords = f.readlines()
            
            assert len(passwords) == 100
        
        finally:
            os.unlink(corpus_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
