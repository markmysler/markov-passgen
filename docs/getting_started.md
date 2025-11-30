# Tutorial: Getting Started with Markov PassGen

This tutorial will walk you through the basic features of Markov PassGen, from simple password generation to advanced multi-corpus analysis.

## Table of Contents

1. [Installation](#installation)
2. [Basic Password Generation](#basic-password-generation)
3. [Understanding N-Grams](#understanding-n-grams)
4. [Applying Filters](#applying-filters)
5. [Using Transformations](#using-transformations)
6. [Multi-Corpus Generation](#multi-corpus-generation)
7. [Visualization and Analysis](#visualization-and-analysis)

## Installation

First, install Markov PassGen:

```bash
pip install markov-passgen
```

Or install from source for development:

```bash
git clone https://github.com/yourusername/markov-passgen.git
cd markov-passgen
pip install -e .
```

## Basic Password Generation

### Using the CLI

The simplest way to generate passwords is using the command-line interface:

```bash
markov-passgen generate --corpus examples/common_passwords.txt --count 10
```

This will generate 10 passwords based on patterns learned from the corpus file.

### Using the Python API

For more control, use the Python API:

```python
from markov_passgen.core import CorpusLoader, NGramBuilder, PasswordGenerator

# Step 1: Load your corpus
loader = CorpusLoader("examples/common_passwords.txt")
text = loader.load()

# Step 2: Build the Markov model
builder = NGramBuilder(ngram_size=3)
model = builder.build_model(text)

# Step 3: Generate passwords
generator = PasswordGenerator(model, min_length=8, max_length=16)
passwords = generator.generate(count=10)

# Step 4: Display results
for password in passwords:
    print(password)
```

**Output:**
```
passw0rd
letmein123
dragonfly
iloveyou1
master123
sunshine99
ashley2023
welcome!
football77
rainbowcat
```

## Understanding N-Grams

N-grams are sequences of N consecutive characters. The n-gram size determines how much context the model uses:

- **n=2 (bigrams)**: Less realistic, more random
- **n=3 (trigrams)**: Good balance (default)
- **n=4 (4-grams)**: More realistic patterns
- **n=5 (5-grams)**: Very close to source text

### Example: Different N-Gram Sizes

```python
from markov_passgen.core import CorpusLoader, NGramBuilder, PasswordGenerator

loader = CorpusLoader("examples/english_words.txt")
text = loader.load()

# Compare different n-gram sizes
for n in [2, 3, 4, 5]:
    print(f"\n=== N-Gram Size: {n} ===")
    builder = NGramBuilder(ngram_size=n)
    model = builder.build_model(text)
    generator = PasswordGenerator(model, min_length=10, max_length=12)
    passwords = generator.generate(count=3)
    for pwd in passwords:
        print(pwd)
```

**Output:**
```
=== N-Gram Size: 2 ===
relpingarl
thndbywate
morystalid

=== N-Gram Size: 3 ===
government
educational
restaurant

=== N-Gram Size: 4 ===
relationship
understanding
characteristic

=== N-Gram Size: 5 ===
international
responsibility
revolutionary
```

## Applying Filters

Filters ensure generated passwords meet specific requirements.

### Length Filters

```python
from markov_passgen.filters import LengthFilter

# Create a length filter
length_filter = LengthFilter(min_length=12, max_length=20)

# Use with generator
generator = PasswordGenerator(model, min_length=12, max_length=20)
passwords = generator.generate_filtered(count=10, filter_chain=length_filter)
```

### Character Set Filters

```python
from markov_passgen.filters import CharacterSetFilter

# Require specific character types
char_filter = CharacterSetFilter(
    require_digit=True,
    require_uppercase=True,
    require_lowercase=True,
    require_special=True
)

passwords = generator.generate_filtered(count=10, filter_chain=char_filter)
```

### Entropy Filters

```python
from markov_passgen.filters import EntropyFilter
from markov_passgen.core import EntropyCalculator

# Require minimum entropy
entropy_calc = EntropyCalculator()
entropy_filter = EntropyFilter(min_entropy=50.0, entropy_calculator=entropy_calc)

passwords = generator.generate_filtered(count=10, filter_chain=entropy_filter)
```

### Combining Filters

```python
from markov_passgen.filters import FilterChain

# Chain multiple filters
filters = FilterChain([
    LengthFilter(min_length=12, max_length=20),
    CharacterSetFilter(require_digit=True, require_special=True),
    EntropyFilter(min_entropy=50.0, entropy_calculator=entropy_calc)
])

passwords = generator.generate_filtered(count=10, filter_chain=filters)
```

### CLI Filters

Apply filters using the command-line:

```bash
markov-passgen generate \
    --corpus examples/english_words.txt \
    --count 50 \
    --min-length 12 \
    --max-length 16 \
    --require-digit \
    --require-special \
    --min-entropy 50 \
    --output secure_passwords.txt
```

## Using Transformations

Transformations modify generated passwords to add variety and complexity.

### Leetspeak Transformation

```python
from markov_passgen.transformers import LeetSpeakTransformer

leet = LeetSpeakTransformer(probability=0.5)

passwords = ["password", "admin", "welcome"]
for pwd in passwords:
    transformed = leet.transform(pwd)
    print(f"{pwd} -> {transformed}")
```

**Output:**
```
password -> p@ssw0rd
admin -> @dm1n
welcome -> w3lc0m3
```

### Case Variation

```python
from markov_passgen.transformers import CaseVariationTransformer

case_var = CaseVariationTransformer(variation_type="alternating")

passwords = ["password", "admin", "welcome"]
for pwd in passwords:
    transformed = case_var.transform(pwd)
    print(f"{pwd} -> {transformed}")
```

**Output:**
```
password -> PaSsWoRd
admin -> AdMiN
welcome -> WeLcOmE
```

### Custom Substitutions

```python
from markov_passgen.transformers import SubstitutionTransformer

sub = SubstitutionTransformer()
sub.add_rule("a", ["@", "4"])
sub.add_rule("o", ["0"])
sub.add_rule("e", ["3"])
sub.add_rule("i", ["1", "!"])

password = "password"
transformed = sub.transform(password)
print(f"{password} -> {transformed}")
```

**Output:**
```
password -> p@ssw0rd
```

### Transformation Chains

```python
from markov_passgen.transformers import TransformerChain

# Combine multiple transformers
chain = TransformerChain([
    LeetSpeakTransformer(probability=0.3),
    CaseVariationTransformer(variation_type="random"),
    SubstitutionTransformer()
])

password = "welcome"
transformed = chain.transform(password)
print(f"{password} -> {transformed}")
```

### CLI Transformations

```bash
markov-passgen generate \
    --corpus examples/english_words.txt \
    --count 20 \
    --transform leetspeak \
    --output transformed.txt
```

## Multi-Corpus Generation

Combine multiple text sources for more diverse passwords.

### Python API

```python
from markov_passgen.core import MultiCorpusManager, PasswordGenerator

# Create manager
manager = MultiCorpusManager(ngram_size=3)

# Add corpora with weights
manager.add_corpus("examples/common_passwords.txt", weight=0.5)
manager.add_corpus("examples/english_words.txt", weight=0.3)
manager.add_corpus("examples/usernames.txt", weight=0.2)

# Build merged model
merged_model = manager.build_merged_model()

# Generate passwords
generator = PasswordGenerator(merged_model, min_length=10, max_length=16)
passwords = generator.generate(count=20)

for pwd in passwords:
    print(pwd)
```

### Corpus Statistics

```python
# Get statistics about each corpus
stats = manager.get_corpus_stats()

for stat in stats:
    print(f"\nCorpus: {stat['name']}")
    print(f"  Characters: {stat['char_count']}")
    print(f"  Words: {stat['word_count']}")
    print(f"  Unique characters: {stat['unique_chars']}")
    print(f"  Weight: {stat['weight']}")
```

### CLI Multi-Corpus

```bash
markov-passgen generate \
    --corpus-list examples/common_passwords.txt \
    --corpus-list examples/english_words.txt \
    --corpus-list examples/usernames.txt \
    --corpus-weights "0.5,0.3,0.2" \
    --count 50 \
    --min-length 12 \
    --output multi_corpus_passwords.txt
```

## Visualization and Analysis

Visualize password characteristics and corpus properties.

### N-Gram Frequency Analysis

```python
from markov_passgen.visualization import NGramVisualizer
from markov_passgen.core import CorpusLoader, NGramBuilder

# Load and build model
loader = CorpusLoader("examples/common_passwords.txt")
text = loader.load()
builder = NGramBuilder(ngram_size=3)
model = builder.build_model(text)

# Create visualizer
viz = NGramVisualizer()

# Plot top 20 n-grams
viz.plot_ngram_frequencies(
    model,
    top_n=20,
    output_path="ngram_frequencies.png"
)
```

### Entropy Distribution

```python
from markov_passgen.core import EntropyCalculator

# Generate passwords
generator = PasswordGenerator(model, min_length=8, max_length=16)
passwords = generator.generate(count=200)

# Calculate and visualize entropy
entropy_calc = EntropyCalculator()
viz.plot_entropy_distribution(
    passwords,
    entropy_calc,
    bins=30,
    output_path="entropy_distribution.png"
)
```

### Length Distribution

```python
# Visualize password lengths
viz.plot_length_distribution(
    passwords,
    bins=20,
    output_path="length_distribution.png"
)
```

### Character Frequency

```python
# Analyze character usage
viz.plot_character_distribution(
    text,
    top_n=30,
    output_path="character_frequencies.png"
)
```

### Corpus Comparison

```python
# Compare multiple corpora
from markov_passgen.core import MultiCorpusManager

manager = MultiCorpusManager(ngram_size=3)
manager.add_corpus("examples/common_passwords.txt", weight=0.5)
manager.add_corpus("examples/english_words.txt", weight=0.3)
manager.add_corpus("examples/usernames.txt", weight=0.2)

stats = manager.get_corpus_stats()

viz.plot_corpus_comparison(
    stats,
    output_path="corpus_comparison.png"
)
```

### CLI Visualization

Visualize corpus:
```bash
markov-passgen visualize-corpus \
    --corpus examples/common_passwords.txt \
    --ngram-freq ngram_analysis.png \
    --char-dist char_analysis.png \
    --top-n 20
```

Visualize passwords:
```bash
markov-passgen visualize-passwords \
    --wordlist generated_passwords.txt \
    --entropy-dist entropy.png \
    --length-dist length.png \
    --bins 30
```

Compare corpora:
```bash
markov-passgen visualize-multi-corpus \
    --corpus-list examples/common_passwords.txt \
    --corpus-list examples/english_words.txt \
    --corpus-list examples/usernames.txt \
    --corpus-weights "0.5,0.3,0.2" \
    --output comparison.png
```

## Next Steps

- Explore [Advanced Techniques](advanced.md) for complex use cases
- Read the [API Reference](../api/) for detailed documentation
- Check out [Architecture Overview](architecture.md) to understand the design
- See [Contributing Guidelines](../../CONTRIBUTING.md) to contribute

## Tips

1. **Start with n=3**: Trigrams offer the best balance between randomness and realism
2. **Use multiple corpora**: Mixing sources creates more diverse passwords
3. **Apply filters carefully**: Too many filters can slow generation
4. **Visualize first**: Analyze your corpus before generating large batches
5. **Test incrementally**: Start with small counts, then scale up

## Common Pitfalls

- **Small corpora**: Need at least 100+ words for reasonable results
- **Too high n-gram**: n=5 often just reproduces source text
- **Over-filtering**: Strict filters may cause slow generation
- **Ignoring entropy**: Low entropy passwords are weak

## Security Note

Remember: Generated passwords are for **research and testing only**. Never use them for real systems or accounts.
