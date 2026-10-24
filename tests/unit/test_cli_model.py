"""Tests for train / generate --model"""

import json

from click.testing import CliRunner

from markov_passgen.cli import main
from markov_passgen.core.ngram_builder import START

WORDS = "\n".join(["dragon", "monkey", "shadow", "master", "sunshine", "princess",
                   "football", "baseball", "welcome", "letmein", "superman", "batman"] * 3)


def test_train_then_generate_from_the_saved_model(tmp_path):
    corpus = tmp_path / "words.txt"
    corpus.write_text(WORDS)
    model_path = tmp_path / "model.json"
    out = tmp_path / "out.txt"
    runner = CliRunner()

    trained = runner.invoke(main, ["train", "--corpus", str(corpus), "--ngram-size", "3",
                                   "--output", str(model_path)])
    assert trained.exit_code == 0, trained.output
    model = json.loads(model_path.read_text(encoding="utf-8"))
    assert START * 3 in model  # a line-mode model survives the JSON round trip

    generated = runner.invoke(main, ["generate", "--model", str(model_path), "--count", "20",
                                     "--min-length", "5", "--random-seed", "1", "--output", str(out)])
    assert generated.exit_code == 0, generated.output
    lines = out.read_text().splitlines()
    assert len(lines) == 20
    assert all(len(line) >= 5 for line in lines)


def test_generate_rejects_model_and_corpus_together(tmp_path):
    corpus = tmp_path / "words.txt"
    corpus.write_text(WORDS)
    model_path = tmp_path / "model.json"
    runner = CliRunner()
    runner.invoke(main, ["train", "--corpus", str(corpus), "--output", str(model_path)])

    result = runner.invoke(main, ["generate", "--model", str(model_path), "--corpus", str(corpus),
                                  "--output", str(tmp_path / "out.txt")])

    assert result.exit_code != 0
    assert "either --model or a corpus" in result.output


def test_train_needs_a_corpus(tmp_path):
    result = CliRunner().invoke(main, ["train", "--output", str(tmp_path / "model.json")])
    assert result.exit_code != 0
