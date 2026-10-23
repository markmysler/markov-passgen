# Markov PassGen

[![CI](https://github.com/markmysler/markov-passgen/actions/workflows/ci.yml/badge.svg)](https://github.com/markmysler/markov-passgen/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/markov-passgen.svg)](https://pypi.org/project/markov-passgen/)
[![Python versions](https://img.shields.io/pypi/pyversions/markov-passgen.svg)](https://pypi.org/project/markov-passgen/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Generate human-like password candidates with Markov chains. Train a character n-gram model on a text corpus (leaked-password lists, dictionaries, usernames) and sample new candidates that follow the same patterns: useful for password-strength research, wordlists for authorized penetration tests, and teaching how predictable "random" passwords are.

## Features

- **Markov chain generation** from character n-gram models (n = 2–5)
- **Multiple corpora** combined with configurable weights
- **Filters** for length and required character classes (digits, upper, lower, special)
- **Corpus cleaning**: lowercase, strip punctuation or digits, normalise whitespace
- **Transformations**: leetspeak and case variations
- **Entropy scores**: Shannon entropy of a string and a Markov score against the model
- **Visualisation**: n-gram, character, entropy, length and corpus-comparison plots
- **Reproducible runs** with a random seed

## Installation

```bash
pip install markov-passgen
```

The plotting commands need matplotlib, seaborn and numpy, which are an optional extra:

```bash
pip install "markov-passgen[viz]"
```

From source:

```bash
git clone https://github.com/markmysler/markov-passgen.git
cd markov-passgen
pip install -e ".[dev]"
```

## Quick start

### Command line

```bash
markov-passgen generate --corpus examples/english_words.txt --ngram-size 3 --count 10 --random-seed 7 --output candidates.txt
```

Require character classes and apply leetspeak:

```bash
markov-passgen generate \
    --corpus examples/common_passwords.txt \
    --count 50 \
    --length 12 \
    --require-digits \
    --leet-speak 0.3 \
    --output wordlist.txt
```

Combine several corpora with weights:

```bash
markov-passgen generate \
    --corpus-list examples/common_passwords.txt \
    --corpus-list examples/english_words.txt \
    --corpus-list examples/usernames.txt \
    --corpus-weights "0.5,0.3,0.2" \
    --count 100
```

Plot the length and entropy distribution of a wordlist:

```bash
markov-passgen visualize-passwords --wordlist wordlist.txt --entropy-dist entropy.png --length-dist length.png
```

### Python

```python
from markov_passgen.core import CorpusLoader, NGramBuilder, PasswordGenerator

text = CorpusLoader().load_from_file("examples/english_words.txt")
model = NGramBuilder().build(text, n=3)

generator = PasswordGenerator(model)
generator.set_random_seed(7)
for password in generator.generate(count=10, length=12):
    print(password)
```

## Usage examples

### Filtering

Filters are applied to a list of generated candidates:

```python
from markov_passgen.filters import CharacterFilter, FilterChain, LengthFilter

chain = FilterChain()
chain.add_filter(LengthFilter(min_length=10, max_length=16))
chain.add_filter(CharacterFilter(require_digits=True, require_lowercase=True))

candidates = generator.generate(count=500, length=12)
strong_enough = chain.apply(candidates)
```

### Cleaning the corpus

```python
from markov_passgen.core import CorpusLoader
from markov_passgen.transformers import TextCleaner

cleaner = TextCleaner(lowercase=True, remove_punctuation=True, normalize_whitespace=True)
text = CorpusLoader().load_from_file("examples/english_words.txt", cleaner=cleaner)
```

### Transforming candidates

```python
from markov_passgen.transformers import (
    CaseVariationTransformer,
    LeetSpeakTransformer,
    SubstitutionTransformer,
    TransformerChain,
)

leet = LeetSpeakTransformer(intensity=0.5)
print(leet.transform("password"))                          # e.g. p@ssw0rd

alternating = CaseVariationTransformer(mode="alternating")
print(alternating.transform("password"))                   # PaSsWoRd

chain = TransformerChain()
chain.add(LeetSpeakTransformer(intensity=0.3)).add(CaseVariationTransformer(mode="capitalize"))
print(chain.transform_batch(["password", "dragon"]))

sub = SubstitutionTransformer({"s": "$"})
print(sub.transform("bass"))                               # ba$$
```

### Multiple corpora

```python
from markov_passgen.core import MultiCorpusManager, NGramBuilder, PasswordGenerator

manager = MultiCorpusManager()
manager.add_corpus("passwords", "examples/common_passwords.txt", weight=0.5)
manager.add_corpus("words", "examples/english_words.txt", weight=0.3)
manager.add_corpus("users", "examples/usernames.txt", weight=0.2)

model = NGramBuilder().build(manager.get_merged_corpus(), n=3)
candidates = PasswordGenerator(model).generate(count=50, length=12)

for name, stats in manager.get_corpus_stats().items():
    print(f"{name}: {stats['char_count']} chars, weight={stats['weight']}")
```

### Entropy

```python
from markov_passgen.core import EntropyCalculator

calc = EntropyCalculator()
calc.calculate_shannon_entropy("password1")       # bits per character, from the string's own letters
calc.calculate_markov_entropy("password1", model) # average bits per character under the model
```

### Visualisation

```python
from markov_passgen.core import EntropyCalculator
from markov_passgen.visualization import NGramVisualizer

viz = NGramVisualizer()
viz.plot_ngram_frequencies(model, top_n=20, output_path="ngram_freq.png")
viz.plot_character_distribution(text, top_n=30, output_path="char_freq.png")
viz.plot_length_distribution(candidates, bins=20, output_path="length_dist.png")
viz.plot_entropy_distribution(candidates, EntropyCalculator(), bins=30, output_path="entropy_dist.png")
viz.plot_corpus_comparison(manager.get_corpus_stats(), output_path="corpus_comparison.png")
NGramVisualizer.close_all()
```

Plots are saved in the format given by the file extension (PNG, JPG, SVG or PDF).

## CLI reference

Run `markov-passgen <command> --help` for the full list.

### `generate`

| Option | Meaning |
|---|---|
| `--corpus PATH` | Corpus file |
| `--corpus-list PATH` | Corpus file for multi-corpus mode (repeat for each file) |
| `--corpus-weights "W1,W2,..."` | Comma-separated weights, one per `--corpus-list` |
| `--ngram-size 2-5` | N-gram size (default 2) |
| `--count N` | Number of candidates (default 100) |
| `--length N` | Length of each candidate (default 12) |
| `--min-length N`, `--max-length N` | Keep only candidates in this length range |
| `--require-digits`, `--require-uppercase`, `--require-lowercase`, `--require-special` | Keep only candidates containing that character class |
| `--min-entropy X` | Keep only candidates whose Markov score (average bits per character) is at least X |
| `--seed-word TEXT` | Start every candidate with this text |
| `--random-seed N` | Seed for reproducible output |
| `--lowercase`, `--remove-punctuation`, `--remove-digits`, `--normalize-whitespace` | Clean the corpus first |
| `--leet-speak 0.0-1.0` | Leetspeak intensity |
| `--case-variation random\|alternating\|capitalize` | Case variation |
| `--output PATH` | Output file (default `wordlist.txt`) |

### `visualize-corpus`

`--corpus PATH` (required), `--ngram-size`, `--ngram-freq PATH`, `--char-dist PATH`, `--top-n N`

### `visualize-passwords`

`--wordlist PATH` (required), `--entropy-dist PATH`, `--length-dist PATH`, `--bins N`

### `visualize-multi-corpus`

`--corpus-list PATH` (repeat, required), `--corpus-weights "W1,W2,..."`, `--output PATH` (required)

## Development

```bash
pip install -e ".[dev]"
pytest
```

The tests are split into `tests/unit`, `tests/integration` and `tests/e2e`. The end-to-end tests call the installed `markov-passgen` command, so install the package first.

More detail: [Getting started](docs/getting_started.md) and [Architecture](docs/architecture.md).

## Responsible use

This tool is for security research, education and **authorized** testing: password-strength analysis, wordlists for penetration tests you have permission to run, and research. Don't use generated candidates as real passwords (they're predictable by design), and don't use them against systems you aren't authorized to test.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT; see [LICENSE](LICENSE).
