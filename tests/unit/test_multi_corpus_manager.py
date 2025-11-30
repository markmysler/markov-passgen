"""Unit tests for MultiCorpusManager"""

import pytest
from pathlib import Path
from markov_passgen.core.multi_corpus_manager import MultiCorpusManager
from markov_passgen.transformers.text_cleaner import TextCleaner


@pytest.fixture
def sample_corpus_file(tmp_path):
    """Create temporary corpus file"""
    file = tmp_path / "test_corpus.txt"
    file.write_text("the quick brown fox")
    return str(file)


@pytest.fixture
def second_corpus_file(tmp_path):
    """Create second temporary corpus file"""
    file = tmp_path / "test_corpus2.txt"
    file.write_text("jumps over the lazy dog")
    return str(file)


class TestMultiCorpusManagerInit:
    """Test MultiCorpusManager initialization"""
    
    def test_init_creates_empty_manager(self):
        """Should initialize with no corpora"""
        manager = MultiCorpusManager()
        assert manager.count() == 0
        assert manager.list_corpora() == []


class TestAddCorpus:
    """Test adding corpus sources"""
    
    def test_add_corpus_from_file(self, sample_corpus_file):
        """Should add corpus from file"""
        manager = MultiCorpusManager()
        manager.add_corpus("test", sample_corpus_file)
        
        assert manager.count() == 1
        assert "test" in manager.list_corpora()
    
    def test_add_corpus_with_default_weight(self, sample_corpus_file):
        """Should use default weight of 1.0"""
        manager = MultiCorpusManager()
        manager.add_corpus("test", sample_corpus_file)
        
        assert manager.get_weight("test") == 1.0
    
    def test_add_corpus_with_custom_weight(self, sample_corpus_file):
        """Should store custom weight"""
        manager = MultiCorpusManager()
        manager.add_corpus("test", sample_corpus_file, weight=2.5)
        
        assert manager.get_weight("test") == 2.5
    
    def test_add_corpus_with_cleaner(self, tmp_path):
        """Should apply text cleaner when loading"""
        file = tmp_path / "test.txt"
        file.write_text("HELLO WORLD!")
        
        manager = MultiCorpusManager()
        cleaner = TextCleaner(lowercase=True, remove_punctuation=True)
        manager.add_corpus("test", str(file), cleaner=cleaner)
        
        merged = manager.get_merged_corpus()
        assert "hello world" in merged
        assert "HELLO" not in merged
    
    def test_add_corpus_invalid_weight(self, sample_corpus_file):
        """Should reject non-positive weights"""
        manager = MultiCorpusManager()
        
        with pytest.raises(ValueError, match="Weight must be positive"):
            manager.add_corpus("test", sample_corpus_file, weight=0)
        
        with pytest.raises(ValueError, match="Weight must be positive"):
            manager.add_corpus("test", sample_corpus_file, weight=-1.0)
    
    def test_add_corpus_duplicate_name(self, sample_corpus_file):
        """Should reject duplicate corpus names"""
        manager = MultiCorpusManager()
        manager.add_corpus("test", sample_corpus_file)
        
        with pytest.raises(ValueError, match="already exists"):
            manager.add_corpus("test", sample_corpus_file)
    
    def test_add_corpus_file_not_found(self):
        """Should raise error for nonexistent file"""
        manager = MultiCorpusManager()
        
        with pytest.raises(FileNotFoundError):
            manager.add_corpus("test", "nonexistent.txt")
    
    def test_add_multiple_corpora(self, sample_corpus_file, second_corpus_file):
        """Should support multiple corpora"""
        manager = MultiCorpusManager()
        manager.add_corpus("corpus1", sample_corpus_file)
        manager.add_corpus("corpus2", second_corpus_file)
        
        assert manager.count() == 2
        assert "corpus1" in manager.list_corpora()
        assert "corpus2" in manager.list_corpora()


class TestAddCorpusText:
    """Test adding corpus from text"""
    
    def test_add_corpus_text(self):
        """Should add corpus from text string"""
        manager = MultiCorpusManager()
        manager.add_corpus_text("test", "hello world")
        
        assert manager.count() == 1
        assert "test" in manager.list_corpora()
    
    def test_add_corpus_text_with_weight(self):
        """Should store custom weight for text corpus"""
        manager = MultiCorpusManager()
        manager.add_corpus_text("test", "hello world", weight=2.0)
        
        assert manager.get_weight("test") == 2.0
    
    def test_add_corpus_text_invalid_weight(self):
        """Should reject non-positive weights for text corpus"""
        manager = MultiCorpusManager()
        
        with pytest.raises(ValueError, match="Weight must be positive"):
            manager.add_corpus_text("test", "hello", weight=0)
    
    def test_add_corpus_text_duplicate_name(self):
        """Should reject duplicate names for text corpus"""
        manager = MultiCorpusManager()
        manager.add_corpus_text("test", "hello")
        
        with pytest.raises(ValueError, match="already exists"):
            manager.add_corpus_text("test", "world")


class TestRemoveCorpus:
    """Test removing corpus sources"""
    
    def test_remove_corpus(self, sample_corpus_file):
        """Should remove corpus"""
        manager = MultiCorpusManager()
        manager.add_corpus("test", sample_corpus_file)
        manager.remove_corpus("test")
        
        assert manager.count() == 0
        assert "test" not in manager.list_corpora()
    
    def test_remove_nonexistent_corpus(self):
        """Should raise error for nonexistent corpus"""
        manager = MultiCorpusManager()
        
        with pytest.raises(KeyError, match="not found"):
            manager.remove_corpus("test")


class TestGetMergedCorpus:
    """Test merging corpora"""
    
    def test_get_merged_corpus_single(self):
        """Should return single corpus unchanged"""
        manager = MultiCorpusManager()
        manager.add_corpus_text("test", "hello world")
        
        merged = manager.get_merged_corpus()
        # Single corpus with weight 1.0 gets repeated 10 times
        assert "hello world" in merged
    
    def test_get_merged_corpus_multiple_equal_weights(self):
        """Should merge corpora with equal weights"""
        manager = MultiCorpusManager()
        manager.add_corpus_text("corpus1", "hello")
        manager.add_corpus_text("corpus2", "world")
        
        merged = manager.get_merged_corpus()
        assert "hello" in merged
        assert "world" in merged
    
    def test_get_merged_corpus_different_weights(self):
        """Should apply weights when merging"""
        manager = MultiCorpusManager()
        manager.add_corpus_text("corpus1", "hello", weight=1.0)
        manager.add_corpus_text("corpus2", "world", weight=2.0)
        
        merged = manager.get_merged_corpus()
        # corpus2 should appear more due to higher weight
        hello_count = merged.count("hello")
        world_count = merged.count("world")
        assert world_count > hello_count
    
    def test_get_merged_corpus_empty(self):
        """Should raise error when no corpora"""
        manager = MultiCorpusManager()
        
        with pytest.raises(ValueError, match="No corpora"):
            manager.get_merged_corpus()


class TestGetCorpusStats:
    """Test corpus statistics"""
    
    def test_get_corpus_stats(self):
        """Should return statistics for all corpora"""
        manager = MultiCorpusManager()
        manager.add_corpus_text("test", "hello world", weight=2.0)
        
        stats = manager.get_corpus_stats()
        assert "test" in stats
        assert stats["test"]["char_count"] == 11
        assert stats["test"]["word_count"] == 2
        assert stats["test"]["weight"] == 2.0
    
    def test_get_corpus_stats_multiple(self):
        """Should return stats for all corpora"""
        manager = MultiCorpusManager()
        manager.add_corpus_text("corpus1", "hello")
        manager.add_corpus_text("corpus2", "world!")
        
        stats = manager.get_corpus_stats()
        assert len(stats) == 2
        assert "corpus1" in stats
        assert "corpus2" in stats


class TestListCorpora:
    """Test listing corpora"""
    
    def test_list_corpora_empty(self):
        """Should return empty list when no corpora"""
        manager = MultiCorpusManager()
        assert manager.list_corpora() == []
    
    def test_list_corpora_single(self):
        """Should list single corpus"""
        manager = MultiCorpusManager()
        manager.add_corpus_text("test", "hello")
        
        assert manager.list_corpora() == ["test"]
    
    def test_list_corpora_multiple(self):
        """Should list all corpora"""
        manager = MultiCorpusManager()
        manager.add_corpus_text("corpus1", "hello")
        manager.add_corpus_text("corpus2", "world")
        
        corpora = manager.list_corpora()
        assert len(corpora) == 2
        assert "corpus1" in corpora
        assert "corpus2" in corpora


class TestGetWeight:
    """Test getting corpus weights"""
    
    def test_get_weight(self):
        """Should return corpus weight"""
        manager = MultiCorpusManager()
        manager.add_corpus_text("test", "hello", weight=2.5)
        
        assert manager.get_weight("test") == 2.5
    
    def test_get_weight_nonexistent(self):
        """Should raise error for nonexistent corpus"""
        manager = MultiCorpusManager()
        
        with pytest.raises(KeyError, match="not found"):
            manager.get_weight("test")


class TestSetWeight:
    """Test updating corpus weights"""
    
    def test_set_weight(self):
        """Should update corpus weight"""
        manager = MultiCorpusManager()
        manager.add_corpus_text("test", "hello", weight=1.0)
        manager.set_weight("test", 2.5)
        
        assert manager.get_weight("test") == 2.5
    
    def test_set_weight_invalid(self):
        """Should reject non-positive weights"""
        manager = MultiCorpusManager()
        manager.add_corpus_text("test", "hello")
        
        with pytest.raises(ValueError, match="Weight must be positive"):
            manager.set_weight("test", 0)
    
    def test_set_weight_nonexistent(self):
        """Should raise error for nonexistent corpus"""
        manager = MultiCorpusManager()
        
        with pytest.raises(KeyError, match="not found"):
            manager.set_weight("test", 2.0)


class TestClear:
    """Test clearing all corpora"""
    
    def test_clear(self):
        """Should remove all corpora"""
        manager = MultiCorpusManager()
        manager.add_corpus_text("corpus1", "hello")
        manager.add_corpus_text("corpus2", "world")
        
        manager.clear()
        
        assert manager.count() == 0
        assert manager.list_corpora() == []


class TestCount:
    """Test counting corpora"""
    
    def test_count_empty(self):
        """Should return 0 for empty manager"""
        manager = MultiCorpusManager()
        assert manager.count() == 0
    
    def test_count_single(self):
        """Should count single corpus"""
        manager = MultiCorpusManager()
        manager.add_corpus_text("test", "hello")
        assert manager.count() == 1
    
    def test_count_multiple(self):
        """Should count all corpora"""
        manager = MultiCorpusManager()
        manager.add_corpus_text("corpus1", "hello")
        manager.add_corpus_text("corpus2", "world")
        manager.add_corpus_text("corpus3", "test")
        assert manager.count() == 3


class TestFromFiles:
    """Test factory method for creating from files"""
    
    def test_from_files_default_weights(self, sample_corpus_file, second_corpus_file):
        """Should create manager with default weights"""
        manager = MultiCorpusManager.from_files([sample_corpus_file, second_corpus_file])
        
        assert manager.count() == 2
        assert manager.get_weight("corpus_0") == 1.0
        assert manager.get_weight("corpus_1") == 1.0
    
    def test_from_files_custom_weights(self, sample_corpus_file, second_corpus_file):
        """Should create manager with custom weights"""
        manager = MultiCorpusManager.from_files(
            [sample_corpus_file, second_corpus_file],
            weights=[1.0, 2.0]
        )
        
        assert manager.count() == 2
        assert manager.get_weight("corpus_0") == 1.0
        assert manager.get_weight("corpus_1") == 2.0
    
    def test_from_files_with_cleaner(self, tmp_path):
        """Should apply cleaner to all files"""
        file1 = tmp_path / "test1.txt"
        file1.write_text("HELLO WORLD")
        file2 = tmp_path / "test2.txt"
        file2.write_text("FOO BAR")
        
        cleaner = TextCleaner(lowercase=True)
        manager = MultiCorpusManager.from_files([str(file1), str(file2)], cleaner=cleaner)
        
        merged = manager.get_merged_corpus()
        assert "hello world" in merged
        assert "foo bar" in merged
        assert "HELLO" not in merged
    
    def test_from_files_weight_length_mismatch(self, sample_corpus_file):
        """Should raise error if weights length doesn't match files"""
        with pytest.raises(ValueError, match="must match number of files"):
            MultiCorpusManager.from_files([sample_corpus_file], weights=[1.0, 2.0])
