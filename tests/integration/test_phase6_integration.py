"""Integration tests for Phase 6: Visualization features"""

import pytest
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from markov_passgen.visualization.visualizer import NGramVisualizer
from markov_passgen.core.corpus_loader import CorpusLoader
from markov_passgen.core.ngram_builder import NGramBuilder
from markov_passgen.core.generator import PasswordGenerator
from markov_passgen.core.entropy_calculator import EntropyCalculator
from markov_passgen.core.multi_corpus_manager import MultiCorpusManager


@pytest.fixture
def sample_corpus(tmp_path):
    """Create sample corpus file"""
    file = tmp_path / "corpus.txt"
    file.write_text("the quick brown fox jumps over the lazy dog " * 20)
    return str(file)


@pytest.fixture
def multi_corpus_files(tmp_path):
    """Create multiple corpus files"""
    file1 = tmp_path / "corpus1.txt"
    file1.write_text("the quick brown fox " * 10)
    file2 = tmp_path / "corpus2.txt"
    file2.write_text("jumps over the lazy dog " * 10)
    file3 = tmp_path / "corpus3.txt"
    file3.write_text("python java javascript code " * 10)
    return [str(file1), str(file2), str(file3)]


class TestNGramVisualizationPipeline:
    """Test n-gram visualization in full pipeline"""
    
    def test_visualize_ngram_from_corpus(self, sample_corpus, tmp_path):
        """Should create n-gram visualization from corpus"""
        # Load and build model
        loader = CorpusLoader()
        text = loader.load_from_file(sample_corpus)
        builder = NGramBuilder()
        model = builder.build(text, n=2)
        
        # Visualize
        visualizer = NGramVisualizer()
        output = tmp_path / "ngram_freq.png"
        visualizer.plot_ngram_frequencies(model, top_n=10, output_path=str(output))
        
        assert output.exists()
        assert output.stat().st_size > 1000  # Reasonable size for plot
    
    def test_visualize_different_ngram_sizes(self, sample_corpus, tmp_path):
        """Should visualize different n-gram sizes"""
        loader = CorpusLoader()
        text = loader.load_from_file(sample_corpus)
        builder = NGramBuilder()
        visualizer = NGramVisualizer()
        
        for n in [2, 3, 4, 5]:
            model = builder.build(text, n=n)
            output = tmp_path / f"ngram_{n}.png"
            visualizer.plot_ngram_frequencies(model, top_n=10, output_path=str(output))
            
            assert output.exists()
    
    def test_visualize_character_distribution(self, sample_corpus, tmp_path):
        """Should visualize character distribution from corpus"""
        loader = CorpusLoader()
        text = loader.load_from_file(sample_corpus)
        
        visualizer = NGramVisualizer()
        output = tmp_path / "char_dist.png"
        visualizer.plot_character_distribution(text, top_n=15, output_path=str(output))
        
        assert output.exists()


class TestPasswordVisualizationPipeline:
    """Test password visualization in full pipeline"""
    
    def test_visualize_generated_passwords_entropy(self, sample_corpus, tmp_path):
        """Should visualize entropy distribution of generated passwords"""
        # Generate passwords
        loader = CorpusLoader()
        text = loader.load_from_file(sample_corpus)
        builder = NGramBuilder()
        model = builder.build(text, n=2)
        generator = PasswordGenerator(model)
        passwords = generator.generate(100, length=12)
        
        # Visualize entropy
        visualizer = NGramVisualizer()
        entropy_calc = EntropyCalculator()
        output = tmp_path / "entropy_dist.png"
        visualizer.plot_entropy_distribution(passwords, entropy_calc, output_path=str(output))
        
        assert output.exists()
        assert output.stat().st_size > 1000
    
    def test_visualize_generated_passwords_length(self, sample_corpus, tmp_path):
        """Should visualize length distribution of generated passwords"""
        # Generate passwords with varying lengths
        loader = CorpusLoader()
        text = loader.load_from_file(sample_corpus)
        builder = NGramBuilder()
        model = builder.build(text, n=2)
        generator = PasswordGenerator(model)
        
        passwords = []
        for length in [8, 10, 12, 14, 16]:
            passwords.extend(generator.generate(20, length=length))
        
        # Visualize lengths
        visualizer = NGramVisualizer()
        output = tmp_path / "length_dist.png"
        visualizer.plot_length_distribution(passwords, output_path=str(output))
        
        assert output.exists()
    
    def test_visualize_entropy_with_filters(self, sample_corpus, tmp_path):
        """Should visualize entropy of filtered passwords"""
        from markov_passgen.filters.character_filter import CharacterFilter
        
        # Generate and filter passwords
        loader = CorpusLoader()
        text = loader.load_from_file(sample_corpus)
        builder = NGramBuilder()
        model = builder.build(text, n=2)
        generator = PasswordGenerator(model)
        passwords = generator.generate(200, length=12)
        
        # Apply filter
        char_filter = CharacterFilter(require_lowercase=True)
        filtered = char_filter.filter(passwords)
        
        # Visualize
        if filtered:
            visualizer = NGramVisualizer()
            entropy_calc = EntropyCalculator()
            output = tmp_path / "filtered_entropy.png"
            visualizer.plot_entropy_distribution(filtered[:50], entropy_calc, output_path=str(output))
            
            assert output.exists()


class TestMultiCorpusVisualization:
    """Test visualization with multiple corpora"""
    
    def test_visualize_multi_corpus_comparison(self, multi_corpus_files, tmp_path):
        """Should visualize comparison of multiple corpora"""
        # Load multiple corpora
        manager = MultiCorpusManager.from_files(
            multi_corpus_files,
            weights=[1.0, 2.0, 1.5]
        )
        
        # Get statistics
        stats = manager.get_corpus_stats()
        
        # Visualize comparison
        visualizer = NGramVisualizer()
        output = tmp_path / "corpus_compare.png"
        visualizer.plot_corpus_comparison(stats, output_path=str(output))
        
        assert output.exists()
        assert output.stat().st_size > 1000
    
    def test_visualize_merged_corpus_ngrams(self, multi_corpus_files, tmp_path):
        """Should visualize n-grams from merged corpora"""
        # Merge corpora
        manager = MultiCorpusManager.from_files(multi_corpus_files)
        merged = manager.get_merged_corpus()
        
        # Build model
        builder = NGramBuilder()
        model = builder.build(merged, n=2)
        
        # Visualize
        visualizer = NGramVisualizer()
        output = tmp_path / "merged_ngrams.png"
        visualizer.plot_ngram_frequencies(model, top_n=15, output_path=str(output))
        
        assert output.exists()
    
    def test_visualize_weighted_corpus_influence(self, multi_corpus_files, tmp_path):
        """Should show different visualizations for different weights"""
        # Create two managers with different weights
        manager1 = MultiCorpusManager.from_files(multi_corpus_files, weights=[1.0, 1.0, 1.0])
        manager2 = MultiCorpusManager.from_files(multi_corpus_files, weights=[1.0, 5.0, 1.0])
        
        # Get statistics
        stats1 = manager1.get_corpus_stats()
        stats2 = manager2.get_corpus_stats()
        
        # Visualize both
        visualizer = NGramVisualizer()
        output1 = tmp_path / "equal_weights.png"
        output2 = tmp_path / "skewed_weights.png"
        
        visualizer.plot_corpus_comparison(stats1, output_path=str(output1))
        visualizer.plot_corpus_comparison(stats2, output_path=str(output2))
        
        assert output1.exists()
        assert output2.exists()


class TestVisualizationOutputFormats:
    """Test different output formats"""
    
    def test_save_multiple_formats(self, sample_corpus, tmp_path):
        """Should save visualizations in multiple formats"""
        loader = CorpusLoader()
        text = loader.load_from_file(sample_corpus)
        builder = NGramBuilder()
        model = builder.build(text, n=2)
        
        visualizer = NGramVisualizer()
        
        formats = ['png', 'jpg', 'svg', 'pdf']
        for fmt in formats:
            output = tmp_path / f"ngram.{fmt}"
            visualizer.plot_ngram_frequencies(model, top_n=10, output_path=str(output))
            assert output.exists()
            assert output.stat().st_size > 0


class TestVisualizationEdgeCases:
    """Test edge cases in visualization"""
    
    def test_visualize_small_corpus(self, tmp_path):
        """Should handle visualization of small corpus"""
        # Create minimal corpus
        file = tmp_path / "small.txt"
        file.write_text("abc def " * 10)
        
        loader = CorpusLoader()
        text = loader.load_from_file(str(file))
        builder = NGramBuilder()
        model = builder.build(text, n=2)
        
        visualizer = NGramVisualizer()
        output = tmp_path / "small_ngram.png"
        visualizer.plot_ngram_frequencies(model, top_n=5, output_path=str(output))
        
        assert output.exists()
    
    def test_visualize_few_passwords(self, tmp_path):
        """Should handle visualization of few passwords"""
        visualizer = NGramVisualizer()
        entropy_calc = EntropyCalculator()
        
        passwords = ["pass1", "pass2", "pass3"]
        output = tmp_path / "few_entropy.png"
        
        visualizer.plot_entropy_distribution(passwords, entropy_calc, output_path=str(output))
        
        assert output.exists()
    
    def test_visualize_with_custom_bins(self, sample_corpus, tmp_path):
        """Should respect custom bin count"""
        loader = CorpusLoader()
        text = loader.load_from_file(sample_corpus)
        builder = NGramBuilder()
        model = builder.build(text, n=2)
        generator = PasswordGenerator(model)
        passwords = generator.generate(100, length=12)
        
        visualizer = NGramVisualizer()
        entropy_calc = EntropyCalculator()
        
        for bins in [10, 20, 50]:
            output = tmp_path / f"entropy_{bins}bins.png"
            visualizer.plot_entropy_distribution(passwords, entropy_calc, bins=bins, output_path=str(output))
            assert output.exists()


class TestEndToEndVisualization:
    """Test complete end-to-end visualization workflows"""
    
    def test_complete_analysis_workflow(self, sample_corpus, tmp_path):
        """Should perform complete analysis with all visualizations"""
        # Load corpus
        loader = CorpusLoader()
        text = loader.load_from_file(sample_corpus)
        
        # Build model
        builder = NGramBuilder()
        model = builder.build(text, n=2)
        
        # Generate passwords
        generator = PasswordGenerator(model)
        passwords = generator.generate(100, length=12)
        
        # Create all visualizations
        visualizer = NGramVisualizer()
        entropy_calc = EntropyCalculator()
        
        outputs = {
            'ngram': tmp_path / "ngram_freq.png",
            'char': tmp_path / "char_dist.png",
            'entropy': tmp_path / "entropy_dist.png",
            'length': tmp_path / "length_dist.png"
        }
        
        visualizer.plot_ngram_frequencies(model, output_path=str(outputs['ngram']))
        visualizer.plot_character_distribution(text, output_path=str(outputs['char']))
        visualizer.plot_entropy_distribution(passwords, entropy_calc, output_path=str(outputs['entropy']))
        visualizer.plot_length_distribution(passwords, output_path=str(outputs['length']))
        
        # Verify all created
        for output in outputs.values():
            assert output.exists()
            assert output.stat().st_size > 1000
