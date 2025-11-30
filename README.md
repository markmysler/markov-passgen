# Markov PassGen

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Coverage](https://img.shields.io/badge/coverage-82%25-green.svg)](htmlcov/index.html)

Generate human-like password candidates using Markov chain analysis. Build probabilistic models from text corpora to create realistic password patterns for security research, penetration testing, and password strength analysis.

## 🎯 Features

- **Markov Chain Generation**: Create passwords using n-gram probabilistic models (n=2-5)
- **Multi-Corpus Support**: Train models on multiple text corpora with configurable weights
- **Advanced Filtering**: Filter passwords by length, character sets, entropy, and custom patterns
- **Text Processing**: Clean and transform source text with case handling and character normalization
- **Password Transformations**: Apply leetspeak, case variations, and character substitutions
- **Entropy Analysis**: Calculate Shannon entropy and estimate password strength
- **Visualization**: Generate statistical plots and analyze password distributions
- **CLI Interface**: Powerful command-line tool with extensive options
- **High Performance**: Efficient n-gram building and generation with progress tracking

## 📦 Installation

### From PyPI (when published)

```bash
pip install markov-passgen
```

### From Source

```bash
git clone https://github.com/markmysler/markov-passgen.git
cd markov-passgen
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/markmysler/markov-passgen.git
cd markov-passgen
pip install -e ".[dev]"
```

## 🚀 Quick Start

### Basic Password Generation

```python
from markov_passgen.core import CorpusLoader, NGramBuilder, PasswordGenerator

# Load a text corpus
loader = CorpusLoader("path/to/corpus.txt")
text = loader.load()

# Build a Markov model
builder = NGramBuilder(ngram_size=3)
model = builder.build_model(text)

# Generate passwords
generator = PasswordGenerator(model, min_length=8, max_length=16)
passwords = generator.generate(count=10)

for password in passwords:
    print(password)
```

### Using the CLI

Generate 20 passwords from a corpus:

```bash
markov-passgen generate --corpus passwords.txt --count 20 --min-length 10 --max-length 16
```

Apply filters and transformations:

```bash
markov-passgen generate \
    --corpus passwords.txt \
    --count 50 \
    --min-length 12 \
    --require-digit \
    --require-special \
    --min-entropy 40 \
    --transform leetspeak \
    --output wordlist.txt
```

Use multiple corpora with weights:

```bash
markov-passgen generate \
    --corpus-list common_passwords.txt \
    --corpus-list english_words.txt \
    --corpus-list usernames.txt \
    --corpus-weights "0.5,0.3,0.2" \
    --count 100
```

Visualize password characteristics:

```bash
markov-passgen visualize-passwords \
    --wordlist generated.txt \
    --entropy-dist entropy.png \
    --length-dist length.png
```

## 📖 Usage Examples

### Advanced Filtering

```python
from markov_passgen.filters import (
    LengthFilter,
    CharacterSetFilter,
    EntropyFilter,
    FilterChain
)
from markov_passgen.core import EntropyCalculator

# Create filter chain
filters = FilterChain([
    LengthFilter(min_length=12, max_length=20),
    CharacterSetFilter(require_digit=True, require_special=True),
    EntropyFilter(min_entropy=50.0, entropy_calculator=EntropyCalculator())
])

# Apply filters during generation
generator = PasswordGenerator(model, min_length=12, max_length=20)
passwords = generator.generate_filtered(count=100, filter_chain=filters)
```

### Text Processing

```python
from markov_passgen.transformers import TextCleaner, CaseTransformer, CharacterTransformer

# Clean and normalize text
cleaner = TextCleaner(
    remove_punctuation=True,
    remove_digits=False,
    remove_whitespace=True,
    lowercase=True
)
cleaned_text = cleaner.clean(raw_text)

# Transform case patterns
case_transformer = CaseTransformer()
titled = case_transformer.transform(text, style="title")  # Title Case
camel = case_transformer.transform(text, style="camel")   # camelCase
snake = case_transformer.transform(text, style="snake")   # snake_case

# Character substitutions
char_transformer = CharacterTransformer()
char_transformer.add_rule("a", "@")
char_transformer.add_rule("e", "3")
transformed = char_transformer.transform("password")  # p@ssword -> p@ssw0rd
```

### Password Transformations

```python
from markov_passgen.transformers import (
    LeetSpeakTransformer,
    CaseVariationTransformer,
    SubstitutionTransformer,
    TransformerChain
)

# Leetspeak transformation
leet = LeetSpeakTransformer(probability=0.5)
leet_password = leet.transform("password")  # p@ssw0rd

# Case variations
case_var = CaseVariationTransformer()
varied = case_var.transform("password")  # PaSsWoRd

# Custom substitutions
sub = SubstitutionTransformer()
sub.add_rule("a", ["@", "4"])
sub.add_rule("o", ["0"])
substituted = sub.transform("password")

# Chain multiple transformers
chain = TransformerChain([leet, case_var, sub])
result = chain.transform("password")
```

### Multi-Corpus Analysis

```python
from markov_passgen.core import MultiCorpusManager

# Create manager with multiple corpora
manager = MultiCorpusManager(ngram_size=3)
manager.add_corpus("common_passwords.txt", weight=0.5)
manager.add_corpus("english_words.txt", weight=0.3)
manager.add_corpus("usernames.txt", weight=0.2)

# Build merged model
merged_model = manager.build_merged_model()

# Generate passwords from merged model
generator = PasswordGenerator(merged_model, min_length=10, max_length=16)
passwords = generator.generate(count=50)

# Get corpus statistics
stats = manager.get_corpus_stats()
for stat in stats:
    print(f"{stat['name']}: {stat['char_count']} chars, weight={stat['weight']}")
```

### Visualization and Analysis

```python
from markov_passgen.visualization import NGramVisualizer
from markov_passgen.core import EntropyCalculator

# Create visualizer
viz = NGramVisualizer(style="seaborn-v0_8-darkgrid")

# Plot n-gram frequencies
viz.plot_ngram_frequencies(model, top_n=20, output_path="ngram_freq.png")

# Plot password entropy distribution
entropy_calc = EntropyCalculator()
viz.plot_entropy_distribution(
    passwords,
    entropy_calc,
    bins=30,
    output_path="entropy_dist.png"
)

# Plot length distribution
viz.plot_length_distribution(passwords, bins=20, output_path="length_dist.png")

# Plot character frequency
viz.plot_character_distribution(text, top_n=30, output_path="char_freq.png")

# Compare multiple corpora
viz.plot_corpus_comparison(corpus_stats, output_path="corpus_comparison.png")

# Cleanup
viz.close_all()
```

## 🛠️ CLI Reference

### Generate Command

```bash
markov-passgen generate [OPTIONS]
```

**Options:**

- `--corpus PATH`: Path to text corpus file
- `--multi-corpus`: Enable multi-corpus mode
- `--corpus-list PATH [PATH ...]`: Paths to multiple corpus files (multi-corpus mode)
- `--corpus-weights FLOAT [FLOAT ...]`: Weights for each corpus (multi-corpus mode)
- `--ngram-size INT`: N-gram size (2-5, default: 3)
- `--count INT`: Number of passwords to generate (default: 10)
- `--min-length INT`: Minimum password length (default: 8)
- `--max-length INT`: Maximum password length (default: 16)
- `--require-digit`: Require at least one digit
- `--require-lowercase`: Require at least one lowercase letter
- `--require-uppercase`: Require at least one uppercase letter
- `--require-special`: Require at least one special character
- `--min-entropy FLOAT`: Minimum entropy threshold
- `--transform CHOICE`: Apply transformation (leetspeak, case_variation, substitution)
- `--output PATH`: Write passwords to file
- `--show-entropy`: Display entropy for each password

### Visualize Corpus Command

```bash
markov-passgen visualize-corpus [OPTIONS]
```

**Options:**

- `--corpus PATH`: Path to corpus file (required)
- `--ngram-size INT`: N-gram size (default: 3)
- `--ngram-freq PATH`: Output path for n-gram frequency plot
- `--char-dist PATH`: Output path for character distribution plot
- `--top-n INT`: Number of top items to display (default: 20)

### Visualize Passwords Command

```bash
markov-passgen visualize-passwords [OPTIONS]
```

**Options:**

- `--wordlist PATH`: Path to password wordlist file (required)
- `--entropy-dist PATH`: Output path for entropy distribution plot
- `--length-dist PATH`: Output path for length distribution plot
- `--bins INT`: Number of bins for histograms (default: 30)

### Visualize Multi-Corpus Command

```bash
markov-passgen visualize-multi-corpus [OPTIONS]
```

**Options:**

- `--corpus-list PATH [PATH ...]`: Paths to corpus files (required)
- `--corpus-weights FLOAT [FLOAT ...]`: Weights for each corpus
- `--output PATH`: Output path for comparison plot (required)

## 📊 Output Formats

Visualization plots support multiple formats:
- **PNG**: Raster graphics (default, 300 DPI)
- **JPG**: Compressed raster graphics (300 DPI)
- **SVG**: Vector graphics (scalable)
- **PDF**: Print-ready vector graphics

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/markov_passgen --cov-report=html

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Building Distribution

```bash
# Build wheel and source distribution
python -m build

# Upload to PyPI (when ready)
twine upload dist/*
```

## 📚 Documentation

- [Development Plan](development-plan.md): Detailed project roadmap and phases
- [API Reference](docs/api/): Complete API documentation
- [Tutorials](docs/tutorials/): Step-by-step guides and examples
- [Architecture](docs/architecture.md): System design and component overview

## 🔐 Security Considerations

**Important**: This tool is designed for **security research and testing purposes only**. Generated passwords should be used in controlled environments for:

- Password strength analysis
- Penetration testing with proper authorization
- Security research and academic studies
- Training machine learning models for password security

**Do NOT use** generated passwords for:
- Actual user accounts or systems
- Production environments
- Unauthorized access attempts

Generated passwords may contain patterns from source corpora and should not be considered cryptographically secure.

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by password cracking research and Markov chain text generation
- Built with [Click](https://click.palletsprojects.com/) for CLI
- Visualization powered by [matplotlib](https://matplotlib.org/) and [seaborn](https://seaborn.pydata.org/)

## 📮 Contact

- GitHub: [markmysler/markov-passgen](https://github.com/markmysler/markov-passgen)
- Issues: [GitHub Issues](https://github.com/markmysler/markov-passgen/issues)

---

**Disclaimer**: This tool is for educational and authorized security testing purposes only. Users are responsible for compliance with applicable laws and regulations.
