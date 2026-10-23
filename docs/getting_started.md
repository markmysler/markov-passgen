# Tutorial: Getting Started with Markov PassGen

This tutorial walks through the main features, from a first wordlist to combining several corpora. Every example runs as written from the repository root; the outputs shown come from real runs with the seeds given.

1. [Installation](#installation)
2. [Basic generation](#basic-generation)
3. [Choosing the n-gram size](#choosing-the-n-gram-size)
4. [Length](#length)
5. [Filters](#filters)
6. [Transformations](#transformations)
7. [Several corpora](#several-corpora)
8. [Scoring candidates](#scoring-candidates)
9. [Visualisation](#visualisation)

## Installation

```bash
pip install "markov-passgen[viz]"   # [viz] adds the plotting commands
```

Or from source:

```bash
git clone https://github.com/markmysler/markov-passgen.git
cd markov-passgen
pip install -e ".[dev]"
```

## Basic generation

### CLI

```bash
markov-passgen generate --corpus examples/common_passwords.txt --count 10 --output candidates.txt
```

### Python

```python
from markov_passgen.core import CorpusLoader, NGramBuilder, PasswordGenerator

text = CorpusLoader().load_from_file("examples/common_passwords.txt")
model = NGramBuilder().build_lines(text, n=3)   # each line is one entry

generator = PasswordGenerator(model)
generator.set_random_seed(42)
print(generator.generate(count=8))
```

```text
['sunshine', 'password1', 'princess', 'cheese', 'iloveyou', 'password1', 'stang', 'zxcvbnm']
```

The example list has only about 50 entries, so a 3-gram model mostly walks back along entries it has seen. Bigger corpora give more new combinations.

## Choosing the n-gram size

The model predicts each character from the previous *n* characters. Small *n* gives more variety and less realism; large *n* sticks closer to the corpus.

```python
from markov_passgen.core import CorpusLoader, NGramBuilder, PasswordGenerator

words = CorpusLoader().load_from_file("examples/english_words.txt")
for n in [2, 3, 4, 5]:
    generator = PasswordGenerator(NGramBuilder().build_lines(words, n=n))
    generator.set_random_seed(42)
    print(n, generator.generate(count=4, min_length=8, max_length=12))
```

```text
2 ['sancyessing', 'chourimaring', 'weraintabore', 'tougenter']
3 ['saladerly', 'leaguest', 'atterror', 'tournetwo']
4 ['salaryle', 'challeyboard', 'sharenture', 'runningly']
5 ['salaryle', 'challenge', 'attention', 'stretchen']
```

At *n* = 5 some candidates are simply words from the list.

## Length

A model built with `build_lines` knows where entries end, so candidate lengths follow the corpus. You can bound them, or ask for an exact length:

```python
generator.generate(count=10, min_length=8, max_length=12)   # between 8 and 12
generator.generate(count=10, length=10)                     # exactly 10
```

CLI: `--min-length`, `--max-length`, `--length`.

`NGramBuilder().build(text, n)` instead reads the text as one continuous stream, which suits prose. Such a model has no entry ends, so every candidate has the requested length (12 by default). CLI: `--stream`.

## Filters

Filters keep the candidates that meet requirements:

```python
from markov_passgen.filters import CharacterFilter, FilterChain, LengthFilter

chain = FilterChain()
chain.add_filter(LengthFilter(min_length=8, max_length=16))
chain.add_filter(CharacterFilter(require_digits=True))

kept = chain.apply(generator.generate(count=500))
```

`CharacterFilter` also takes `require_uppercase`, `require_lowercase`, `require_special`, `must_include` and `must_not_include`.

On the command line, filters run on each batch and the CLI keeps generating until it has `--count` candidates that pass:

```bash
markov-passgen generate \
    --corpus examples/common_passwords.txt \
    --count 50 \
    --min-length 8 \
    --require-digits \
    --output with_digits.txt
```

## Transformations

```python
import random
from markov_passgen.transformers import (
    CaseVariationTransformer,
    LeetSpeakTransformer,
    SubstitutionTransformer,
    TransformerChain,
)

random.seed(42)
leet = LeetSpeakTransformer(intensity=0.5)
print([leet.transform(p) for p in ["password", "admin", "welcome"]])

alternating = CaseVariationTransformer(mode="alternating")
print([alternating.transform(p) for p in ["password", "admin", "welcome"]])

dollars = SubstitutionTransformer({"s": "$"})
print(dollars.transform("bass"))

chain = TransformerChain()
chain.add(LeetSpeakTransformer(intensity=0.3)).add(CaseVariationTransformer(mode="capitalize"))
print(chain.transform("welcome"))
```

```text
['pa55w0rd', 'admin', 'welc0m3']
['PaSsWoRd', 'AdMiN', 'WeLcOmE']
ba$$
```

(The last line is random.) `CaseVariationTransformer` modes are `random`, `alternating` and `capitalize`.

CLI: `--leet-speak 0.3` (intensity 0 to 1) and `--case-variation alternating`.

## Several corpora

```python
from markov_passgen.core import MultiCorpusManager, PasswordGenerator

manager = MultiCorpusManager()
manager.add_corpus("passwords", "examples/common_passwords.txt", weight=0.5)
manager.add_corpus("words", "examples/english_words.txt", weight=0.3)
manager.add_corpus("users", "examples/usernames.txt", weight=0.2)

model = manager.build_model(n=3)
candidates = PasswordGenerator(model).generate(count=20)

for name, stats in manager.get_corpus_stats().items():
    print(f"{name}: {stats['char_count']} chars, {stats['word_count']} words, weight {stats['weight']}")
```

A weight is the corpus's share of the merged model, whatever its size: the 50-line password list gets half the model even though the word list is about 30 times larger.

CLI:

```bash
markov-passgen generate \
    --corpus-list examples/common_passwords.txt \
    --corpus-list examples/english_words.txt \
    --corpus-list examples/usernames.txt \
    --corpus-weights "0.5,0.3,0.2" \
    --count 50 \
    --output mixed.txt
```

## Scoring candidates

`EntropyCalculator` offers three different numbers:

| Method | Meaning |
|---|---|
| `calculate_markov_bits(p, model)` | Total bits, -log2 of the candidate's probability under the model. How surprising the candidate is to the model: higher is less predictable. |
| `calculate_markov_entropy(p, model)` | The same per character (average bits per transition), typically 1 to 4. |
| `calculate_shannon_entropy(p)` | How evenly the string uses its own characters, bounded by log2(length). It doesn't measure guessability. |

```python
from markov_passgen.core import EntropyCalculator

calc = EntropyCalculator()
for candidate in candidates[:5]:
    print(candidate, round(calc.calculate_markov_bits(candidate, model), 1))
```

Typical values depend on the corpus. With 3-grams, candidates from the small password list mostly score 5 to 7 bits, and candidates from the word list mostly 10 to 20. On the command line, `--min-markov-bits 15` keeps only the more surprising ones:

```bash
markov-passgen generate --corpus examples/english_words.txt --ngram-size 3 --min-markov-bits 15 --count 20 --output unusual.txt
```

## Visualisation

Needs the `[viz]` extra.

```python
from markov_passgen.core import EntropyCalculator
from markov_passgen.visualization import NGramVisualizer

viz = NGramVisualizer()
viz.plot_ngram_frequencies(model, top_n=20, output_path="ngram_frequencies.png")
viz.plot_length_distribution(candidates, bins=20, output_path="length_distribution.png")
viz.plot_entropy_distribution(candidates, EntropyCalculator(), bins=30, output_path="entropy_distribution.png")
viz.plot_character_distribution(words, top_n=30, output_path="character_frequencies.png")
viz.plot_corpus_comparison(manager.get_corpus_stats(), output_path="corpus_comparison.png")
NGramVisualizer.close_all()
```

CLI:

```bash
markov-passgen visualize-corpus --corpus examples/common_passwords.txt --ngram-freq ngrams.png --char-dist chars.png --top-n 20
markov-passgen visualize-passwords --wordlist mixed.txt --entropy-dist entropy.png --length-dist length.png --bins 30
markov-passgen visualize-multi-corpus --corpus-list examples/common_passwords.txt --corpus-list examples/english_words.txt --output comparison.png
```

## Tips

- **Start with *n* = 3.** It balances novelty and realism; *n* = 5 often reproduces corpus entries.
- **Use bigger corpora** for more varied output; the bundled examples are tiny.
- **Strict filters cost attempts.** The CLI gives up after 50 batches and says how many candidates it found.

## Responsible use

Generated candidates are for research, teaching and authorized testing. Don't use them as real passwords: they're predictable by design.

See also [Architecture](architecture.md).
