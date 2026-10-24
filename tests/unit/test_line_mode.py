"""Tests for line-mode models, length control, back-off and weighting"""

import pytest
from click.testing import CliRunner

from markov_passgen.cli import main
from markov_passgen.core.generator import PasswordGenerator
from markov_passgen.core.multi_corpus_manager import MultiCorpusManager
from markov_passgen.core.ngram_builder import END, START, NGramBuilder, is_line_model

WORDS = "\n".join([
    "dragon", "monkey", "shadow", "master", "sunshine", "princess", "football",
    "baseball", "welcome", "letmein", "trustno1", "superman", "batman", "hunter",
    "ranger", "buster", "soccer", "harley", "summer", "winter", "spring", "autumn",
])


class TestBuildLines:
    def test_learns_starts_and_ends_not_line_crossings(self):
        model = NGramBuilder().build_lines("ab\ncd\n", n=2)

        assert is_line_model(model)
        assert model[START * 2] == {"a": 1, "c": 1}
        assert model["ab"] == {END: 1}
        # No transition from the end of "ab" into "cd"
        assert not any(key.startswith("b") for key in model)

    def test_strips_markers_and_blank_lines_from_input(self):
        model = NGramBuilder().build_lines(f"  a{START}b{END}  \n\n   \n", n=2)
        assert model["ab"] == {END: 1}

    def test_rejects_text_without_entries(self):
        with pytest.raises(ValueError):
            NGramBuilder().build_lines("\n  \n", n=2)

    def test_add_to_model_keeps_line_mode(self):
        builder = NGramBuilder()
        builder.build_lines("ab", n=2)
        builder.add_to_model("cd\n")
        assert builder._model[START * 2] == {"a": 1, "c": 1}


class TestLineModeGeneration:
    def test_single_path_corpus_reproduces_the_entry(self):
        generator = PasswordGenerator(NGramBuilder().build_lines("abcd\nabcd\n", n=2))
        assert generator.generate(20) == ["abcd"] * 20

    def test_lengths_follow_the_bounds(self):
        generator = PasswordGenerator(NGramBuilder().build_lines(WORDS, n=3))
        generator.set_random_seed(1)
        candidates = generator.generate(300, min_length=7, max_length=9)
        assert all(7 <= len(c) <= 9 for c in candidates)

    def test_exact_length(self):
        generator = PasswordGenerator(NGramBuilder().build_lines(WORDS, n=3))
        assert {len(c) for c in generator.generate(100, length=14)} == {14}

    def test_natural_lengths_vary_and_never_contain_line_breaks(self):
        generator = PasswordGenerator(NGramBuilder().build_lines(WORDS, n=2))
        generator.set_random_seed(3)
        candidates = generator.generate(200)
        assert len({len(c) for c in candidates}) > 3
        assert not any("\n" in c or START in c or END in c for c in candidates)

    def test_seed_word_starts_every_candidate(self):
        generator = PasswordGenerator(NGramBuilder().build_lines(WORDS, n=2))
        assert all(c.startswith("sun") for c in generator.generate(20, seed="sun"))

    def test_rejects_min_above_max(self):
        generator = PasswordGenerator(NGramBuilder().build_lines(WORDS, n=2))
        with pytest.raises(ValueError):
            generator.generate(1, min_length=9, max_length=5)


class TestBackOff:
    def test_unseen_context_backs_off_to_real_frequencies(self):
        model = NGramBuilder().build_lines("ab\nab\nab\ncb\n", n=2)
        generator = PasswordGenerator(model)

        # "zz" never occurred, nor did "z": falls back to character counts
        distribution = generator._distribution("zz", allow_end=False)
        assert distribution == {"a": 3, "b": 4, "c": 1}

    def test_backs_off_one_level_before_giving_up_on_context(self):
        model = NGramBuilder().build("xab xcb yab", n=2)
        generator = PasswordGenerator(model)
        # "qa" is unseen, but contexts ending in "a" were always followed by "b"
        assert generator._distribution("qa", allow_end=False) == {"b": 2}

    def test_stream_mode_still_gives_exact_lengths(self):
        generator = PasswordGenerator(NGramBuilder().build(WORDS.replace("\n", " "), n=3))
        assert {len(c) for c in generator.generate(50, 10)} == {10}


class TestWeighting:
    @staticmethod
    def _start_shares(model):
        starts = model[START * 2]
        total = sum(starts.values())
        return {char: weight / total for char, weight in starts.items()}

    def test_weights_are_shares_whatever_the_corpus_sizes(self):
        manager = MultiCorpusManager()
        manager.add_corpus_text("small", "ab\n")
        manager.add_corpus_text("large", "cd\n" * 100)

        shares = self._start_shares(manager.build_model(n=2))

        assert shares["a"] == pytest.approx(0.5)
        assert shares["c"] == pytest.approx(0.5)

    def test_small_weights_are_not_rounded_together(self):
        manager = MultiCorpusManager()
        manager.add_corpus_text("a", "ab\n", weight=0.04)
        manager.add_corpus_text("c", "cd\n", weight=0.06)
        manager.add_corpus_text("e", "ef\n", weight=0.90)

        shares = self._start_shares(manager.build_model(n=2))

        assert shares["a"] == pytest.approx(0.04)
        assert shares["c"] == pytest.approx(0.06)
        assert shares["e"] == pytest.approx(0.90)


class TestCliLength:
    def test_min_length_above_the_old_fixed_length_still_yields_results(self, tmp_path):
        corpus = tmp_path / "words.txt"
        corpus.write_text(WORDS * 5)
        output = tmp_path / "out.txt"

        result = CliRunner().invoke(main, [
            "generate", "--corpus", str(corpus), "--count", "30", "--min-length", "14",
            "--random-seed", "1", "--output", str(output),
        ])

        assert result.exit_code == 0, result.output
        lines = output.read_text().splitlines()
        assert len(lines) == 30
        assert all(len(line) >= 14 for line in lines)
