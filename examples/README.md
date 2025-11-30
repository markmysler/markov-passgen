# Markov PassGen Examples

This directory contains sample corpus files for testing and demonstration purposes.

## Sample Corpora

### common_passwords.txt
A collection of common passwords frequently found in password breaches. Useful for:
- Generating realistic password patterns
- Testing password strength validators
- Security research on password patterns

**Size**: ~50 common passwords

### english_words.txt
Common English words covering various categories. Useful for:
- Generating pronounceable password candidates
- Creating word-based password patterns
- Text analysis and visualization

**Size**: ~1000 common English words

### usernames.txt
Technical usernames and role-based identifiers. Useful for:
- Generating username-based password patterns
- Multi-corpus mixing experiments
- Role-based password generation

**Size**: ~60 common usernames

## Usage Examples

### Basic Generation

Generate passwords from a single corpus:

```bash
markov-passgen generate --corpus common_passwords.txt --count 20
```

### Multi-Corpus Generation

Combine multiple corpora with weights:

```bash
markov-passgen generate \
    --corpus-list common_passwords.txt \
    --corpus-list english_words.txt \
    --corpus-list usernames.txt \
    --corpus-weights "0.5,0.3,0.2" \
    --count 50 \
    --min-length 12 \
    --max-length 16
```

### With Filters

Apply filters to generated passwords:

```bash
markov-passgen generate \
    --corpus english_words.txt \
    --count 100 \
    --min-length 10 \
    --require-digit \
    --require-special \
    --min-entropy 40 \
    --output wordlist.txt
```

### Visualization

Analyze corpus characteristics:

```bash
markov-passgen visualize-corpus \
    --corpus common_passwords.txt \
    --ngram-freq ngram_analysis.png \
    --char-dist char_analysis.png \
    --top-n 20
```

Compare multiple corpora:

```bash
markov-passgen visualize-multi-corpus \
    --corpus-list common_passwords.txt \
    --corpus-list english_words.txt \
    --corpus-list usernames.txt \
    --corpus-weights "0.5,0.3,0.2" \
    --output corpus_comparison.png
```

## Python API Examples

### Load and Generate

```python
from markov_passgen.core import CorpusLoader, NGramBuilder, PasswordGenerator

# Load corpus
loader = CorpusLoader("examples/common_passwords.txt")
text = loader.load()

# Build model
builder = NGramBuilder(ngram_size=3)
model = builder.build_model(text)

# Generate passwords
generator = PasswordGenerator(model, min_length=8, max_length=16)
passwords = generator.generate(count=10)
```

### Multi-Corpus

```python
from markov_passgen.core import MultiCorpusManager, PasswordGenerator

# Create multi-corpus manager
manager = MultiCorpusManager(ngram_size=3)
manager.add_corpus("examples/common_passwords.txt", weight=0.5)
manager.add_corpus("examples/english_words.txt", weight=0.3)
manager.add_corpus("examples/usernames.txt", weight=0.2)

# Build merged model
model = manager.build_merged_model()

# Generate passwords
generator = PasswordGenerator(model, min_length=10, max_length=16)
passwords = generator.generate(count=50)
```

## Notes

- These corpora are for **testing and educational purposes only**
- Do not use generated passwords for real systems
- Always add your own corpus files for production use cases
- Larger corpora generally produce more diverse results
