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
markov-passgen generate --corpus examples/english_words.txt --ngram-size 3 --count 12 --random-seed 7 --output candidates.txt
```

```text
occasist  pager  mist  watchemsell  ract  pink  tomachink  pret  stroke  slow  scies  neting
```

Each line of the corpus is one training entry, so candidates start and end the way entries do and their lengths follow the data. Bound the length, require character classes and mix in a second corpus:

```bash
markov-passgen generate \
    --corpus-list examples/common_passwords.txt \
    --corpus-list examples/english_words.txt \
    --corpus-weights "0.6,0.4" \
    --ngram-size 3 \
    --min-length 8 --max-length 14 \
    --require-digits \
    --count 8 --random-seed 7
```

```text
qwerty1234567  password123  1234567p  password123456  qwerty1234567  surerty123  password1  flowerty123
```

Train once on a big corpus and reuse the model:

```bash
markov-passgen train --corpus big_wordlist.txt --ngram-size 4 --output model.json
markov-passgen generate --model model.json --count 1000 --output candidates.txt
```

Apply leetspeak to fixed-length candidates:

```bash
markov-passgen generate --corpus examples/common_passwords.txt --count 50 --length 12 --leet-speak 0.3 --output wordlist.txt
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
model = NGramBuilder().build_lines(text, n=3)  # one entry per line

generator = PasswordGenerator(model)
generator.set_random_seed(7)
for password in generator.generate(count=10, min_length=6, max_length=12):
    print(password)
```

`generate(count, length=12)` gives an exact length instead. `NGramBuilder().build(text, n)` reads the text as one continuous stream (for prose rather than lists); such a model has no entry ends, so it always needs a length.

## Usage examples

### Filtering

Filters are applied to a list of generated candidates:

```python
from markov_passgen.filters import CharacterFilter, FilterChain, LengthFilter

chain = FilterChain()
chain.add_filter(LengthFilter(min_length=10, max_length=16))
chain.add_filter(CharacterFilter(require_digits=True, require_lowercase=True))

candidates = generator.generate(count=500)
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
print(leet.transform("password"))                          # e.g. p455w0rd

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
from markov_passgen.core import MultiCorpusManager, PasswordGenerator

manager = MultiCorpusManager()
manager.add_corpus("passwords", "examples/common_passwords.txt", weight=0.5)
manager.add_corpus("words", "examples/english_words.txt", weight=0.3)
manager.add_corpus("users", "examples/usernames.txt", weight=0.2)

model = manager.build_model(n=3)
candidates = PasswordGenerator(model).generate(count=50)

for name, stats in manager.get_corpus_stats().items():
    print(f"{name}: {stats['char_count']} chars, weight={stats['weight']}")
```

A weight is the corpus's share of the merged model: here half of all transitions come from the password list, even though the word list is 30 times larger.

### Scoring candidates

```python
from markov_passgen.core import EntropyCalculator

calc = EntropyCalculator()
calc.calculate_markov_bits("password1", model)     # total bits: -log2 P(candidate) under the model
calc.calculate_markov_entropy("password1", model)  # the same per character (typically 1-4)
calc.calculate_shannon_entropy("password1")        # spread of the string's own letters
```

- **Markov bits** is the useful one: how surprising the whole candidate is to the model. Higher means less predictable. Typical values depend on the corpus; with 3-grams, candidates from the bundled word list mostly score 10–20 bits.
- **Markov entropy** is that score divided by the number of characters.
- **Shannon entropy** only measures how evenly a string uses its own characters. It's bounded by log2(length) (about 3.6 for 12 characters) and doesn't measure guessability.

None of these is the "bits of entropy" used for password strength, so a value like 40 isn't reachable for `--min-entropy`.

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
| `--model PATH` | Use a model saved by `train` instead of a corpus |
| `--corpus-list PATH` | Corpus file for multi-corpus mode (repeat for each file) |
| `--corpus-weights "W1,W2,..."` | Comma-separated weights, one per `--corpus-list`; each is that corpus's share of the model |
| `--ngram-size 2-5` | N-gram size (default 2) |
| `--count N` | Number of candidates (default 100) |
| `--min-length N`, `--max-length N` | Length range to generate in (default: whatever the corpus suggests, up to 64) |
| `--length N` | Exact length for every candidate |
| `--stream` | Read the corpus as one continuous text instead of one entry per line (for prose); candidates are then 12 characters unless `--length` is set |
| `--require-digits`, `--require-uppercase`, `--require-lowercase`, `--require-special` | Keep only candidates containing that character class |
| `--min-markov-bits X` | Keep only candidates whose total Markov bits (see *Scoring candidates*) is at least X |
| `--min-entropy X` | Keep only candidates whose Markov entropy (average bits per character, typically 1–4) is at least X |
| `--seed-word TEXT` | Start every candidate with this text |
| `--random-seed N` | Seed for reproducible output |
| `--lowercase`, `--remove-punctuation`, `--remove-digits`, `--normalize-whitespace` | Clean the corpus first |
| `--leet-speak 0.0-1.0` | Leetspeak intensity |
| `--case-variation random\|alternating\|capitalize` | Case variation |
| `--output PATH` | Output file (default `wordlist.txt`) |

### `train`

Builds the model and saves it as JSON. Takes the same corpus options as `generate` (`--corpus` or `--corpus-list` with `--corpus-weights`, `--ngram-size`, `--stream`, the cleaning flags), plus `--output PATH` (required).

### `visualize-corpus`

`--corpus PATH` (required), `--ngram-size`, `--ngram-freq PATH`, `--char-dist PATH`, `--top-n N`

### `visualize-passwords`

`--wordlist PATH` (required), `--entropy-dist PATH`, `--length-dist PATH`, `--bins N`

### `visualize-multi-corpus`

`--corpus-list PATH` (repeat, required), `--corpus-weights "W1,W2,..."`, `--output PATH` (required)

## How it works

- **Training.** Each corpus line is padded with start and end markers, and the model counts which character follows every *n*-character context. It learns how entries begin and end, and never learns a jump from the end of one line into the next.
- **Generating.** A candidate starts from the start context and samples one character at a time, weighted by the counts, until the model picks the end marker (never before `--min-length`, never past `--max-length`). When a context never occurred in the corpus, the generator backs off to the last *n*−1, *n*−2, … characters, down to plain character frequencies. So output stays faithful to the corpus instead of being padded with random characters.
- **Several corpora.** Each corpus gets its own model, and its counts are scaled so it makes up its weight's share of the merged model.
- **Filters** (character classes, entropy) run on generated candidates; the CLI keeps generating in batches until it has `--count` that pass.

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check src tests
mypy src
```

The tests are split into `tests/unit`, `tests/integration` and `tests/e2e`. The end-to-end tests call the installed `markov-passgen` command, so install the package first.

More detail: [Getting started](docs/getting_started.md) and [Architecture](docs/architecture.md).

## Responsible use

This tool is for security research, education and **authorized** testing: password-strength analysis, wordlists for penetration tests you have permission to run, and research. Don't use generated candidates as real passwords (they're predictable by design), and don't use them against systems you aren't authorized to test.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT; see [LICENSE](LICENSE).
