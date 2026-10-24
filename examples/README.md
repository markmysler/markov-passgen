# Markov PassGen Examples

Small sample corpora for trying the tool out. Run the commands below from the repository root.

## Sample corpora

| File | Contents | Size |
|---|---|---|
| `common_passwords.txt` | Common passwords from public breach lists | ~50 entries |
| `english_words.txt` | Common English words | ~1,600 words |
| `usernames.txt` | Technical and role-based usernames | ~60 entries |

They're tiny on purpose; real corpora give more varied output.

## CLI

Single corpus:

```bash
markov-passgen generate --corpus examples/common_passwords.txt --count 20
```

Several corpora, each weighted by its share of the model:

```bash
markov-passgen generate \
    --corpus-list examples/common_passwords.txt \
    --corpus-list examples/english_words.txt \
    --corpus-list examples/usernames.txt \
    --corpus-weights "0.5,0.3,0.2" \
    --count 50 \
    --min-length 8 \
    --max-length 14
```

With filters:

```bash
markov-passgen generate \
    --corpus examples/english_words.txt \
    --ngram-size 3 \
    --count 100 \
    --min-length 10 \
    --require-digits \
    --leet-speak 0.5 \
    --min-markov-bits 15 \
    --output wordlist.txt
```

Plots (needs `pip install "markov-passgen[viz]"`):

```bash
markov-passgen visualize-corpus --corpus examples/common_passwords.txt --ngram-freq ngram_analysis.png --char-dist char_analysis.png --top-n 20
markov-passgen visualize-multi-corpus --corpus-list examples/common_passwords.txt --corpus-list examples/english_words.txt --corpus-list examples/usernames.txt --corpus-weights "0.5,0.3,0.2" --output corpus_comparison.png
```

## Python

```python
from markov_passgen.core import CorpusLoader, MultiCorpusManager, NGramBuilder, PasswordGenerator

text = CorpusLoader().load_from_file("examples/common_passwords.txt")
generator = PasswordGenerator(NGramBuilder().build_lines(text, n=3))
print(generator.generate(count=10, min_length=6, max_length=12))

manager = MultiCorpusManager()
manager.add_corpus("passwords", "examples/common_passwords.txt", weight=0.5)
manager.add_corpus("words", "examples/english_words.txt", weight=0.3)
manager.add_corpus("users", "examples/usernames.txt", weight=0.2)
print(PasswordGenerator(manager.build_model(n=3)).generate(count=10))
```

More in the [tutorial](../docs/getting_started.md).

## Notes

These corpora and anything generated from them are for testing and teaching. Don't use generated candidates as real passwords.
