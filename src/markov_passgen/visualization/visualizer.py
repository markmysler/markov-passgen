"""Visualization tools for Markov chain analysis"""

from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import numpy as np


class NGramVisualizer:
    """Visualize n-gram models and password analysis
    
    Single Responsibility: Create visualizations for Markov chain analysis
    """
    
    def __init__(self, style: str = "seaborn-v0_8-darkgrid"):
        """Initialize visualizer with matplotlib style
        
        Args:
            style: Matplotlib style name (default: seaborn-darkgrid)
        """
        try:
            plt.style.use(style)
        except Exception:
            # Fallback to default if style not available
            plt.style.use("default")
        
        # Set seaborn color palette
        sns.set_palette("husl")
    
    def plot_ngram_frequencies(self, ngram_model: Dict[str, Dict[str, int]], 
                               top_n: int = 20, 
                               output_path: Optional[str] = None) -> None:
        """Plot top N most frequent n-grams
        
        Args:
            ngram_model: N-gram frequency dictionary
            top_n: Number of top n-grams to display
            output_path: Optional path to save plot (if None, display interactively)
        """
        if not ngram_model:
            raise ValueError("N-gram model is empty")
        
        # Calculate total frequency for each n-gram prefix
        ngram_counts = {}
        for prefix, next_chars in ngram_model.items():
            total_count = sum(next_chars.values())
            ngram_counts[prefix] = total_count
        
        # Get top N n-grams
        top_ngrams = sorted(ngram_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        if not top_ngrams:
            raise ValueError("No n-grams to visualize")
        
        # Create bar plot
        prefixes = [repr(prefix) for prefix, _ in top_ngrams]
        frequencies = [count for _, count in top_ngrams]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(range(len(prefixes)), frequencies)
        
        # Color bars by frequency
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(bars)))
        for bar, color in zip(bars, colors):
            bar.set_color(color)
        
        ax.set_xlabel("N-gram Prefix", fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        ax.set_title(f"Top {top_n} Most Frequent N-grams", fontsize=14, fontweight="bold")
        ax.set_xticks(range(len(prefixes)))
        ax.set_xticklabels(prefixes, rotation=45, ha="right")
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()
        else:
            plt.show()
    
    def plot_entropy_distribution(self, passwords: List[str], 
                                   entropy_calc, 
                                   bins: int = 30,
                                   output_path: Optional[str] = None) -> None:
        """Plot entropy distribution of passwords
        
        Args:
            passwords: List of passwords to analyze
            entropy_calc: EntropyCalculator instance
            bins: Number of histogram bins
            output_path: Optional path to save plot (if None, display interactively)
        """
        if not passwords:
            raise ValueError("Password list is empty")
        
        # Calculate entropy for each password
        entropies = [entropy_calc.calculate_shannon_entropy(pwd) for pwd in passwords]
        
        # Create histogram with KDE
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot histogram
        n, bins_edges, patches = ax.hist(entropies, bins=bins, alpha=0.7, 
                                         edgecolor="black", linewidth=0.5)
        
        # Color histogram by value
        colors = plt.cm.coolwarm(np.linspace(0.2, 0.8, len(patches)))
        for patch, color in zip(patches, colors):
            patch.set_facecolor(color)
        
        # Add KDE overlay
        try:
            from scipy import stats
            kde = stats.gaussian_kde(entropies)
            x_range = np.linspace(min(entropies), max(entropies), 100)
            kde_values = kde(x_range) * len(entropies) * (bins_edges[1] - bins_edges[0])
            ax.plot(x_range, kde_values, 'k-', linewidth=2, label="KDE")
        except ImportError:
            # scipy not available, skip KDE
            pass
        
        # Add statistics
        mean_entropy = np.mean(entropies)
        median_entropy = np.median(entropies)
        
        ax.axvline(mean_entropy, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_entropy:.2f}')
        ax.axvline(median_entropy, color='green', linestyle='--', linewidth=2, label=f'Median: {median_entropy:.2f}')
        
        ax.set_xlabel("Shannon Entropy (bits)", fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        ax.set_title(f"Entropy Distribution ({len(passwords)} passwords)", 
                    fontsize=14, fontweight="bold")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()
        else:
            plt.show()
    
    def plot_corpus_comparison(self, corpus_stats: Dict[str, Dict[str, int]], 
                               output_path: Optional[str] = None) -> None:
        """Plot comparison of multiple corpus statistics
        
        Args:
            corpus_stats: Dictionary mapping corpus names to their stats
                         (as returned by MultiCorpusManager.get_corpus_stats())
            output_path: Optional path to save plot (if None, display interactively)
        """
        if not corpus_stats:
            raise ValueError("Corpus statistics is empty")
        
        # Extract data
        corpus_names = list(corpus_stats.keys())
        char_counts = [stats["char_count"] for stats in corpus_stats.values()]
        word_counts = [stats["word_count"] for stats in corpus_stats.values()]
        unique_chars = [stats["unique_chars"] for stats in corpus_stats.values()]
        weights = [stats["weight"] for stats in corpus_stats.values()]
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Character counts
        ax1 = axes[0, 0]
        bars1 = ax1.bar(corpus_names, char_counts, color=sns.color_palette("muted", len(corpus_names)))
        ax1.set_ylabel("Character Count", fontsize=11)
        ax1.set_title("Corpus Size (Characters)", fontsize=12, fontweight="bold")
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}',
                    ha='center', va='bottom', fontsize=9)
        
        # 2. Word counts
        ax2 = axes[0, 1]
        bars2 = ax2.bar(corpus_names, word_counts, color=sns.color_palette("pastel", len(corpus_names)))
        ax2.set_ylabel("Word Count", fontsize=11)
        ax2.set_title("Corpus Size (Words)", fontsize=12, fontweight="bold")
        ax2.tick_params(axis='x', rotation=45)
        
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}',
                    ha='center', va='bottom', fontsize=9)
        
        # 3. Unique characters
        ax3 = axes[1, 0]
        bars3 = ax3.bar(corpus_names, unique_chars, color=sns.color_palette("bright", len(corpus_names)))
        ax3.set_ylabel("Unique Character Count", fontsize=11)
        ax3.set_title("Character Diversity", fontsize=12, fontweight="bold")
        ax3.tick_params(axis='x', rotation=45)
        
        for bar in bars3:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9)
        
        # 4. Weights
        ax4 = axes[1, 1]
        bars4 = ax4.bar(corpus_names, weights, color=sns.color_palette("dark", len(corpus_names)))
        ax4.set_ylabel("Weight", fontsize=11)
        ax4.set_title("Corpus Weights", fontsize=12, fontweight="bold")
        ax4.tick_params(axis='x', rotation=45)
        
        for bar in bars4:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontsize=9)
        
        plt.suptitle("Multi-Corpus Comparison", fontsize=16, fontweight="bold", y=0.995)
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()
        else:
            plt.show()
    
    def plot_length_distribution(self, passwords: List[str], 
                                 bins: int = 20,
                                 output_path: Optional[str] = None) -> None:
        """Plot password length distribution
        
        Args:
            passwords: List of passwords to analyze
            bins: Number of histogram bins
            output_path: Optional path to save plot (if None, display interactively)
        """
        if not passwords:
            raise ValueError("Password list is empty")
        
        lengths = [len(pwd) for pwd in passwords]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        n, bins_edges, patches = ax.hist(lengths, bins=bins, alpha=0.8, 
                                         edgecolor="black", linewidth=0.8)
        
        # Color by frequency
        colors = plt.cm.plasma(np.linspace(0.2, 0.9, len(patches)))
        for patch, color in zip(patches, colors):
            patch.set_facecolor(color)
        
        mean_length = np.mean(lengths)
        median_length = np.median(lengths)
        
        ax.axvline(mean_length, color='red', linestyle='--', linewidth=2, 
                  label=f'Mean: {mean_length:.1f}')
        ax.axvline(median_length, color='green', linestyle='--', linewidth=2, 
                  label=f'Median: {median_length:.1f}')
        
        ax.set_xlabel("Password Length", fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        ax.set_title(f"Password Length Distribution ({len(passwords)} passwords)", 
                    fontsize=14, fontweight="bold")
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()
        else:
            plt.show()
    
    def plot_character_distribution(self, text: str, 
                                    top_n: int = 20,
                                    output_path: Optional[str] = None) -> None:
        """Plot character frequency distribution
        
        Args:
            text: Text corpus to analyze
            top_n: Number of top characters to display
            output_path: Optional path to save plot (if None, display interactively)
        """
        if not text:
            raise ValueError("Text corpus is empty")
        
        # Count character frequencies
        char_counts = Counter(text)
        
        # Get top N characters (exclude whitespace for clarity)
        top_chars = sorted(
            [(char, count) for char, count in char_counts.items() if char not in [' ', '\n', '\t']],
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        if not top_chars:
            raise ValueError("No characters to visualize")
        
        characters = [repr(char) for char, _ in top_chars]
        frequencies = [count for _, count in top_chars]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(range(len(characters)), frequencies)
        
        # Color bars by frequency
        colors = plt.cm.Spectral(np.linspace(0.2, 0.9, len(bars)))
        for bar, color in zip(bars, colors):
            bar.set_color(color)
        
        ax.set_xlabel("Character", fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        ax.set_title(f"Top {top_n} Most Frequent Characters", fontsize=14, fontweight="bold")
        ax.set_xticks(range(len(characters)))
        ax.set_xticklabels(characters, rotation=0)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()
        else:
            plt.show()
    
    @staticmethod
    def close_all() -> None:
        """Close all open matplotlib figures"""
        plt.close('all')
