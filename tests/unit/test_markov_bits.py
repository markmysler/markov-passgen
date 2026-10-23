"""Tests for EntropyCalculator.calculate_markov_bits"""

import math

import pytest

from markov_passgen.core.entropy_calculator import EntropyCalculator
from markov_passgen.core.ngram_builder import NGramBuilder

calc = EntropyCalculator()


def test_certain_string_costs_zero_bits():
    model = NGramBuilder().build_lines("abc\nabc\n", n=2)
    assert calc.calculate_markov_bits("abc", model) == pytest.approx(0.0)


def test_one_binary_choice_costs_one_bit():
    # Start is "a" or "b" with equal counts; everything after is certain
    model = NGramBuilder().build_lines("ax\nbx\n", n=2)
    assert calc.calculate_markov_bits("ax", model) == pytest.approx(1.0)


def test_rarer_strings_score_higher():
    model = NGramBuilder().build_lines("pass\n" * 9 + "past\n", n=2)
    assert calc.calculate_markov_bits("past", model) > calc.calculate_markov_bits("pass", model)


def test_includes_ending_where_the_string_ends():
    # "ab" usually continues to "abc"; stopping at "ab" is the unlikely branch
    model = NGramBuilder().build_lines("abc\n" * 3 + "ab\n", n=2)
    assert calc.calculate_markov_bits("ab", model) == pytest.approx(-math.log2(1 / 4))


def test_unseen_characters_get_a_finite_score():
    model = NGramBuilder().build_lines("abc\n", n=2)
    assert math.isfinite(calc.calculate_markov_bits("xyz", model))


def test_stream_model():
    model = NGramBuilder().build("ababab", n=2)
    assert calc.calculate_markov_bits("abab", model) == pytest.approx(0.0)


def test_rejects_empty_input():
    model = NGramBuilder().build_lines("abc\n", n=2)
    with pytest.raises(ValueError):
        calc.calculate_markov_bits("", model)
    with pytest.raises(ValueError):
        calc.calculate_markov_bits("abc", {})
