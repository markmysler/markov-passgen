# Markov PassGen Architecture

How the pieces fit together. For usage, see the [tutorial](getting_started.md).

## Overview

```
                    CLI (click): generate, visualize-*
                                  │
          ┌───────────────────────┼────────────────────────┐
          ▼                       ▼                        ▼
    CorpusLoader            MultiCorpusManager       TextCleaner
    (read, clean)           (several corpora,        (optional corpus
          │                  weighted merge)          cleaning)
          ▼                       │
    NGramBuilder ◄────────────────┘
    (build_lines / build)
          │  model: {context: {next_char: count}}
          ▼
    PasswordGenerator ──► candidates ──► EntropyCalculator (scores)
                                    ──► TransformerChain (leetspeak, case)
                                    ──► FilterChain (length, character classes)
                                    ──► NGramVisualizer (plots, [viz] extra)
```

Each class does one job, and the pieces meet at plain data: a model is a dict, and candidates are a list of strings.

## Core (`markov_passgen.core`)

### CorpusLoader

- `load_from_file(path, cleaner=None)` and `load_from_files(paths, cleaner=None)` read UTF-8 text and optionally clean it.
- `validate_corpus(text)` checks for at least 100 characters.
- `get_corpus_stats()` reports character, word and unique-character counts.

### NGramBuilder

The model maps each *n*-character context to counts of the character that followed it:

```python
{
    "pas": {"s": 10, "t": 3},   # "pas" was followed by "s" 10 times, "t" 3 times
    ...
}
```

- `build_lines(text, n)` (used by the CLI) treats each line as one entry, padded with a start marker (`\x02` × *n*) and an end marker (`\x03`). The model learns how entries begin and end, and never learns a jump from one line into the next.
- `build(text, n)` reads the text as one continuous stream, for prose. Such a model has no entry ends.
- `add_to_model(text)` extends a model the same way it was built.
- `save_model(path)` and `load_model(path)` write and read JSON.

### PasswordGenerator

`generate(count, length=None, seed=None, transformer=None, min_length=None, max_length=None)`

1. Start from the start context (line mode), or a random context (stream mode).
2. Look up what followed the last *n* characters and pick the next character, weighted by the counts.
3. In line mode, stop when the end marker is picked. It's never allowed before `min_length`, and generation stops at `max_length` (default 64). An exact `length` sets both. In stream mode, stop at `length` (default 12).
4. If a context never occurred in the corpus, back off to the last *n*−1, *n*−2, … characters, down to plain character frequencies. These lower-order tables are summed from the model once, on first use.

### MultiCorpusManager

Holds several corpora with weights. `build_model(n, per_line=True)` builds one model per corpus, then scales each so its total count equals its weight's share of the merged model. Weights mean shares regardless of corpus size, and nothing is copied. (`get_merged_corpus()` keeps the old repeat-the-text approximation for compatibility.)

### EntropyCalculator

| Method | Measures |
|---|---|
| `calculate_markov_bits(p, model)` | -log2 P(p) under the model, using the generator's back-off; includes the end marker in line mode. How surprising the whole candidate is. |
| `calculate_markov_entropy(p, model)` | Average bits per transition. |
| `calculate_shannon_entropy(p)` | Spread of the string's own characters; bounded by log2(length). |
| `estimate_crack_time(p)` | Brute-force time over the candidate's character classes. Ignores that Markov candidates are far more guessable than that. |

## Filters (`markov_passgen.filters`)

Every filter takes a list and returns the candidates that pass:

```python
class BaseFilter(ABC):
    @abstractmethod
    def filter(self, passwords: List[str]) -> List[str]: ...
```

- `LengthFilter(min_length, max_length)`
- `CharacterFilter(require_digits, require_uppercase, require_lowercase, require_special, must_include, must_not_include)`
- `FilterChain` applies its filters in order (`add_filter`, `apply`).

The CLI runs filters on each batch of candidates and keeps generating until it has enough, for up to 50 batches.

## Transformers (`markov_passgen.transformers`)

Corpus cleaning (text → text):

- **TextCleaner**: lowercase, remove punctuation, remove digits, normalise whitespace. Normalising keeps line breaks, because entries are lines.
- **CaseTransformer**: `lower`, `upper`, `title` or `capitalize`.
- **CharacterTransformer**: keep or drop letters, digits, spaces and punctuation.

Candidate transformations (`BasePasswordTransformer.transform(password) -> str`):

- **LeetSpeakTransformer(intensity)** replaces a→4, e→3, i→1, o→0, s→5, t→7, g→9 and b→8, each with probability `intensity`.
- **CaseVariationTransformer(mode)** uses one of `random`, `alternating` or `capitalize`.
- **SubstitutionTransformer(substitutions, probability)** applies a custom one-to-one map.
- **TransformerChain** applies transformers in order.

## Visualisation (`markov_passgen.visualization`)

`NGramVisualizer` draws n-gram frequencies, character frequencies, and the entropy and length distributions of a wordlist, plus a corpus comparison, with matplotlib and seaborn. These are the optional `[viz]` extra; without them, importing the module raises an error that says how to install it. The file extension picks the format (PNG, JPG, SVG or PDF).

## CLI (`markov_passgen.cli`)

The commands are `generate`, `visualize-corpus`, `visualize-passwords` and `visualize-multi-corpus`. Errors are printed as one line and the command exits with a non-zero status.

## Tests

- `tests/unit`: one file per component.
- `tests/integration`: pipelines (corpus → model → generator → filters/transformers), multi-corpus, visualisation.
- `tests/e2e`: the installed `markov-passgen` command, run as a subprocess.

CI runs them on Python 3.9–3.13 for every push and pull request, and releases are published only after they pass.

## Extending

New filters subclass `BaseFilter` and implement `filter(passwords)`; new candidate transformations subclass `BasePasswordTransformer` and implement `transform(password)`. Both drop straight into `FilterChain` and `TransformerChain`.

## Security notes

- Candidates are predictable by design: the point is to model how people pick passwords. Don't use them as real passwords.
- The tool is offline and stateless: it reads corpora, writes wordlists and plots, and nothing else.
- Use it for research, teaching and testing you're authorized to do.
