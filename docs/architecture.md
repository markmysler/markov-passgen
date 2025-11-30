# Markov PassGen Architecture

This document provides an overview of the system architecture, design principles, and component interactions.

## Design Principles

### 1. Single Responsibility Principle (SRP)
Each class has one clear purpose:
- `CorpusLoader`: Reads text files
- `NGramBuilder`: Builds Markov models
- `PasswordGenerator`: Generates passwords
- `EntropyCalculator`: Calculates entropy

### 2. Open/Closed Principle (OCP)
Components are open for extension but closed for modification:
- Filters implement `BaseFilter` interface
- Transformers implement `PasswordTransformer` interface
- New implementations can be added without changing existing code

### 3. Dependency Inversion
High-level modules depend on abstractions:
- `PasswordGenerator` accepts any n-gram model
- `FilterChain` works with any `BaseFilter` implementation
- `TransformerChain` works with any transformer

### 4. Composition Over Inheritance
- Filter chains compose multiple filters
- Transformer chains compose multiple transformers
- Multi-corpus manager composes multiple corpus loaders

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                            │
│  ┌─────────┐  ┌──────────┐  ┌──────────────┐               │
│  │generate │  │visualize │  │multi-corpus  │               │
│  │command  │  │commands  │  │commands      │               │
│  └────┬────┘  └─────┬────┘  └──────┬───────┘               │
└───────┼─────────────┼───────────────┼──────────────────────┘
        │             │               │
        ▼             ▼               ▼
┌─────────────────────────────────────────────────────────────┐
│                      Core Components                         │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │CorpusLoader  │  │ NGramBuilder │  │MultiCorpus      │   │
│  │              │  │              │  │Manager          │   │
│  └──────┬───────┘  └──────┬───────┘  └────────┬────────┘   │
│         │                 │                    │            │
│         └─────────────────┼────────────────────┘            │
│                           ▼                                 │
│                  ┌────────────────┐                         │
│                  │Password        │                         │
│                  │Generator       │                         │
│                  └───────┬────────┘                         │
│                          │                                  │
└──────────────────────────┼──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌────────────────┐  ┌──────────────┐
│Filters       │  │Transformers    │  │Analysis      │
│              │  │                │  │              │
│• Length      │  │• LeetSpeak     │  │• Entropy     │
│• CharSet     │  │• CaseVariation │  │• Visualizer  │
│• Entropy     │  │• Substitution  │  │              │
│• FilterChain │  │• TransformChain│  │              │
└──────────────┘  └────────────────┘  └──────────────┘
```

## Component Details

### Core Module (`src/markov_passgen/core/`)

#### CorpusLoader
Responsible for reading text files and handling encoding.

**Key Methods:**
- `load()`: Read and return corpus text
- `validate()`: Check file exists and is readable

**Dependencies:** None (pure I/O)

#### NGramBuilder
Builds n-gram frequency models from text.

**Key Methods:**
- `build_model(text)`: Create n-gram frequency dictionary
- `_extract_ngrams(text)`: Extract n-grams with context

**Data Structure:**
```python
{
    "pa": {"s": 10, "r": 5, "t": 3},  # "pa" followed by "s" 10 times
    "as": {"s": 15, "h": 2},          # "as" followed by "s" 15 times
    ...
}
```

#### PasswordGenerator
Generates passwords using probabilistic selection.

**Key Methods:**
- `generate(count)`: Generate N passwords
- `generate_filtered(count, filter_chain)`: Generate with filters
- `_select_next_char(context)`: Weighted random selection

**Algorithm:**
1. Start with random n-gram from model
2. Look up possible next characters
3. Select next char weighted by frequency
4. Append and shift context window
5. Repeat until length criteria met

#### MultiCorpusManager
Manages multiple corpora with weights.

**Key Methods:**
- `add_corpus(path, weight)`: Register corpus
- `build_merged_model()`: Create weighted merged model
- `get_corpus_stats()`: Get corpus statistics

**Merging Algorithm:**
```python
merged_freq[ngram][next_char] = 
    sum(corpus_freq[ngram][next_char] * corpus_weight)
```

#### EntropyCalculator
Calculates Shannon entropy for passwords.

**Formula:**
```
H(X) = -Σ p(x) * log₂(p(x))
```

Where p(x) is the probability of each character.

### Filters Module (`src/markov_passgen/filters/`)

All filters implement `BaseFilter` interface:

```python
class BaseFilter(ABC):
    @abstractmethod
    def apply(self, password: str) -> bool:
        pass
```

#### LengthFilter
Checks password length bounds.

#### CharacterSetFilter
Validates presence of required character types:
- Digits
- Uppercase letters
- Lowercase letters
- Special characters

#### EntropyFilter
Ensures minimum entropy threshold.

#### FilterChain
Composes multiple filters (AND logic):
```python
def apply(self, password: str) -> bool:
    return all(f.apply(password) for f in self.filters)
```

### Transformers Module (`src/markov_passgen/transformers/`)

#### Text Processing

**TextCleaner**: Normalizes raw text
- Remove punctuation
- Remove digits
- Remove whitespace
- Convert case

**CaseTransformer**: Applies case styles
- lowercase
- UPPERCASE
- Title Case
- camelCase
- snake_case
- PascalCase

**CharacterTransformer**: Character-level substitutions
- Custom mapping rules
- Preserves unmapped characters

#### Password Transformers

**LeetSpeakTransformer**: Common character substitutions
```python
{
    'a': '@', 'e': '3', 'i': '1', 'o': '0',
    's': '$', 't': '7', 'l': '1'
}
```

**CaseVariationTransformer**: Case patterns
- Alternating: `AbCdEf`
- Random: `aBcDeF`
- First upper: `Abcdef`

**SubstitutionTransformer**: Custom substitution rules
- One-to-many mappings
- Probabilistic selection

**TransformerChain**: Applies transformers in sequence

### Visualization Module (`src/markov_passgen/visualization/`)

#### NGramVisualizer
Creates statistical plots using matplotlib/seaborn.

**Supported Visualizations:**
1. N-gram frequency bar charts
2. Entropy distribution histograms
3. Length distribution histograms
4. Character frequency charts
5. Multi-corpus comparison plots

**Output Formats:**
- PNG (raster, 300 DPI)
- JPG (compressed raster, 300 DPI)
- SVG (vector)
- PDF (vector)

### CLI Module (`src/markov_passgen/cli.py`)

Uses Click framework for command-line interface.

**Commands:**
- `generate`: Password generation
- `visualize-corpus`: Corpus analysis
- `visualize-passwords`: Password analysis
- `visualize-multi-corpus`: Corpus comparison

## Data Flow

### Simple Generation Flow
```
Text File → CorpusLoader → Raw Text
                              ↓
                         NGramBuilder → N-Gram Model
                                            ↓
                                    PasswordGenerator → Passwords
```

### Filtered Generation Flow
```
Text File → CorpusLoader → Raw Text
                              ↓
                         NGramBuilder → N-Gram Model
                                            ↓
                                    PasswordGenerator
                                            ↓
                                      FilterChain
                                     (Length, CharSet, Entropy)
                                            ↓
                                    Filtered Passwords
```

### Multi-Corpus Flow
```
Corpus 1 (weight 0.5) ─┐
Corpus 2 (weight 0.3) ─┼→ MultiCorpusManager
Corpus 3 (weight 0.2) ─┘        ↓
                          Build Merged Model
                                 ↓
                          PasswordGenerator → Passwords
```

### Transformation Flow
```
Generated Password → TransformerChain
                        ↓
                    LeetSpeak → CaseVariation → Substitution
                                                      ↓
                                             Transformed Password
```

## Performance Considerations

### N-Gram Building
- **Time Complexity**: O(n) where n is text length
- **Space Complexity**: O(k) where k is unique n-grams
- **Optimization**: Use dict for O(1) lookups

### Password Generation
- **Time Complexity**: O(m*l) where m is count, l is avg length
- **Space Complexity**: O(m*l) for storing passwords
- **Optimization**: Weighted random selection using cumulative sums

### Filtering
- **Time Complexity**: O(m*f) where f is filter count
- **Space Complexity**: O(1) per filter
- **Optimization**: Short-circuit evaluation in FilterChain

### Multi-Corpus Merging
- **Time Complexity**: O(k*c) where k is n-grams, c is corpus count
- **Space Complexity**: O(k) for merged model
- **Optimization**: In-place frequency accumulation

## Testing Strategy

### Unit Tests
Test individual components in isolation:
- Each class has dedicated test file
- Mock dependencies
- Test edge cases and error conditions

### Integration Tests
Test component interactions:
- Corpus → Model → Generator pipeline
- Filter chains
- Transformer chains
- Multi-corpus workflows

### End-to-End Tests
Test complete user workflows:
- CLI command execution
- File I/O
- Full generation pipelines

### Coverage Goals
- Overall: 85%+
- Core modules: 90%+
- Filters: 100%
- Transformers: 95%+

## Extension Points

### Adding New Filters
```python
class CustomFilter(BaseFilter):
    def apply(self, password: str) -> bool:
        # Implement custom logic
        return meets_criteria
```

### Adding New Transformers
```python
class CustomTransformer(PasswordTransformer):
    def transform(self, password: str) -> str:
        # Implement transformation
        return transformed
```

### Adding New Visualizations
```python
class CustomVisualizer(NGramVisualizer):
    def plot_custom(self, data, output_path):
        # Create custom plot
        plt.savefig(output_path)
```

## Security Architecture

### Threat Model
- **Not a cryptographic tool**: Passwords are predictable
- **Research purposes only**: Not for production use
- **No sensitive data**: Don't train on real passwords

### Design Decisions
- No password hashing (not needed for generation)
- No network communication (offline tool)
- No persistent storage (stateless)

## Future Enhancements

### Planned Features
1. **GPU Acceleration**: Faster n-gram building
2. **Distributed Generation**: Multi-process password generation
3. **Real-time Analysis**: Live entropy/strength feedback
4. **Custom Alphabets**: Support for non-ASCII characters
5. **Pattern Detection**: Identify common patterns in generated passwords

### API Stability
- Core interfaces are stable
- Internal implementations may change
- Breaking changes will bump major version

## References

- [Markov Chains](https://en.wikipedia.org/wiki/Markov_chain)
- [Shannon Entropy](https://en.wikipedia.org/wiki/Entropy_(information_theory))
- [Password Strength](https://en.wikipedia.org/wiki/Password_strength)
