"""Unit tests for NGramVisualizer"""

import pytest
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt
from markov_passgen.visualization.visualizer import NGramVisualizer
from markov_passgen.core.entropy_calculator import EntropyCalculator


@pytest.fixture
def sample_ngram_model():
    """Create sample n-gram model"""
    return {
        "th": {"e": 100, "i": 50, "a": 30},
        "he": {" ": 80, "r": 60, "l": 40},
        "qu": {"i": 90, "e": 70},
        "br": {"o": 85, "i": 45},
        "fo": {"x": 95, "r": 55},
    }


@pytest.fixture
def sample_passwords():
    """Create sample password list"""
    return [
        "password123",
        "helloworld",
        "securepass",
        "testword",
        "example123",
        "sample456",
        "demo789",
        "tryit123",
    ]


@pytest.fixture
def sample_corpus_stats():
    """Create sample corpus statistics"""
    return {
        "corpus_0": {
            "char_count": 500,
            "word_count": 100,
            "unique_chars": 30,
            "weight": 1.0
        },
        "corpus_1": {
            "char_count": 750,
            "word_count": 150,
            "unique_chars": 35,
            "weight": 2.0
        },
        "corpus_2": {
            "char_count": 600,
            "word_count": 120,
            "unique_chars": 32,
            "weight": 1.5
        }
    }


class TestNGramVisualizerInit:
    """Test NGramVisualizer initialization"""
    
    def test_init_default_style(self):
        """Should initialize with default style"""
        visualizer = NGramVisualizer()
        assert visualizer is not None
    
    def test_init_custom_style(self):
        """Should initialize with custom style"""
        visualizer = NGramVisualizer(style="default")
        assert visualizer is not None
    
    def test_init_invalid_style_fallback(self):
        """Should fallback to default if style invalid"""
        visualizer = NGramVisualizer(style="nonexistent_style")
        assert visualizer is not None


class TestPlotNGramFrequencies:
    """Test n-gram frequency plotting"""
    
    def test_plot_to_file(self, sample_ngram_model, tmp_path):
        """Should save plot to file"""
        visualizer = NGramVisualizer()
        output = tmp_path / "ngram_freq.png"
        
        visualizer.plot_ngram_frequencies(sample_ngram_model, top_n=5, output_path=str(output))
        
        assert output.exists()
        assert output.stat().st_size > 0
    
    def test_plot_with_default_top_n(self, sample_ngram_model, tmp_path):
        """Should use default top_n=20"""
        visualizer = NGramVisualizer()
        output = tmp_path / "ngram_freq.png"
        
        visualizer.plot_ngram_frequencies(sample_ngram_model, output_path=str(output))
        
        assert output.exists()
    
    def test_plot_empty_model(self):
        """Should raise error for empty model"""
        visualizer = NGramVisualizer()
        
        with pytest.raises(ValueError, match="N-gram model is empty"):
            visualizer.plot_ngram_frequencies({}, output_path="test.png")
    
    def test_plot_more_top_n_than_available(self, sample_ngram_model, tmp_path):
        """Should handle top_n larger than available n-grams"""
        visualizer = NGramVisualizer()
        output = tmp_path / "ngram_freq.png"
        
        visualizer.plot_ngram_frequencies(sample_ngram_model, top_n=100, output_path=str(output))
        
        assert output.exists()
    
    def test_plot_closes_figure(self, sample_ngram_model, tmp_path):
        """Should close figure after saving"""
        visualizer = NGramVisualizer()
        output = tmp_path / "ngram_freq.png"
        
        initial_figs = len(plt.get_fignums())
        visualizer.plot_ngram_frequencies(sample_ngram_model, output_path=str(output))
        final_figs = len(plt.get_fignums())
        
        assert final_figs == initial_figs


class TestPlotEntropyDistribution:
    """Test entropy distribution plotting"""
    
    def test_plot_entropy_to_file(self, sample_passwords, tmp_path):
        """Should save entropy plot to file"""
        visualizer = NGramVisualizer()
        entropy_calc = EntropyCalculator()
        output = tmp_path / "entropy_dist.png"
        
        visualizer.plot_entropy_distribution(sample_passwords, entropy_calc, output_path=str(output))
        
        assert output.exists()
        assert output.stat().st_size > 0
    
    def test_plot_entropy_custom_bins(self, sample_passwords, tmp_path):
        """Should accept custom bin count"""
        visualizer = NGramVisualizer()
        entropy_calc = EntropyCalculator()
        output = tmp_path / "entropy_dist.png"
        
        visualizer.plot_entropy_distribution(sample_passwords, entropy_calc, bins=50, output_path=str(output))
        
        assert output.exists()
    
    def test_plot_entropy_empty_list(self):
        """Should raise error for empty password list"""
        visualizer = NGramVisualizer()
        entropy_calc = EntropyCalculator()
        
        with pytest.raises(ValueError, match="Password list is empty"):
            visualizer.plot_entropy_distribution([], entropy_calc, output_path="test.png")
    
    def test_plot_entropy_single_password(self, tmp_path):
        """Should handle single password"""
        visualizer = NGramVisualizer()
        entropy_calc = EntropyCalculator()
        output = tmp_path / "entropy_dist.png"
        
        visualizer.plot_entropy_distribution(["password"], entropy_calc, output_path=str(output))
        
        assert output.exists()


class TestPlotCorpusComparison:
    """Test corpus comparison plotting"""
    
    def test_plot_comparison_to_file(self, sample_corpus_stats, tmp_path):
        """Should save corpus comparison plot to file"""
        visualizer = NGramVisualizer()
        output = tmp_path / "corpus_compare.png"
        
        visualizer.plot_corpus_comparison(sample_corpus_stats, output_path=str(output))
        
        assert output.exists()
        assert output.stat().st_size > 0
    
    def test_plot_comparison_empty_stats(self):
        """Should raise error for empty statistics"""
        visualizer = NGramVisualizer()
        
        with pytest.raises(ValueError, match="Corpus statistics is empty"):
            visualizer.plot_corpus_comparison({}, output_path="test.png")
    
    def test_plot_comparison_single_corpus(self, tmp_path):
        """Should handle single corpus"""
        visualizer = NGramVisualizer()
        output = tmp_path / "corpus_compare.png"
        
        stats = {
            "corpus_0": {
                "char_count": 500,
                "word_count": 100,
                "unique_chars": 30,
                "weight": 1.0
            }
        }
        
        visualizer.plot_corpus_comparison(stats, output_path=str(output))
        
        assert output.exists()


class TestPlotLengthDistribution:
    """Test password length distribution plotting"""
    
    def test_plot_length_to_file(self, sample_passwords, tmp_path):
        """Should save length distribution plot to file"""
        visualizer = NGramVisualizer()
        output = tmp_path / "length_dist.png"
        
        visualizer.plot_length_distribution(sample_passwords, output_path=str(output))
        
        assert output.exists()
        assert output.stat().st_size > 0
    
    def test_plot_length_custom_bins(self, sample_passwords, tmp_path):
        """Should accept custom bin count"""
        visualizer = NGramVisualizer()
        output = tmp_path / "length_dist.png"
        
        visualizer.plot_length_distribution(sample_passwords, bins=50, output_path=str(output))
        
        assert output.exists()
    
    def test_plot_length_empty_list(self):
        """Should raise error for empty password list"""
        visualizer = NGramVisualizer()
        
        with pytest.raises(ValueError, match="Password list is empty"):
            visualizer.plot_length_distribution([], output_path="test.png")
    
    def test_plot_length_single_password(self, tmp_path):
        """Should handle single password"""
        visualizer = NGramVisualizer()
        output = tmp_path / "length_dist.png"
        
        visualizer.plot_length_distribution(["pass"], output_path=str(output))
        
        assert output.exists()


class TestPlotCharacterDistribution:
    """Test character distribution plotting"""
    
    def test_plot_char_dist_to_file(self, tmp_path):
        """Should save character distribution plot to file"""
        visualizer = NGramVisualizer()
        output = tmp_path / "char_dist.png"
        text = "the quick brown fox jumps over the lazy dog " * 10
        
        visualizer.plot_character_distribution(text, output_path=str(output))
        
        assert output.exists()
        assert output.stat().st_size > 0
    
    def test_plot_char_dist_custom_top_n(self, tmp_path):
        """Should accept custom top_n"""
        visualizer = NGramVisualizer()
        output = tmp_path / "char_dist.png"
        text = "abcdefghijklmnopqrstuvwxyz" * 10
        
        visualizer.plot_character_distribution(text, top_n=10, output_path=str(output))
        
        assert output.exists()
    
    def test_plot_char_dist_empty_text(self):
        """Should raise error for empty text"""
        visualizer = NGramVisualizer()
        
        with pytest.raises(ValueError, match="Text corpus is empty"):
            visualizer.plot_character_distribution("", output_path="test.png")
    
    def test_plot_char_dist_whitespace_only(self):
        """Should raise error for whitespace-only text"""
        visualizer = NGramVisualizer()
        
        with pytest.raises(ValueError, match="No characters to visualize"):
            visualizer.plot_character_distribution("   \n\t   ", output_path="test.png")


class TestCloseAll:
    """Test close_all utility"""
    
    def test_close_all_figures(self, sample_ngram_model, tmp_path):
        """Should close all open figures"""
        visualizer = NGramVisualizer()
        
        # Create multiple plots without closing
        output1 = tmp_path / "plot1.png"
        output2 = tmp_path / "plot2.png"
        
        # Don't specify output to keep figures open
        plt.figure()
        plt.plot([1, 2, 3])
        plt.figure()
        plt.plot([4, 5, 6])
        
        initial_figs = len(plt.get_fignums())
        assert initial_figs >= 2
        
        NGramVisualizer.close_all()
        
        final_figs = len(plt.get_fignums())
        assert final_figs == 0


class TestOutputFormats:
    """Test different output formats"""
    
    def test_save_as_png(self, sample_passwords, tmp_path):
        """Should save as PNG"""
        visualizer = NGramVisualizer()
        output = tmp_path / "test.png"
        
        visualizer.plot_length_distribution(sample_passwords, output_path=str(output))
        
        assert output.suffix == ".png"
        assert output.exists()
    
    def test_save_as_jpg(self, sample_passwords, tmp_path):
        """Should save as JPG"""
        visualizer = NGramVisualizer()
        output = tmp_path / "test.jpg"
        
        visualizer.plot_length_distribution(sample_passwords, output_path=str(output))
        
        assert output.suffix == ".jpg"
        assert output.exists()
    
    def test_save_as_svg(self, sample_passwords, tmp_path):
        """Should save as SVG"""
        visualizer = NGramVisualizer()
        output = tmp_path / "test.svg"
        
        visualizer.plot_length_distribution(sample_passwords, output_path=str(output))
        
        assert output.suffix == ".svg"
        assert output.exists()
    
    def test_save_as_pdf(self, sample_passwords, tmp_path):
        """Should save as PDF"""
        visualizer = NGramVisualizer()
        output = tmp_path / "test.pdf"
        
        visualizer.plot_length_distribution(sample_passwords, output_path=str(output))
        
        assert output.suffix == ".pdf"
        assert output.exists()
