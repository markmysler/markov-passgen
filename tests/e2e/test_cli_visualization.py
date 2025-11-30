"""E2E tests for visualization CLI commands"""

import pytest
import subprocess
from pathlib import Path


@pytest.fixture
def sample_corpus(tmp_path):
    """Create sample corpus file"""
    file = tmp_path / "test_corpus.txt"
    file.write_text("the quick brown fox jumps over the lazy dog " * 20)
    return str(file)


@pytest.fixture
def sample_wordlist(tmp_path):
    """Create sample wordlist file"""
    file = tmp_path / "wordlist.txt"
    passwords = [
        "password123",
        "helloworld",
        "testword",
        "example456",
        "sample789",
    ] * 10
    file.write_text("\n".join(passwords))
    return str(file)


class TestVisualizeCLI:
    """Test visualization CLI commands"""
    
    def test_visualize_corpus_ngram_freq(self, sample_corpus, tmp_path):
        """Should generate n-gram frequency plot via CLI"""
        output = tmp_path / "ngram.png"
        
        result = subprocess.run([
            "markov-passgen", "visualize-corpus",
            "--corpus", sample_corpus,
            "--ngram-freq", str(output),
            "--top-n", "10"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert output.exists()
        assert "Loading corpus" in result.stdout
        assert "N-gram frequency plot saved" in result.stdout
    
    def test_visualize_corpus_char_dist(self, sample_corpus, tmp_path):
        """Should generate character distribution plot via CLI"""
        output = tmp_path / "char.png"
        
        result = subprocess.run([
            "markov-passgen", "visualize-corpus",
            "--corpus", sample_corpus,
            "--char-dist", str(output),
            "--top-n", "15"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert output.exists()
        assert "Character distribution plot saved" in result.stdout
    
    def test_visualize_corpus_both_plots(self, sample_corpus, tmp_path):
        """Should generate both plots via CLI"""
        ngram_out = tmp_path / "ngram.png"
        char_out = tmp_path / "char.png"
        
        result = subprocess.run([
            "markov-passgen", "visualize-corpus",
            "--corpus", sample_corpus,
            "--ngram-freq", str(ngram_out),
            "--char-dist", str(char_out)
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert ngram_out.exists()
        assert char_out.exists()
    
    def test_visualize_corpus_no_output(self, sample_corpus):
        """Should show error when no output specified"""
        result = subprocess.run([
            "markov-passgen", "visualize-corpus",
            "--corpus", sample_corpus
        ], capture_output=True, text=True)
        
        # Should complete but warn about no output (message is in stderr)
        assert "No visualization output specified" in result.stderr
    
    def test_visualize_passwords_entropy(self, sample_wordlist, tmp_path):
        """Should generate entropy distribution plot via CLI"""
        output = tmp_path / "entropy.png"
        
        result = subprocess.run([
            "markov-passgen", "visualize-passwords",
            "--wordlist", sample_wordlist,
            "--entropy-dist", str(output),
            "--bins", "20"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert output.exists()
        assert "Loading passwords" in result.stdout
        assert "Entropy distribution plot saved" in result.stdout
    
    def test_visualize_passwords_length(self, sample_wordlist, tmp_path):
        """Should generate length distribution plot via CLI"""
        output = tmp_path / "length.png"
        
        result = subprocess.run([
            "markov-passgen", "visualize-passwords",
            "--wordlist", sample_wordlist,
            "--length-dist", str(output),
            "--bins", "15"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert output.exists()
        assert "Length distribution plot saved" in result.stdout
    
    def test_visualize_passwords_both_plots(self, sample_wordlist, tmp_path):
        """Should generate both password plots via CLI"""
        entropy_out = tmp_path / "entropy.png"
        length_out = tmp_path / "length.png"
        
        result = subprocess.run([
            "markov-passgen", "visualize-passwords",
            "--wordlist", sample_wordlist,
            "--entropy-dist", str(entropy_out),
            "--length-dist", str(length_out)
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert entropy_out.exists()
        assert length_out.exists()
    
    def test_visualize_multi_corpus(self, tmp_path):
        """Should generate multi-corpus comparison plot via CLI"""
        # Create multiple corpus files
        corpus1 = tmp_path / "corpus1.txt"
        corpus1.write_text("the quick brown fox " * 10)
        corpus2 = tmp_path / "corpus2.txt"
        corpus2.write_text("jumps over lazy dog " * 10)
        corpus3 = tmp_path / "corpus3.txt"
        corpus3.write_text("hello world test " * 10)
        
        output = tmp_path / "comparison.png"
        
        result = subprocess.run([
            "markov-passgen", "visualize-multi-corpus",
            "--corpus-list", str(corpus1),
            "--corpus-list", str(corpus2),
            "--corpus-list", str(corpus3),
            "--corpus-weights", "1.0,2.0,1.5",
            "--output", str(output)
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert output.exists()
        assert "Loading 3 corpus files" in result.stdout
        assert "Corpus comparison plot saved" in result.stdout
    
    def test_visualize_multi_corpus_no_weights(self, tmp_path):
        """Should generate comparison with default weights"""
        corpus1 = tmp_path / "corpus1.txt"
        corpus1.write_text("test one " * 10)
        corpus2 = tmp_path / "corpus2.txt"
        corpus2.write_text("test two " * 10)
        
        output = tmp_path / "comparison.png"
        
        result = subprocess.run([
            "markov-passgen", "visualize-multi-corpus",
            "--corpus-list", str(corpus1),
            "--corpus-list", str(corpus2),
            "--output", str(output)
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert output.exists()
