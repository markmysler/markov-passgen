# Markov Chain Password Generator - Autonomous Development Plan

## High-Level Overview

This plan guides the autonomous development of a production-grade Python CLI tool that generates human-like password candidates using Markov chains. The project follows strict OOP principles with Single Responsibility Principle (SRP), comprehensive test-driven development (TDD), and includes full CI/CD automation for PyPI publication via GitHub Actions. Development progresses through 7 distinct phases from minimal functionality to advanced features, with mandatory test validation and git commits after each successful phase. Each phase includes detailed logging of implementation steps, failures, debugging attempts, and resolutions to ensure systematic progress and prevent repeated errors.

The final deliverable is a pip-installable package (`markov-passgen`) with CLI entrypoint, comprehensive documentation, 90%+ test coverage, and automated workflows for linting, testing, building, and publishing to PyPI with secure secret management.

---

## Table of Contents

1. [Architecture Blueprint](#architecture-blueprint)
2. [Phase-by-Phase Development Plan](#phase-by-phase-development-plan)
3. [Testing Strategy & Matrix](#testing-strategy--matrix)
4. [Error Diagnosis Policy](#error-diagnosis-policy)
5. [Git Workflow](#git-workflow)
6. [PyPI Packaging Requirements](#pypi-packaging-requirements)
7. [GitHub Actions Workflows](#github-actions-workflows)
8. [Documentation Requirements](#documentation-requirements)
9. [Success Criteria Checklist](#success-criteria-checklist)

---

## Architecture Blueprint

### Package Structure

```
markov-passgen/
├── .github/
│   └── workflows/
│       ├── test.yml
│       ├── lint.yml
│       └── publish.yml
├── src/
│   └── markov_passgen/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── corpus_loader.py
│       │   ├── ngram_builder.py
│       │   ├── generator.py
│       │   └── entropy_calculator.py
│       ├── filters/
│       │   ├── __init__.py
│       │   ├── length_filter.py
│       │   ├── character_filter.py
│       │   └── filter_chain.py
│       ├── transformers/
│       │   ├── __init__.py
│       │   ├── leetspeak.py
│       │   ├── keyboard_adjacency.py
│       │   └── mutation_rules.py
│       ├── visualization/
│       │   ├── __init__.py
│       │   └── markov_visualizer.py
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── text_cleaner.py
│       │   └── parallel_executor.py
│       └── config/
│           ├── __init__.py
│           └── settings.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_corpus_loader.py
│   │   ├── test_ngram_builder.py
│   │   ├── test_generator.py
│   │   ├── test_entropy_calculator.py
│   │   ├── test_filters.py
│   │   ├── test_transformers.py
│   │   └── test_utils.py
│   ├── integration/
│   │   ├── test_generation_pipeline.py
│   │   ├── test_multi_corpus.py
│   │   └── test_filter_chain.py
│   └── e2e/
│       ├── test_cli.py
│       └── test_full_workflow.py
├── docs/
│   ├── architecture.md
│   ├── usage.md
│   └── examples.md
├── examples/
│   ├── sample_corpus.txt
│   └── advanced_config.json
├── .gitignore
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
└── development_log.txt
```

### Core Classes and Responsibilities

#### 1. **CorpusLoader** (`core/corpus_loader.py`)
**Single Responsibility**: Load and validate text corpus from files or streams

**Methods**:
- `load_from_file(filepath: str) -> str`: Load corpus from single file
- `load_from_files(filepaths: List[str]) -> str`: Merge multiple corpus files
- `validate_corpus(text: str) -> bool`: Ensure corpus meets minimum requirements
- `get_corpus_stats() -> Dict[str, int]`: Return character count, word count, unique chars

**Use Cases**:
- Load single text file
- Load multiple files and merge
- Handle UTF-8 encoded files
- Validate minimum corpus size (100+ chars)
- Handle compressed files (.gz, .zip)

**Abuse Cases**:
- Non-existent file path
- Empty file
- Binary file instead of text
- Extremely large file (>1GB)
- Invalid encoding

---

#### 2. **TextCleaner** (`utils/text_cleaner.py`)
**Single Responsibility**: Normalize and clean text corpus

**Methods**:
- `lowercase(text: str) -> str`: Convert to lowercase
- `remove_punctuation(text: str) -> str`: Strip punctuation
- `remove_digits(text: str) -> str`: Remove numbers
- `stem_words(text: str) -> str`: Apply stemming
- `clean(text: str, options: CleanOptions) -> str`: Apply selected cleaning operations

**Use Cases**:
- Lowercase normalization
- Punctuation removal
- Digit preservation for password generation
- Custom cleaning pipeline
- Unicode normalization

**Abuse Cases**:
- None type input
- Empty string
- Only whitespace
- Invalid regex patterns
- Malformed Unicode

---

#### 3. **NGramBuilder** (`core/ngram_builder.py`)
**Single Responsibility**: Build n-gram frequency dictionary from corpus

**Methods**:
- `build(text: str, n: int) -> Dict[str, Dict[str, int]]`: Create n-gram model
- `get_next_char_probabilities(prefix: str) -> Dict[str, float]`: Get weighted next char options
- `add_to_model(text: str)`: Incrementally update model
- `save_model(filepath: str)`: Serialize model to JSON
- `load_model(filepath: str)`: Deserialize model from JSON

**Use Cases**:
- Build bigram (n=2) model
- Build trigram (n=3) model
- Variable n-gram sizes (2-5)
- Incremental model updates
- Model persistence

**Abuse Cases**:
- n < 1
- n > corpus length
- Empty corpus
- Corpus shorter than n
- Invalid model file format

---

#### 4. **PasswordGenerator** (`core/generator.py`)
**Single Responsibility**: Generate password candidates from n-gram model

**Methods**:
- `generate(count: int, length: int, seed: Optional[str] = None) -> List[str]`: Generate passwords
- `generate_with_entropy(count: int, min_entropy: float) -> List[Tuple[str, float]]`: Generate with entropy scores
- `set_random_seed(seed: int)`: Enable deterministic generation
- `get_generation_stats() -> Dict`: Return generation statistics

**Use Cases**:
- Generate N passwords
- Fixed length generation
- Variable length (min/max)
- Seed word initialization
- Deterministic mode with random seed
- Parallel generation for large batches

**Abuse Cases**:
- count = 0 or negative
- length < 1
- length > 1000
- Invalid seed word (not in corpus)
- Insufficient n-gram data
- Memory exhaustion (count > 10M)

---

#### 5. **EntropyCalculator** (`core/entropy_calculator.py`)
**Single Responsibility**: Calculate password entropy scores

**Methods**:
- `calculate_shannon_entropy(password: str) -> float`: Shannon entropy
- `calculate_markov_entropy(password: str, ngram_model: Dict) -> float`: Markov-based entropy
- `estimate_crack_time(password: str, attempts_per_second: int) -> str`: Human-readable crack time

**Use Cases**:
- Shannon entropy calculation
- Markov model entropy
- Crack time estimation
- Batch entropy scoring
- Entropy-based filtering

**Abuse Cases**:
- Empty password
- Non-string input
- Invalid ngram model
- Extremely long password
- Non-ASCII characters

---

#### 6. **FilterChain** (`filters/filter_chain.py`)
**Single Responsibility**: Apply multiple filters in sequence

**Methods**:
- `add_filter(filter: BaseFilter)`: Add filter to chain
- `apply(passwords: List[str]) -> List[str]`: Apply all filters
- `clear()`: Remove all filters

**Use Cases**:
- Combine multiple filters
- Order-dependent filtering
- Reusable filter configurations

**Abuse Cases**:
- No filters added
- Filters remove all candidates
- Circular filter dependencies

---

#### 7. **LengthFilter** (`filters/length_filter.py`)
**Single Responsibility**: Filter by password length

**Methods**:
- `filter(passwords: List[str], min_len: int, max_len: int) -> List[str]`

**Use Cases**:
- Minimum length only
- Maximum length only
- Range filtering
- Exact length

**Abuse Cases**:
- min > max
- Negative values
- Zero length

---

#### 8. **CharacterFilter** (`filters/character_filter.py`)
**Single Responsibility**: Filter by character requirements

**Methods**:
- `filter(passwords: List[str], must_include: Optional[str], must_not_include: Optional[str]) -> List[str]`
- `require_digits(passwords: List[str]) -> List[str]`
- `require_uppercase(passwords: List[str]) -> List[str]`
- `require_special(passwords: List[str]) -> List[str]`

**Use Cases**:
- Require digits
- Require special chars
- Exclude ambiguous chars (0, O, l, 1)
- Custom character sets

**Abuse Cases**:
- Contradictory requirements
- Empty requirement sets
- Invalid regex patterns

---

#### 9. **LeetspeakTransformer** (`transformers/leetspeak.py`)
**Single Responsibility**: Apply leetspeak character substitutions

**Methods**:
- `transform(password: str, probability: float = 0.5) -> str`: Apply random leet
- `get_leet_mapping() -> Dict[str, List[str]]`: Return substitution rules

**Use Cases**:
- Random leetspeak
- Deterministic leetspeak
- Partial substitution
- Custom mapping rules

**Abuse Cases**:
- probability < 0 or > 1
- Empty password
- Unicode edge cases

---

#### 10. **KeyboardAdjacencyTransformer** (`transformers/keyboard_adjacency.py`)
**Single Responsibility**: Apply keyboard proximity mutations

**Methods**:
- `transform(password: str, mutations: int = 1) -> str`: Replace chars with adjacent keys
- `get_adjacent_chars(char: str, layout: str = 'qwerty') -> List[str]`

**Use Cases**:
- QWERTY layout
- DVORAK layout
- Single mutation
- Multiple mutations

**Abuse Cases**:
- mutations < 0
- Unknown layout
- Non-keyboard characters

---

#### 11. **MutationRulesEngine** (`transformers/mutation_rules.py`)
**Single Responsibility**: Apply custom mutation rules

**Methods**:
- `add_rule(rule: Callable[[str], str])`
- `apply_rules(password: str) -> List[str]`: Generate all rule variants
- `load_rules_from_config(filepath: str)`

**Use Cases**:
- Append numbers (e.g., +123)
- Capitalize first letter
- Reverse string
- Insert special chars
- Custom lambda rules

**Abuse Cases**:
- Rules that create duplicates
- Infinite recursion
- Rules that invalidate filters

---

#### 12. **MarkovVisualizer** (`visualization/markov_visualizer.py`)
**Single Responsibility**: Generate Markov chain graph visualization

**Methods**:
- `visualize(ngram_model: Dict, output_path: str, max_nodes: int = 50)`
- `visualize_top_transitions(ngram_model: Dict, top_n: int = 20)`

**Use Cases**:
- Full graph visualization
- Top transitions only
- Export to PNG/SVG/PDF
- Interactive HTML output

**Abuse Cases**:
- Model too large for rendering
- Invalid output format
- Graphviz not installed

---

#### 13. **ParallelExecutor** (`utils/parallel_executor.py`)
**Single Responsibility**: Execute generation in parallel

**Methods**:
- `generate_parallel(generator: PasswordGenerator, count: int, workers: int) -> List[str]`

**Use Cases**:
- Multi-core generation
- Progress tracking
- Configurable worker count

**Abuse Cases**:
- workers < 1
- workers > CPU count
- Memory exhaustion

---

#### 14. **CLI** (`cli.py`)
**Single Responsibility**: Parse arguments and orchestrate generation

**Methods**:
- `main()`: Entry point
- `parse_args() -> argparse.Namespace`
- `execute_generate(args)`
- `execute_visualize(args)`
- `execute_analyze(args)`

**Subcommands**:
- `generate`: Generate passwords
- `visualize`: Create Markov graph
- `analyze`: Analyze corpus or passwords

**Use Cases**:
- Single corpus generation
- Multi-corpus merge
- Custom output file
- JSON output format
- Verbose logging
- Config file input

**Abuse Cases**:
- Missing required args
- Invalid file paths
- Conflicting flags
- Output file write-protected

---

## Phase-by-Phase Development Plan

### **Phase 0: Project Initialization (30 min)**

#### Deliverables:
1. Git repository initialized
2. Package structure created
3. `pyproject.toml` configured
4. `.gitignore` created
5. `development_log.txt` initialized
6. Virtual environment set up

#### Steps:
1. Create project directory: `markov-passgen/`
2. Initialize git: `git init`
3. Create branch structure: `main` branch only (trunk-based)
4. Create all directories per architecture blueprint
5. Create empty `__init__.py` files in all package directories
6. Create `pyproject.toml` with:
   - Build system: `setuptools`, `wheel`
   - Project metadata: name, version (0.1.0), description, authors, license (MIT)
   - Dependencies: `click>=8.0.0`, `graphviz>=0.20`
   - Dev dependencies: `pytest>=7.0.0`, `pytest-cov>=4.0.0`, `black>=23.0.0`, `flake8>=6.0.0`, `mypy>=1.0.0`
   - Entry point: `markov-passgen = markov_passgen.cli:main`
7. Create `.gitignore`:
   ```
   __pycache__/
   *.py[cod]
   *$py.class
   .pytest_cache/
   .coverage
   htmlcov/
   dist/
   build/
   *.egg-info/
   .venv/
   .env
   .mypy_cache/
   .tox/
   *.log
   .DS_Store
   ```
8. Create `development_log.txt` with header:
   ```
   MARKOV PASSWORD GENERATOR - DEVELOPMENT LOG
   ===========================================
   Start Time: [timestamp]
   
   Phase 0: Project Initialization
   --------------------------------
   ```

#### Tests:
- Verify package can be installed in editable mode: `pip install -e .`
- Verify CLI entry point exists: `markov-passgen --help` (should fail gracefully with not implemented)

#### Log Requirements:
- Record directory creation
- Record file creation
- Record any environment issues

#### Commit Trigger:
- All files created
- Package installs without errors
- Log updated

#### Git Commit Message:
```
Phase 0: Initialize project structure

- Create package directory structure
- Configure pyproject.toml with dependencies
- Set up .gitignore
- Initialize development log
```

---

### **Phase 1: Minimal Viable Product (1.5-2h)**

#### Deliverables:
1. `CorpusLoader` class
2. `NGramBuilder` class (bigram only, n=2)
3. `PasswordGenerator` class (basic generation)
4. Basic CLI with `generate` subcommand
5. Output to `wordlist.txt`
6. Unit tests for each class
7. E2E test for full generation

#### Implementation Order:

1. **Implement `CorpusLoader`**:
   - `load_from_file(filepath: str) -> str`
   - `validate_corpus(text: str) -> bool` (min 100 chars)
   - `get_corpus_stats() -> Dict`

2. **Implement `NGramBuilder`**:
   - `build(text: str, n: int = 2) -> Dict[str, Dict[str, int]]`
   - Build frequency dictionary: `{"ab": {"c": 5, "d": 3}, ...}`
   - `get_next_char_probabilities(prefix: str) -> Dict[str, float]`

3. **Implement `PasswordGenerator`**:
   - `generate(count: int, length: int) -> List[str]`
   - Use weighted random choice from n-gram probabilities
   - Random starting prefix from model keys

4. **Implement Basic CLI**:
   - Use `argparse` or `click`
   - Subcommand: `generate`
   - Required args: `--corpus PATH`, `--count N`, `--length L`
   - Output to `wordlist.txt`

5. **Write Unit Tests**:
   - `tests/unit/test_corpus_loader.py`:
     - Test load valid file
     - Test load non-existent file (should raise FileNotFoundError)
     - Test validate valid corpus
     - Test validate empty corpus (should return False)
     - Test get_corpus_stats
   - `tests/unit/test_ngram_builder.py`:
     - Test build with valid corpus
     - Test build with empty corpus (should raise ValueError)
     - Test get_next_char_probabilities
     - Test invalid prefix (should return empty or raise)
   - `tests/unit/test_generator.py`:
     - Test generate N passwords
     - Test generate with length L
     - Test count=0 (should return empty list or raise)
     - Test length=0 (should raise ValueError)

6. **Write E2E Test**:
   - `tests/e2e/test_cli.py`:
     - Create sample corpus file
     - Run CLI: `markov-passgen generate --corpus sample.txt --count 10 --length 8`
     - Verify `wordlist.txt` created
     - Verify 10 passwords generated
     - Verify each password has length 8

#### Testing Execution:
```bash
pytest tests/unit/ -v
pytest tests/e2e/ -v
pytest --cov=src/markov_passgen --cov-report=html
```

#### Log Requirements:
- Record each class implementation start/end
- Record any bugs encountered during implementation
- Record test failures and causes
- Record debugging attempts:
  - Hypothesis for failure
  - Fix attempted
  - Result (pass/fail)
  - Note: "Checked log to ensure fix not attempted before"

#### Commit Trigger:
- All unit tests pass
- E2E test passes
- Coverage >= 80%
- Log updated

#### Git Commit Message:
```
Phase 1: Implement minimal viable product

- Add CorpusLoader with file loading and validation
- Add NGramBuilder for bigram frequency dictionary
- Add PasswordGenerator for basic weighted generation
- Add CLI with generate subcommand
- Add unit tests with 85% coverage
- Add E2E test for full workflow
```

---

### **Phase 2: Standard Features - Configuration & Filtering (2-2.5h)**

#### Deliverables:
1. Adjustable n-gram size (2-5)
2. `EntropyCalculator` class
3. `LengthFilter` class
4. `CharacterFilter` class
5. `FilterChain` class
6. Seed word support in generator
7. Deterministic mode (random seed)
8. Enhanced CLI with filter flags
9. Unit tests for all new classes
10. Integration tests for filter chain

#### Implementation Order:

1. **Enhance `NGramBuilder`**:
   - Support n-gram sizes 2-5 via parameter
   - Validate n within range

2. **Implement `EntropyCalculator`**:
   - `calculate_shannon_entropy(password: str) -> float`
   - Formula: -Σ(p(x) * log2(p(x)))
   - `calculate_markov_entropy(password: str, ngram_model: Dict) -> float`

3. **Implement `LengthFilter`**:
   - `filter(passwords: List[str], min_len: int, max_len: int) -> List[str]`

4. **Implement `CharacterFilter`**:
   - `require_digits(passwords: List[str]) -> List[str]`
   - `require_uppercase(passwords: List[str]) -> List[str]`
   - `require_special(passwords: List[str]) -> List[str]`

5. **Implement `FilterChain`**:
   - `add_filter(filter: BaseFilter)`
   - `apply(passwords: List[str]) -> List[str]`

6. **Enhance `PasswordGenerator`**:
   - `generate(..., seed: Optional[str] = None)`
   - If seed provided, start generation from seed
   - `set_random_seed(seed: int)` for deterministic mode

7. **Enhance CLI**:
   - Add flags: `--ngram-size N`, `--min-length L`, `--max-length L`
   - Add flags: `--require-digits`, `--require-uppercase`, `--require-special`
   - Add flags: `--seed-word WORD`, `--random-seed N`
   - Add flag: `--min-entropy E`

8. **Write Unit Tests**:
   - `tests/unit/test_entropy_calculator.py`:
     - Test Shannon entropy for known strings
     - Test empty password (should handle gracefully)
     - Test Markov entropy
   - `tests/unit/test_filters.py`:
     - Test LengthFilter with various ranges
     - Test CharacterFilter requirements
     - Test FilterChain ordering
     - Test filters that eliminate all candidates

9. **Write Integration Tests**:
   - `tests/integration/test_filter_chain.py`:
     - Generate 100 passwords
     - Apply length filter (8-12)
     - Apply require digits
     - Apply require uppercase
     - Verify all remaining passwords meet all criteria

#### Testing Execution:
```bash
pytest tests/unit/test_entropy_calculator.py -v
pytest tests/unit/test_filters.py -v
pytest tests/integration/ -v
pytest --cov=src/markov_passgen --cov-report=html
```

#### Log Requirements:
- Record implementation of each feature
- Record test failures with detailed error messages
- Record debugging process:
  - List possible causes (sorted by probability)
  - Try fix for most likely cause
  - Re-run tests
  - If still failing, try next cause
  - Explicitly note: "Verified this fix not attempted in previous log entries"

#### Error Diagnosis Example:
```
Test Failure: test_require_digits fails
Error: AssertionError: Expected 10 passwords with digits, got 3

Possible Causes (sorted by probability):
1. Generator not producing enough passwords with digits (70%)
2. Filter logic incorrect (20%)
3. Test expectation incorrect (10%)

Attempt 1: Increase generation count to 100, re-filter
Result: Still only 3 passwords with digits
Conclusion: Cause #1 eliminated

Attempt 2: Check filter logic - found bug in regex pattern
Fix: Changed pattern from '\d' to r'\d'
Result: All tests pass
```

#### Commit Trigger:
- All unit tests pass
- All integration tests pass
- Coverage >= 85%
- Log updated

#### Git Commit Message:
```
Phase 2: Add standard features (filters, entropy, config)

- Support adjustable n-gram sizes (2-5)
- Add EntropyCalculator with Shannon and Markov methods
- Add LengthFilter and CharacterFilter classes
- Add FilterChain for composable filtering
- Add seed word and deterministic mode to generator
- Enhance CLI with filter and config flags
- Add unit and integration tests (87% coverage)
```

---

### **Phase 3: Text Processing & Cleaning (1.5h)**

#### Deliverables:
1. `TextCleaner` class
2. Cleaning options: lowercase, remove punctuation, remove digits, stemming
3. Integration with `CorpusLoader`
4. CLI flags for cleaning options
5. Unit tests for all cleaning operations

#### Implementation Order:

1. **Implement `TextCleaner`**:
   - `lowercase(text: str) -> str`
   - `remove_punctuation(text: str) -> str`
   - `remove_digits(text: str) -> str`
   - `stem_words(text: str) -> str` (use `nltk` or `SnowballStemmer`)
   - `clean(text: str, options: CleanOptions) -> str`
   - `CleanOptions` dataclass with bool flags

2. **Integrate with `CorpusLoader`**:
   - Add `clean_corpus(cleaning_options: CleanOptions) -> str` method
   - Apply cleaning after loading

3. **Update CLI**:
   - Add flags: `--lowercase`, `--remove-punctuation`, `--remove-digits`, `--stem`

4. **Write Unit Tests**:
   - `tests/unit/test_text_cleaner.py`:
     - Test lowercase conversion
     - Test punctuation removal
     - Test digit removal
     - Test stemming
     - Test combined operations
     - Test empty input
     - Test Unicode handling

#### Testing Execution:
```bash
pytest tests/unit/test_text_cleaner.py -v
pytest --cov=src/markov_passgen --cov-report=html
```

#### Log Requirements:
- Document each cleaning operation implementation
- Record any edge cases discovered
- Record test results

#### Commit Trigger:
- All tests pass
- Coverage >= 85%

#### Git Commit Message:
```
Phase 3: Add text cleaning and preprocessing

- Add TextCleaner with lowercase, punctuation, digit, stemming
- Integrate cleaning with CorpusLoader
- Add CLI flags for cleaning options
- Add comprehensive unit tests
```

---

### **Phase 4: Advanced Features - Transformations (2-2.5h)**

#### Deliverables:
1. `LeetspeakTransformer` class
2. `KeyboardAdjacencyTransformer` class
3. `MutationRulesEngine` class
4. Integration with generator pipeline
5. CLI flags for transformations
6. Unit tests for each transformer

#### Implementation Order:

1. **Implement `LeetspeakTransformer`**:
   - Define mapping: `{"a": ["4", "@"], "e": ["3"], "i": ["1", "!"], ...}`
   - `transform(password: str, probability: float) -> str`
   - Random substitution based on probability

2. **Implement `KeyboardAdjacencyTransformer`**:
   - Define QWERTY layout adjacency map
   - `get_adjacent_chars(char: str) -> List[str]`
   - `transform(password: str, mutations: int) -> str`

3. **Implement `MutationRulesEngine`**:
   - `add_rule(name: str, rule: Callable[[str], str])`
   - Built-in rules:
     - `append_number`: Add 123, 2024, etc.
     - `capitalize_first`: Capitalize first letter
     - `reverse`: Reverse string
     - `insert_special`: Insert !@# at random positions
   - `apply_rules(password: str) -> List[str]`

4. **Update CLI**:
   - Add flags: `--leetspeak`, `--keyboard-mutations N`, `--mutation-rules RULES`

5. **Write Unit Tests**:
   - `tests/unit/test_transformers.py`:
     - Test leetspeak with probability 0, 0.5, 1.0
     - Test keyboard adjacency for known chars
     - Test mutation rules independently
     - Test combined transformations

#### Testing Execution:
```bash
pytest tests/unit/test_transformers.py -v
pytest --cov=src/markov_passgen --cov-report=html
```

#### Log Requirements:
- Document transformer implementations
- Record any unexpected behaviors
- Document debugging steps for test failures

#### Commit Trigger:
- All tests pass
- Coverage >= 85%

#### Git Commit Message:
```
Phase 4: Add password transformations

- Add LeetspeakTransformer with configurable substitutions
- Add KeyboardAdjacencyTransformer for typo simulation
- Add MutationRulesEngine with extensible rules
- Integrate transformers into generation pipeline
- Add CLI flags for transformation options
```

---

### **Phase 5: Advanced Features - Multi-Source & Parallelization (2h)**

#### Deliverables:
1. Multi-corpus merging in `CorpusLoader`
2. `ParallelExecutor` for parallel generation
3. Enhanced CLI for multiple corpus files
4. Progress bar for generation
5. Integration tests for multi-corpus
6. Performance tests

#### Implementation Order:

1. **Enhance `CorpusLoader`**:
   - `load_from_files(filepaths: List[str]) -> str`
   - Merge corpora with optional weighting

2. **Implement `ParallelExecutor`**:
   - `generate_parallel(generator: PasswordGenerator, count: int, workers: int) -> List[str]`
   - Use `multiprocessing.Pool` or `concurrent.futures`
   - Add progress tracking with `tqdm`

3. **Update CLI**:
   - Accept multiple `--corpus` arguments
   - Add `--workers N` flag
   - Add `--progress` flag for progress bar

4. **Write Integration Tests**:
   - `tests/integration/test_multi_corpus.py`:
     - Load 3 corpus files
     - Verify merged n-gram model
     - Generate passwords from merged model
   - `tests/integration/test_parallel.py`:
     - Generate 10,000 passwords with 4 workers
     - Verify count matches
     - Verify uniqueness (if required)

#### Testing Execution:
```bash
pytest tests/integration/test_multi_corpus.py -v
pytest tests/integration/test_parallel.py -v
pytest --cov=src/markov_passgen --cov-report=html
```

#### Log Requirements:
- Document multi-corpus merging logic
- Document parallelization approach
- Record performance metrics (generation speed)

#### Commit Trigger:
- All tests pass
- Coverage >= 85%

#### Git Commit Message:
```
Phase 5: Add multi-corpus and parallel generation

- Support loading and merging multiple corpus files
- Add ParallelExecutor for multi-core generation
- Add progress bar with tqdm
- Add CLI support for multiple corpus files
- Add integration tests for multi-corpus scenarios
```

---

### **Phase 6: Visualization & Analysis (1.5h)**

#### Deliverables:
1. `MarkovVisualizer` class
2. CLI `visualize` subcommand
3. CLI `analyze` subcommand for corpus/password analysis
4. Unit tests for visualizer
5. Example visualizations in docs

#### Implementation Order:

1. **Implement `MarkovVisualizer`**:
   - Requires `graphviz` library
   - `visualize(ngram_model: Dict, output_path: str, max_nodes: int)`
   - Create directed graph with weighted edges
   - Export to PNG, SVG, or PDF

2. **Add CLI `visualize` Subcommand**:
   - `markov-passgen visualize --corpus PATH --output graph.png --max-nodes 50`

3. **Add CLI `analyze` Subcommand**:
   - `markov-passgen analyze corpus --file PATH`
     - Show character distribution
     - Show most common n-grams
     - Show corpus stats
   - `markov-passgen analyze passwords --file wordlist.txt`
     - Show entropy distribution
     - Show length distribution
     - Show character type usage

4. **Write Unit Tests**:
   - `tests/unit/test_visualizer.py`:
     - Test graph creation
     - Test output formats
     - Test max_nodes limiting

#### Testing Execution:
```bash
pytest tests/unit/test_visualizer.py -v
pytest --cov=src/markov_passgen --cov-report=html
```

#### Log Requirements:
- Document visualization implementation
- Record any graphviz issues
- Include sample visualizations in log

#### Commit Trigger:
- All tests pass
- Coverage >= 85%

#### Git Commit Message:
```
Phase 6: Add visualization and analysis tools

- Add MarkovVisualizer with graphviz integration
- Add visualize subcommand for Markov chain graphs
- Add analyze subcommand for corpus and password analysis
- Add unit tests for visualization
```

---

### **Phase 7: Documentation & Packaging (2h)**

#### Deliverables:
1. Comprehensive README.md
2. `docs/architecture.md`
3. `docs/usage.md`
4. `docs/examples.md`
5. Example corpus files in `examples/`
6. CHANGELOG.md
7. LICENSE (MIT)
8. Version bump to 1.0.0
9. Final test run with 100% coverage target

#### Implementation Order:

1. **Write README.md**:
   - Project description
   - Installation instructions
   - Quick start guide
   - Feature overview
   - CLI reference
   - Contributing guidelines
   - License

2. **Write `docs/architecture.md`**:
   - Package structure diagram
   - Class hierarchy
   - Data flow diagrams
   - Design principles (SRP, OOP)

3. **Write `docs/usage.md`**:
   - Detailed CLI reference
   - Configuration file format
   - Advanced usage scenarios
   - Troubleshooting

4. **Write `docs/examples.md`**:
   - Example 1: Basic password generation
   - Example 2: Multi-corpus with filters
   - Example 3: Advanced transformations
   - Example 4: Visualization
   - Example 5: Custom mutation rules

5. **Create Example Files**:
   - `examples/sample_corpus.txt`: 500-line text corpus
   - `examples/advanced_config.json`: Configuration file example

6. **Create CHANGELOG.md**:
   ```
   # Changelog
   
   ## [1.0.0] - 2024-XX-XX
   ### Added
   - Initial release
   - Markov chain password generation
   - Configurable n-gram sizes
   - Entropy scoring
   - Filters (length, character requirements)
   - Transformations (leetspeak, keyboard adjacency, mutations)
   - Multi-corpus support
   - Parallel generation
   - Text cleaning and preprocessing
   - Markov chain visualization
   - Corpus and password analysis tools
   ```

7. **Create LICENSE**:
   - MIT License template

8. **Version Bump**:
   - Update `pyproject.toml` version to `1.0.0`

9. **Final Test Run**:
   ```bash
   pytest tests/ -v --cov=src/markov_passgen --cov-report=html --cov-report=term
   ```

#### Log Requirements:
- Document documentation creation
- Record final test results
- Record coverage percentage

#### Commit Trigger:
- All documentation complete
- All tests pass
- Coverage >= 90%

#### Git Commit Message:
```
Phase 7: Add comprehensive documentation and bump to v1.0.0

- Add comprehensive README with installation and usage
- Add architecture documentation
- Add detailed usage guide
- Add usage examples
- Add CHANGELOG and LICENSE
- Bump version to 1.0.0
- Achieve 92% test coverage
```

---

## Testing Strategy & Matrix

### Testing Pyramid

```
           /\
          /E2E\      5-10 tests
         /------\
        /  INT   \    15-25 tests
       /----------\
      /    UNIT    \  50-75 tests
     /--------------\
```

### Test Categories

#### Unit Tests (50-75 tests)
**Purpose**: Test individual methods and functions in isolation

**Coverage Requirements**:
- Each public method must have 3-7 tests
- Each use case must have a test
- Each abuse case must have a test
- Edge cases must be covered

**Example Test Matrix for `CorpusLoader.load_from_file()`**:

| Test ID | Category | Input | Expected Output | Rationale |
|---------|----------|-------|-----------------|-----------|
| TC-CL-01 | Use Case | Valid file path | File contents as string | Happy path |
| TC-CL-02 | Use Case | UTF-8 file with special chars | Correctly decoded string | Unicode handling |
| TC-CL-03 | Use Case | Large file (10MB) | File contents | Performance |
| TC-CL-04 | Abuse Case | Non-existent file | `FileNotFoundError` | Error handling |
| TC-CL-05 | Abuse Case | Empty file | Empty string or error | Edge case |
| TC-CL-06 | Abuse Case | Binary file | `UnicodeDecodeError` or graceful handling | Type validation |
| TC-CL-07 | Abuse Case | File with no read permissions | `PermissionError` | Permission handling |
| TC-CL-08 | Edge Case | File with only whitespace | Validation failure | Content validation |

#### Integration Tests (15-25 tests)
**Purpose**: Test interactions between multiple components

**Example Scenarios**:
- Load corpus → Clean → Build n-grams → Generate passwords
- Load multiple corpora → Merge → Build model → Generate
- Generate → Filter → Transform → Output
- Load corpus → Visualize Markov chain
- Generate large batch → Parallel execution

#### E2E Tests (5-10 tests)
**Purpose**: Test complete workflows through CLI

**Example Scenarios**:
1. Basic generation workflow:
   ```bash
   markov-passgen generate --corpus sample.txt --count 100 --length 12 --output passwords.txt
   ```
   - Verify file created
   - Verify 100 passwords
   - Verify all lengths = 12

2. Advanced workflow with filters:
   ```bash
   markov-passgen generate --corpus sample.txt --count 50 --min-length 8 --max-length 16 \
     --require-digits --require-uppercase --leetspeak --output secure.txt
   ```
   - Verify all passwords meet requirements

3. Multi-corpus workflow:
   ```bash
   markov-passgen generate --corpus corp1.txt --corpus corp2.txt --corpus corp3.txt \
     --count 1000 --workers 4 --progress --output merged.txt
   ```
   - Verify parallel execution
   - Verify correct count

4. Visualization workflow:
   ```bash
   markov-passgen visualize --corpus sample.txt --ngram-size 3 --output markov.png
   ```
   - Verify PNG created
   - Verify file is valid image

5. Analysis workflow:
   ```bash
   markov-passgen analyze passwords --file passwords.txt --min-entropy 50
   ```
   - Verify entropy analysis output

### Use Cases & Abuse Cases per Feature

#### CorpusLoader
**Use Cases**:
1. Load single text file
2. Load multiple text files
3. Load file with UTF-8 encoding
4. Load large file (>100MB)
5. Validate corpus minimum size
6. Get corpus statistics
7. Handle compressed files (.gz)

**Abuse Cases**:
1. Load non-existent file
2. Load empty file
3. Load binary file
4. Load file with invalid encoding
5. Load directory instead of file
6. Load file without read permissions
7. Load extremely large file (OOM scenario)
8. Load file with null bytes

#### NGramBuilder
**Use Cases**:
1. Build bigram model (n=2)
2. Build trigram model (n=3)
3. Build with n=2 to 5
4. Get next character probabilities
5. Handle start-of-word markers
6. Save model to JSON
7. Load model from JSON
8. Incrementally update model

**Abuse Cases**:
1. Build with n < 1
2. Build with n > corpus length
3. Build with empty corpus
4. Get probabilities for non-existent prefix
5. Load corrupted JSON model
6. Build with corpus shorter than n
7. Save/load with invalid file paths

#### PasswordGenerator
**Use Cases**:
1. Generate N passwords
2. Generate with fixed length
3. Generate with min/max length range
4. Generate with seed word
5. Generate in deterministic mode
6. Generate with entropy threshold
7. Batch generation (10,000+)
8. Generate with parallel execution

**Abuse Cases**:
1. Generate with count = 0
2. Generate with negative count
3. Generate with length < 1
4. Generate with length > 1000
5. Generate with invalid seed word
6. Generate from empty n-gram model
7. Generate with insufficient n-gram data
8. Memory exhaustion (count > 10M)

#### Filters (Length, Character)
**Use Cases**:
1. Filter by minimum length only
2. Filter by maximum length only
3. Filter by length range
4. Filter by exact length
5. Require digits
6. Require uppercase
7. Require special characters
8. Exclude ambiguous characters
9. Combine multiple filters
10. Custom character sets

**Abuse Cases**:
1. min_length > max_length
2. Negative length values
3. Zero length
4. Contradictory requirements (require and exclude same char)
5. Empty requirement sets
6. Invalid regex patterns
7. Filters that eliminate all candidates

#### Transformers
**Use Cases**:
1. Apply leetspeak with probability 0.5
2. Apply full leetspeak (probability 1.0)
3. Apply keyboard adjacency mutations (1-3)
4. Apply mutation rules (append number, capitalize, reverse)
5. Combine multiple transformations
6. Custom leetspeak mapping
7. DVORAK keyboard layout

**Abuse Cases**:
1. Leetspeak probability < 0 or > 1
2. Negative mutation count
3. Keyboard layout not found
4. Transform empty password
5. Unicode characters not in keyboard map
6. Infinite mutation loops
7. Mutations that break filters

#### Visualizer
**Use Cases**:
1. Visualize full Markov chain
2. Visualize top N transitions
3. Export to PNG
4. Export to SVG
5. Export to PDF
6. Limit max nodes for large models

**Abuse Cases**:
1. Visualize empty model
2. Model too large (>10,000 nodes)
3. Invalid output format
4. Graphviz not installed
5. Output path not writable

### Test Execution Rules

1. **After each phase**:
   ```bash
   # Run all tests
   pytest tests/ -v
   
   # If failures, stop and diagnose
   # Do not proceed to next phase
   ```

2. **Before any commit**:
   ```bash
   # Run tests with coverage
   pytest tests/ -v --cov=src/markov_passgen --cov-report=term
   
   # Coverage must be >= 85% (target: 90%+)
   ```

3. **Test failure protocol**:
   - Capture full error output
   - Log error in `development_log.txt`
   - List possible causes (sorted by probability)
   - Check log to ensure fix not attempted before
   - Try most likely fix
   - Re-run tests
   - If still failing, try next cause
   - Repeat until fixed or all causes exhausted

4. **When to modify tests**:
   - **LAST RESORT ONLY**
   - Only if:
     - All fixes attempted
     - No other possible causes remain
     - Test expectation is demonstrably incorrect
     - Change logged with full justification

---

## Error Diagnosis Policy

### Structured Debugging Process

#### Step 1: Capture Error Information
When a test fails:
1. Copy full error output to log
2. Note which test(s) failed
3. Note error type (AssertionError, Exception, etc.)
4. Note error message

#### Step 2: Analyze Error
1. Read error message carefully
2. Identify assertion that failed
3. Identify expected vs actual values
4. Review relevant code paths

#### Step 3: Generate Hypotheses
List all possible causes, sorted by probability:

**Probability Ranking Criteria**:
- **70-90%**: Most likely (logic error in new code)
- **20-40%**: Somewhat likely (integration issue, dependency)
- **5-15%**: Less likely (environment, edge case)
- **<5%**: Unlikely (test error, framework bug)

**Common Causes by Probability**:
1. **Logic error in newly written code** (70%)
2. **Off-by-one error** (60%)
3. **Missing null/empty check** (50%)
4. **Incorrect data type** (40%)
5. **Integration issue between components** (30%)
6. **Incorrect test expectation** (10%)
7. **Environment/dependency issue** (5%)

#### Step 4: Check Log for Previous Attempts
**CRITICAL**: Before attempting any fix:
```
1. Open development_log.txt
2. Search for similar error message
3. Search for similar test name
4. Verify this fix has not been attempted
5. Log: "Checked log - fix not attempted previously"
```

#### Step 5: Attempt Fix
For each hypothesis (starting with highest probability):
1. **Log hypothesis**:
   ```
   Hypothesis #1 (70%): Generator not producing enough valid passwords
   Reasoning: Filter eliminating most candidates
   ```

2. **Log fix attempt**:
   ```
   Fix Attempt #1:
   - Increase generation count from 10 to 100
   - Re-apply filters
   - Expect: More passwords pass filters
   ```

3. **Apply fix**

4. **Re-run tests**:
   ```bash
   pytest tests/unit/test_generator.py::test_with_filters -v
   ```

5. **Log result**:
   ```
   Result: PASS
   All tests passing after increasing generation count
   Root cause confirmed: insufficient candidate pool
   ```

OR

```
Result: FAIL
Still failing with same error
Hypothesis #1 eliminated
Proceeding to Hypothesis #2
```

#### Step 6: Iterate or Escalate
- If fixed: Log resolution, update code, re-run ALL tests
- If not fixed: Move to next hypothesis
- If all hypotheses exhausted: Re-analyze error with fresh perspective
- If still stuck: Modify test ONLY if demonstrably incorrect

### Example Debugging Session Log

```
=== PHASE 2 - TEST FAILURE ===
Timestamp: 2024-01-15 14:32:00

Test Failed: tests/unit/test_filters.py::test_require_digits
Error Type: AssertionError
Error Message: assert 3 == 10
  Expected 10 passwords with digits, got 3

Step 1: Error Captured ✓

Step 2: Analysis
- Test expects 10 passwords with digits
- Generator produces 100 candidates
- Filter applied: CharacterFilter.require_digits()
- Only 3 passwords retained
- Conclusion: Either generator not producing enough passwords with digits,
  or filter logic incorrect

Step 3: Hypotheses (sorted by probability)
1. Generator corpus lacks digits (80%)
   - Sample corpus may be pure text without numbers
2. Filter regex incorrect (15%)
   - Pattern may not match digits properly
3. Test expectation too high (5%)
   - 10/100 may be unrealistic for random generation

Step 4: Log Check
- Searched for "require_digits" in log
- No previous attempts found
- Logged: "Checked log - no previous fix attempts for this test"

Step 5: Fix Attempt #1
Hypothesis: Generator corpus lacks digits
Fix: Add sample numbers to corpus file
Code change:
  - Modified tests/fixtures/sample_corpus.txt
  - Added lines with numbers: "password123", "secure2024", etc.
Test run:
  pytest tests/unit/test_filters.py::test_require_digits -v
Result: FAIL - still only 3 passwords

Step 6: Fix Attempt #2
Hypothesis #1 refined: Need more candidates
Fix: Increase generation count from 100 to 1000
Code change:
  - Modified test_require_digits: count=1000
Test run:
  pytest tests/unit/test_filters.py::test_require_digits -v
Result: FAIL - now 28 passwords, but test expects 10, why failing?

Step 7: Re-read Error
ERROR: Re-read error message: assert 28 >= 10
Wait - test is now PASSING! Misread initial result.
Resolution: Increasing candidate pool solved issue
Root Cause: Insufficient candidates for stochastic filter

Step 8: Verify Fix
Full test run:
  pytest tests/unit/test_filters.py -v
Result: ALL PASS

Logged resolution:
"test_require_digits fixed by increasing candidate pool from 100 to 1000.
Root cause: stochastic generation needs larger sample size for filters.
Updated test to generate 1000 candidates."

=== END DEBUG SESSION ===
```

### When to Modify Tests

**ONLY modify tests if ALL of the following are true**:
1. ✅ All reasonable fixes attempted
2. ✅ All possible code causes eliminated
3. ✅ Test expectation is demonstrably incorrect
4. ✅ Product requirement has changed
5. ✅ Modification logged with full justification

**Example of valid test modification**:
```
Test: test_generate_length
Expected: All passwords exactly length 8
Actual: Passwords length 8-9

Investigation:
- Generator code reviewed: correctly enforces max length
- Edge case found: seed word of length 9 used
- Product requirement: seed word should be preserved
- Conclusion: Test expectation incorrect

Modification:
- Changed assertion from exact length to length <= max_length
- Logged justification: "Seed words can exceed target length per requirement"
```

---

## Git Workflow

### Repository Initialization

```bash
# Initialize repo
git init
git config user.name "Markov PassGen Bot"
git config user.email "bot@markovpassgen.dev"

# Create .gitignore
# (content as specified in Phase 0)

# Initial commit
git add .gitignore
git commit -m "Initial commit: Add .gitignore"
```

### Branching Strategy

**Trunk-based development** (single `main` branch):
- All development on `main`
- Commits only after phase tests pass
- Tags for versions

**Rationale**: 
- Autonomous agent doesn't need feature branches
- Linear history easier to track
- Simplifies automation

### Commit Strategy

**Commit Triggers**:
1. ✅ All tests in current phase pass
2. ✅ Coverage threshold met (85%+)
3. ✅ Development log updated
4. ✅ Code formatted (black)
5. ✅ Linted (flake8)

**Commit Message Format**:
```
Phase X: Brief description (50 chars max)

- Bullet point of feature/change
- Bullet point of feature/change
- Add tests with X% coverage
- Fix bug in Y

[optional] Breaking changes: ...
[optional] Migration notes: ...
```

**Example Commits**:
```
Phase 1: Implement minimal viable product

- Add CorpusLoader with file loading and validation
- Add NGramBuilder for bigram frequency dictionary
- Add PasswordGenerator for basic weighted generation
- Add CLI with generate subcommand
- Add unit tests with 85% coverage
- Add E2E test for full workflow
```

```
Phase 4: Add password transformations

- Add LeetspeakTransformer with configurable substitutions
- Add KeyboardAdjacencyTransformer for typo simulation
- Add MutationRulesEngine with extensible rules
- Integrate transformers into generation pipeline
- Add CLI flags for transformation options
```

### Pre-Commit Checks (Automated)

```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/ --max-line-length=100

# Type check (optional but recommended)
mypy src/

# Run tests
pytest tests/ -v --cov=src/markov_passgen --cov-report=term

# If all pass, commit
git add .
git commit -m "Phase X: Description"
```

### Tagging Strategy

**Version Tags**:
- Phase 7 completion: `v1.0.0`
- Future releases: Semantic versioning (MAJOR.MINOR.PATCH)

```bash
# After Phase 7 completion
git tag -a v1.0.0 -m "Release version 1.0.0

- Initial public release
- Full feature set implemented
- 92% test coverage
- Production-ready"

git push origin v1.0.0
```

**Tag Format**:
- `vMAJOR.MINOR.PATCH`
- Annotated tags with release notes

### Branch Protection (for future)

When moving to team development:
- Protect `main` branch
- Require PR reviews
- Require CI checks to pass
- No force pushes

---

## PyPI Packaging Requirements

### pyproject.toml Configuration

```toml
[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "markov-passgen"
version = "1.0.0"
description = "Generate human-like password candidates using Markov chains"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
maintainers = [
    {name = "Your Name", email = "your.email@example.com"}
]
keywords = ["password", "generator", "markov", "security", "wordlist"]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: Information Technology",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Security",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Utilities",
]

dependencies = [
    "click>=8.0.0",
    "tqdm>=4.65.0",
    "graphviz>=0.20",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
    "build>=0.10.0",
    "twine>=4.0.0",
]

[project.urls]
Homepage = "https://github.com/yourusername/markov-passgen"
Documentation = "https://github.com/yourusername/markov-passgen#readme"
Repository = "https://github.com/yourusername/markov-passgen"
Issues = "https://github.com/yourusername/markov-passgen/issues"
Changelog = "https://github.com/yourusername/markov-passgen/blob/main/CHANGELOG.md"

[project.scripts]
markov-passgen = "markov_passgen.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=src/markov_passgen --cov-report=html --cov-report=term-missing"

[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311']

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Versioning Scheme

**Semantic Versioning** (MAJOR.MINOR.PATCH):
- **MAJOR**: Incompatible API changes (e.g., 2.0.0)
- **MINOR**: New features, backward compatible (e.g., 1.1.0)
- **PATCH**: Bug fixes, backward compatible (e.g., 1.0.1)

**Version Bumping Strategy**:
- Initial release: `1.0.0`
- Bug fix: `1.0.1`, `1.0.2`, ...
- New feature: `1.1.0`, `1.2.0`, ...
- Breaking change: `2.0.0`

**Version Management**:
- Single source of truth: `pyproject.toml`
- Also define in `src/markov_passgen/__init__.py`:
  ```python
  __version__ = "1.0.0"
  ```
- Automated bump via GitHub Actions (optional)

### CLI Entrypoint

**Entry Point Configuration** (in `pyproject.toml`):
```toml
[project.scripts]
markov-passgen = "markov_passgen.cli:main"
```

**CLI Module** (`src/markov_passgen/cli.py`):
```python
import click

@click.group()
@click.version_option()
def main():
    """Markov Chain Password Generator"""
    pass

@main.command()
@click.option('--corpus', multiple=True, required=True, help='Path to corpus file')
@click.option('--count', default=100, help='Number of passwords to generate')
@click.option('--length', default=12, help='Password length')
@click.option('--output', default='wordlist.txt', help='Output file')
def generate(corpus, count, length, output):
    """Generate passwords from corpus"""
    # Implementation
    pass

if __name__ == '__main__':
    main()
```

### Package Metadata

**Required Files**:
1. **README.md**: Comprehensive project description
2. **LICENSE**: MIT License
3. **CHANGELOG.md**: Version history
4. **src/markov_passgen/py.typed**: Marker for type hints

**MANIFEST.in** (if needed for non-Python files):
```
include README.md
include LICENSE
include CHANGELOG.md
include src/markov_passgen/py.typed
recursive-include examples *.txt *.json
```

### Building the Package

```bash
# Install build tools
pip install build twine

# Build distributions
python -m build

# Output:
# dist/
#   markov_passgen-1.0.0-py3-none-any.whl
#   markov_passgen-1.0.0.tar.gz

# Check package
twine check dist/*

# Test upload to TestPyPI (optional)
twine upload --repository testpypi dist/*

# Verify installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ markov-passgen

# Upload to PyPI (production)
twine upload dist/*
```

---

## GitHub Actions Workflows

### 1. Lint Workflow (`.github/workflows/lint.yml`)

```yaml
name: Lint

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install black flake8 mypy
        pip install -e .
    
    - name: Check formatting with Black
      run: black --check src/ tests/
    
    - name: Lint with flake8
      run: flake8 src/ tests/ --max-line-length=100 --statistics
    
    - name: Type check with mypy
      run: mypy src/
      continue-on-error: true
```

### 2. Test Workflow (`.github/workflows/test.yml`)

```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install system dependencies (Ubuntu)
      if: matrix.os == 'ubuntu-latest'
      run: sudo apt-get update && sudo apt-get install -y graphviz
    
    - name: Install system dependencies (macOS)
      if: matrix.os == 'macos-latest'
      run: brew install graphviz
    
    - name: Install system dependencies (Windows)
      if: matrix.os == 'windows-latest'
      run: choco install graphviz -y
    
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    
    - name: Run tests with coverage
      run: |
        pytest tests/ -v --cov=src/markov_passgen --cov-report=xml --cov-report=term
    
    - name: Upload coverage to Codecov
      if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.11'
      uses: codecov/codecov-action@v4
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
```

### 3. Build & Publish Workflow (`.github/workflows/publish.yml`)

```yaml
name: Build and Publish to PyPI

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Check package
      run: twine check dist/*
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v4
      with:
        name: dist
        path: dist/
  
  test-install:
    needs: build
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Download artifacts
      uses: actions/download-artifact@v4
      with:
        name: dist
        path: dist/
    
    - name: Install system dependencies
      run: sudo apt-get update && sudo apt-get install -y graphviz
    
    - name: Install package from wheel
      run: |
        pip install dist/*.whl
    
    - name: Test CLI entrypoint
      run: |
        markov-passgen --version
        markov-passgen --help
  
  publish-testpypi:
    needs: test-install
    runs-on: ubuntu-latest
    
    steps:
    - name: Download artifacts
      uses: actions/download-artifact@v4
      with:
        name: dist
        path: dist/
    
    - name: Publish to TestPyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.TEST_PYPI_API_TOKEN }}
        repository-url: https://test.pypi.org/legacy/
        skip-existing: true
  
  publish-pypi:
    needs: publish-testpypi
    runs-on: ubuntu-latest
    environment: release
    
    steps:
    - name: Download artifacts
      uses: actions/download-artifact@v4
      with:
        name: dist
        path: dist/
    
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
  
  create-release:
    needs: publish-pypi
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Extract version from tag
      id: get_version
      run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT
    
    - name: Extract changelog
      id: changelog
      run: |
        # Extract changelog for this version
        awk '/^## \[${{ steps.get_version.outputs.VERSION }}\]/,/^## \[/ {print}' CHANGELOG.md | head -n -1 > release_notes.txt
    
    - name: Create GitHub Release
      uses: softprops/action-gh-release@v2
      with:
        body_path: release_notes.txt
        draft: false
        prerelease: false
        files: |
          dist/*.whl
          dist/*.tar.gz
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 4. Security Scanning Workflow (`.github/workflows/security.yml`)

```yaml
name: Security Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install safety bandit
        pip install -e .
    
    - name: Run Safety (dependency vulnerabilities)
      run: safety check --json
      continue-on-error: true
    
    - name: Run Bandit (code security issues)
      run: bandit -r src/ -f json -o bandit-report.json
      continue-on-error: true
    
    - name: Upload Bandit report
      uses: actions/upload-artifact@v4
      with:
        name: bandit-report
        path: bandit-report.json
```

### GitHub Secrets Configuration

**Required Secrets**:
1. **PYPI_API_TOKEN**: PyPI API token for publishing
   - Generate at: https://pypi.org/manage/account/token/
   - Scope: Project-specific token for `markov-passgen`

2. **TEST_PYPI_API_TOKEN**: TestPyPI API token
   - Generate at: https://test.pypi.org/manage/account/token/
   - Scope: Project-specific token for `markov-passgen`

**Setting Secrets**:
1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `PYPI_API_TOKEN`
4. Value: `pypi-AgEIcHlw...` (paste token)
5. Repeat for `TEST_PYPI_API_TOKEN`

### Workflow Triggers Summary

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| lint.yml | Push to main, PRs | Code quality checks |
| test.yml | Push to main, PRs | Test suite across OS/Python versions |
| security.yml | Push, PRs, weekly | Dependency and code security scanning |
| publish.yml | Tag push (v*.*.*) | Build, test, publish to PyPI |

### Release Process

**Manual Release**:
```bash
# 1. Update version in pyproject.toml and __init__.py
# 2. Update CHANGELOG.md
# 3. Commit changes
git add pyproject.toml src/markov_passgen/__init__.py CHANGELOG.md
git commit -m "Bump version to 1.0.0"

# 4. Create tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# 5. Push tag
git push origin v1.0.0

# GitHub Actions will automatically:
# - Run tests
# - Build package
# - Publish to TestPyPI
# - Publish to PyPI
# - Create GitHub Release with artifacts
```

**Automated Version Bump** (optional future enhancement):
```yaml
# .github/workflows/auto-version.yml
name: Auto Version Bump

on:
  push:
    branches: [ main ]

jobs:
  bump-version:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Bump version and create tag
      uses: anothrNick/github-tag-action@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        WITH_V: true
        DEFAULT_BUMP: patch
```

---

## Documentation Requirements

### README.md Structure

```markdown
# Markov Password Generator

Generate human-like password candidates using Markov chains from text corpora.

[![Tests](https://github.com/username/markov-passgen/workflows/Tests/badge.svg)](https://github.com/username/markov-passgen/actions)
[![Coverage](https://codecov.io/gh/username/markov-passgen/branch/main/graph/badge.svg)](https://codecov.io/gh/username/markov-passgen)
[![PyPI](https://img.shields.io/pypi/v/markov-passgen.svg)](https://pypi.org/project/markov-passgen/)
[![Python](https://img.shields.io/pypi/pyversions/markov-passgen.svg)](https://pypi.org/project/markov-passgen/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Features

- 🔤 N-gram based Markov chain password generation
- 📊 Entropy scoring (Shannon and Markov-based)
- 🔍 Flexible filtering (length, character requirements)
- 🔀 Password transformations (leetspeak, keyboard adjacency, custom mutations)
- 📚 Multi-corpus support with merging
- ⚡ Parallel generation for large batches
- 📈 Markov chain visualization
- 🧹 Text corpus preprocessing and cleaning
- 🖥️ Comprehensive CLI with subcommands

## Installation

```bash
pip install markov-passgen
```

## Quick Start

```bash
# Generate 100 passwords from a corpus
markov-passgen generate --corpus sample.txt --count 100 --length 12

# Advanced usage with filters
markov-passgen generate \
  --corpus corpus1.txt --corpus corpus2.txt \
  --count 1000 \
  --min-length 8 --max-length 16 \
  --require-digits --require-uppercase \
  --leetspeak \
  --output passwords.txt

# Visualize Markov chain
markov-passgen visualize --corpus sample.txt --output markov.png

# Analyze passwords
markov-passgen analyze passwords --file passwords.txt --min-entropy 50
```

## Documentation

- [Architecture Overview](docs/architecture.md)
- [Usage Guide](docs/usage.md)
- [Examples](docs/examples.md)
- [API Reference](docs/api.md)

## Requirements

- Python 3.8+
- graphviz (for visualization)

## Development

```bash
# Clone repository
git clone https://github.com/username/markov-passgen.git
cd markov-passgen

# Install in development mode
pip install -e .[dev]

# Run tests
pytest tests/ -v --cov=src/markov_passgen

# Format code
black src/ tests/

# Lint
flake8 src/ tests/
```

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Acknowledgments

- Markov chain theory and applications
- Password research community
- Open source contributors
```

### docs/architecture.md

```markdown
# Architecture Overview

## Package Structure

[Include directory tree]

## Design Principles

### Single Responsibility Principle (SRP)

Each class has ONE responsibility:
- **CorpusLoader**: Load and validate text
- **NGramBuilder**: Build frequency model
- **PasswordGenerator**: Generate candidates
- etc.

### Object-Oriented Design

- Clear class hierarchies
- Composition over inheritance
- Interface segregation

## Data Flow

```
Corpus Files
    ↓
CorpusLoader → TextCleaner
    ↓
NGramBuilder
    ↓
PasswordGenerator → FilterChain → Transformers
    ↓
Output File
```

## Class Diagram

[Include UML or diagram]

## Testing Strategy

- Unit tests: Individual methods
- Integration tests: Component interactions
- E2E tests: Full CLI workflows

## Extension Points

How to add:
- Custom filters
- Custom transformers
- Custom mutation rules
- New CLI subcommands
```

### docs/usage.md

```markdown
# Usage Guide

## CLI Reference

### generate

Generate passwords from corpus.

```bash
markov-passgen generate [OPTIONS]
```

**Options**:
- `--corpus PATH`: Path to corpus file (required, multiple allowed)
- `--count N`: Number of passwords (default: 100)
- `--length L`: Password length (default: 12)
- `--min-length L`: Minimum length
- `--max-length L`: Maximum length
- `--ngram-size N`: N-gram size 2-5 (default: 3)
- `--seed-word WORD`: Start generation from word
- `--random-seed N`: Deterministic mode
- `--require-digits`: Require at least one digit
- `--require-uppercase`: Require uppercase letter
- `--require-special`: Require special character
- `--min-entropy E`: Minimum entropy score
- `--leetspeak`: Apply leetspeak transformation
- `--keyboard-mutations N`: Apply keyboard adjacency mutations
- `--mutation-rules RULES`: Apply mutation rules
- `--workers N`: Parallel workers (default: 1)
- `--progress`: Show progress bar
- `--output FILE`: Output file (default: wordlist.txt)
- `--format FORMAT`: Output format (txt, json, csv)

### visualize

Visualize Markov chain graph.

```bash
markov-passgen visualize [OPTIONS]
```

**Options**:
- `--corpus PATH`: Path to corpus file (required)
- `--ngram-size N`: N-gram size (default: 3)
- `--output FILE`: Output file (default: markov.png)
- `--max-nodes N`: Maximum nodes to display (default: 50)
- `--format FORMAT`: Output format (png, svg, pdf)

### analyze

Analyze corpus or passwords.

```bash
markov-passgen analyze corpus --file PATH
markov-passgen analyze passwords --file PATH
```

**Options**:
- `--file PATH`: File to analyze (required)
- `--min-entropy E`: Filter by minimum entropy
- `--output FILE`: Save analysis report

## Configuration File

Create `config.json`:

```json
{
  "corpus": ["corpus1.txt", "corpus2.txt"],
  "count": 1000,
  "length": 12,
  "filters": {
    "min_length": 8,
    "max_length": 16,
    "require_digits": true,
    "require_uppercase": true
  },
  "transformations": {
    "leetspeak": true,
    "keyboard_mutations": 2
  }
}
```

Use with:
```bash
markov-passgen generate --config config.json
```

## Python API

```python
from markov_passgen import CorpusLoader, NGramBuilder, PasswordGenerator

# Load corpus
loader = CorpusLoader()
corpus = loader.load_from_file("sample.txt")

# Build model
builder = NGramBuilder()
model = builder.build(corpus, n=3)

# Generate passwords
generator = PasswordGenerator(model)
passwords = generator.generate(count=100, length=12)

print(passwords)
```
```

### docs/examples.md

```markdown
# Examples

## Example 1: Basic Generation

```bash
markov-passgen generate \
  --corpus /usr/share/dict/words \
  --count 50 \
  --length 10 \
  --output passwords.txt
```

**Output**: 50 10-character passwords in `passwords.txt`

## Example 2: High-Entropy Passwords

```bash
markov-passgen generate \
  --corpus corpus.txt \
  --count 100 \
  --min-length 12 \
  --max-length 16 \
  --require-digits \
  --require-uppercase \
  --require-special \
  --min-entropy 60 \
  --output secure_passwords.txt
```

## Example 3: Multi-Corpus with Transformations

```bash
markov-passgen generate \
  --corpus english.txt \
  --corpus technical.txt \
  --corpus slang.txt \
  --count 500 \
  --length 14 \
  --leetspeak \
  --keyboard-mutations 1 \
  --workers 4 \
  --progress \
  --output mixed_passwords.txt
```

## Example 4: Visualization

```bash
markov-passgen visualize \
  --corpus sample.txt \
  --ngram-size 3 \
  --max-nodes 100 \
  --output markov_chain.png
```

## Example 5: Password Analysis

```bash
markov-passgen analyze passwords \
  --file generated_passwords.txt \
  --min-entropy 50 \
  --output analysis_report.json
```

**Output** (analysis_report.json):
```json
{
  "total_passwords": 1000,
  "avg_length": 12.3,
  "avg_entropy": 58.7,
  "character_distribution": {
    "uppercase": 0.15,
    "lowercase": 0.70,
    "digits": 0.10,
    "special": 0.05
  },
  "entropy_distribution": {
    "min": 45.2,
    "max": 72.8,
    "median": 58.5
  }
}
```
```

---

## Success Criteria Checklist

### Phase Completion Criteria

- [ ] **Phase 0: Initialization**
  - [ ] Git repository initialized
  - [ ] All directories created per structure
  - [ ] `pyproject.toml` configured
  - [ ] Package installs with `pip install -e .`
  - [ ] Development log initialized

- [ ] **Phase 1: MVP**
  - [ ] CorpusLoader implemented and tested
  - [ ] NGramBuilder implemented and tested
  - [ ] PasswordGenerator implemented and tested
  - [ ] CLI `generate` subcommand functional
  - [ ] Unit tests: 15+ tests, all passing
  - [ ] E2E test passing
  - [ ] Coverage >= 80%
  - [ ] Git commit created

- [ ] **Phase 2: Standard Features**
  - [ ] Adjustable n-gram sizes (2-5)
  - [ ] EntropyCalculator implemented
  - [ ] Filters implemented (Length, Character)
  - [ ] FilterChain implemented
  - [ ] Seed word and deterministic mode
  - [ ] Unit tests: 25+ total tests
  - [ ] Integration tests: 3+ tests
  - [ ] Coverage >= 85%
  - [ ] Git commit created

- [ ] **Phase 3: Text Processing**
  - [ ] TextCleaner implemented
  - [ ] All cleaning operations tested
  - [ ] Integration with CorpusLoader
  - [ ] CLI flags added
  - [ ] Unit tests: 35+ total tests
  - [ ] Coverage >= 85%
  - [ ] Git commit created

- [ ] **Phase 4: Transformations**
  - [ ] LeetspeakTransformer implemented
  - [ ] KeyboardAdjacencyTransformer implemented
  - [ ] MutationRulesEngine implemented
  - [ ] CLI flags added
  - [ ] Unit tests: 50+ total tests
  - [ ] Coverage >= 85%
  - [ ] Git commit created

- [ ] **Phase 5: Multi-Source & Parallel**
  - [ ] Multi-corpus loading implemented
  - [ ] ParallelExecutor implemented
  - [ ] Progress bar integrated
  - [ ] Integration tests: 6+ tests
  - [ ] Coverage >= 85%
  - [ ] Git commit created

- [ ] **Phase 6: Visualization**
  - [ ] MarkovVisualizer implemented
  - [ ] CLI `visualize` subcommand
  - [ ] CLI `analyze` subcommand
  - [ ] Unit tests: 60+ total tests
  - [ ] Coverage >= 85%
  - [ ] Git commit created

- [ ] **Phase 7: Documentation**
  - [ ] README.md complete
  - [ ] docs/architecture.md complete
  - [ ] docs/usage.md complete
  - [ ] docs/examples.md complete
  - [ ] CHANGELOG.md complete
  - [ ] LICENSE added
  - [ ] Example files created
  - [ ] Version bumped to 1.0.0
  - [ ] All tests passing
  - [ ] Coverage >= 90%
  - [ ] Git commit created
  - [ ] Tag v1.0.0 created

### GitHub Actions Criteria

- [ ] **Lint Workflow**
  - [ ] `.github/workflows/lint.yml` created
  - [ ] Black formatting check passes
  - [ ] Flake8 linting passes
  - [ ] Mypy type checking runs (can fail)

- [ ] **Test Workflow**
  - [ ] `.github/workflows/test.yml` created
  - [ ] Tests run on Ubuntu, macOS, Windows
  - [ ] Tests run on Python 3.8, 3.9, 3.10, 3.11, 3.12
  - [ ] Coverage uploaded to Codecov
  - [ ] All tests passing

- [ ] **Publish Workflow**
  - [ ] `.github/workflows/publish.yml` created
  - [ ] Package builds successfully
  - [ ] Package passes `twine check`
  - [ ] Test installation succeeds
  - [ ] TestPyPI publish configured
  - [ ] PyPI publish configured
  - [ ] GitHub Release creation automated
  - [ ] Secrets configured (PYPI_API_TOKEN, TEST_PYPI_API_TOKEN)

- [ ] **Security Workflow**
  - [ ] `.github/workflows/security.yml` created
  - [ ] Safety check runs
  - [ ] Bandit scan runs

### Final Package Criteria

- [ ] **Package Structure**
  - [ ] All modules in `src/markov_passgen/`
  - [ ] All tests in `tests/`
  - [ ] All docs in `docs/`
  - [ ] Examples in `examples/`

- [ ] **Installation**
  - [ ] Package installs with `pip install markov-passgen`
  - [ ] CLI accessible: `markov-passgen --version`
  - [ ] CLI accessible: `markov-passgen --help`
  - [ ] All dependencies install correctly

- [ ] **Functionality**
  - [ ] Can generate passwords from corpus
  - [ ] All CLI subcommands work
  - [ ] All filters work
  - [ ] All transformations work
  - [ ] Visualization works (with graphviz)
  - [ ] Parallel generation works

- [ ] **Quality**
  - [ ] All tests passing (70+ tests)
  - [ ] Coverage >= 90%
  - [ ] No linting errors
  - [ ] Type hints present
  - [ ] Code formatted with Black

- [ ] **Documentation**
  - [ ] README comprehensive
  - [ ] Architecture documented
  - [ ] Usage documented
  - [ ] Examples provided
  - [ ] Changelog maintained

- [ ] **CI/CD**
  - [ ] All workflows passing
  - [ ] Package published to PyPI
  - [ ] GitHub Release created
  - [ ] Versioning automated

### Autonomous Agent Execution Validation

- [ ] **Logging**
  - [ ] Every phase logged in `development_log.txt`
  - [ ] All test failures logged with debugging steps
  - [ ] All fixes attempted logged
  - [ ] Verification of no-repeat fixes logged

- [ ] **Git History**
  - [ ] One commit per phase
  - [ ] All commit messages follow format
  - [ ] Tag v1.0.0 exists
  - [ ] Linear history (no merge commits)

- [ ] **Error Recovery**
  - [ ] At least one test failure recovered
  - [ ] Debugging process documented
  - [ ] Root cause identified and fixed
  - [ ] No repeated fix attempts

- [ ] **Completeness**
  - [ ] All features from minimal/standard/advanced tiers implemented
  - [ ] All use cases tested
  - [ ] All abuse cases tested
  - [ ] No TODOs or placeholder code

---

## Appendix A: Development Log Template

```
MARKOV PASSWORD GENERATOR - DEVELOPMENT LOG
===========================================
Project Start: [TIMESTAMP]
Agent: Autonomous Coding Agent v1.0

================================================================================
PHASE 0: PROJECT INITIALIZATION
================================================================================
Start Time: [TIMESTAMP]

Tasks:
- [ ] Create directory structure
- [ ] Initialize git repository
- [ ] Create pyproject.toml
- [ ] Create .gitignore
- [ ] Verify package installation

Execution Log:
[TIMESTAMP] Creating project directory: markov-passgen/
[TIMESTAMP] Creating subdirectories: src/, tests/, docs/, .github/workflows/
[TIMESTAMP] Creating __init__.py files in all packages
[TIMESTAMP] Writing pyproject.toml with dependencies
[TIMESTAMP] Writing .gitignore with Python patterns
[TIMESTAMP] Initializing git repository
[TIMESTAMP] Installing package in editable mode
[TIMESTAMP] Testing CLI entry point

Issues Encountered: NONE

Tests Run:
- Package installation: PASS
- CLI entry point exists: PASS (with expected NotImplementedError)

Phase Status: COMPLETE
Commit: [COMMIT HASH] "Phase 0: Initialize project structure"
End Time: [TIMESTAMP]

================================================================================
PHASE 1: MINIMAL VIABLE PRODUCT
================================================================================
Start Time: [TIMESTAMP]

Tasks:
- [ ] Implement CorpusLoader
- [ ] Implement NGramBuilder
- [ ] Implement PasswordGenerator
- [ ] Implement basic CLI
- [ ] Write unit tests
- [ ] Write E2E test

Execution Log:
[TIMESTAMP] Starting CorpusLoader implementation
[TIMESTAMP] Implemented load_from_file() method
[TIMESTAMP] Implemented validate_corpus() method
[TIMESTAMP] Implemented get_corpus_stats() method
[TIMESTAMP] Writing unit tests for CorpusLoader
[TIMESTAMP] Running tests: pytest tests/unit/test_corpus_loader.py -v

Test Results:
- test_load_valid_file: PASS
- test_load_nonexistent_file: PASS
- test_validate_valid_corpus: PASS
- test_validate_empty_corpus: PASS
- test_get_corpus_stats: FAIL

Test Failure Diagnosis:
Test: test_get_corpus_stats
Error: AssertionError: assert 125 == 124
Expected 124 characters, got 125

Possible Causes (sorted by probability):
1. Off-by-one error in character counting (80%)
2. Whitespace handling difference (15%)
3. Test fixture incorrect (5%)

Checked log: No previous attempts for this error

Fix Attempt #1:
Hypothesis: Newline at end of file counted
Investigation: Opened fixture file, confirmed trailing newline
Fix: Updated get_corpus_stats() to strip trailing whitespace before counting
Code change: text.strip() before len(text)
Test run: pytest tests/unit/test_corpus_loader.py::test_get_corpus_stats -v
Result: PASS

Verification: All CorpusLoader tests passing

[TIMESTAMP] Starting NGramBuilder implementation
[... continue similar detailed logging ...]

Issues Encountered:
1. Off-by-one error in corpus stats (RESOLVED)
2. NGramBuilder empty corpus handling (RESOLVED)

Final Test Run:
pytest tests/ -v --cov=src/markov_passgen
Result: 18 tests, 18 passed, 0 failed
Coverage: 87%

Phase Status: COMPLETE
Commit: [COMMIT HASH] "Phase 1: Implement minimal viable product"
End Time: [TIMESTAMP]

================================================================================
[Continue for each phase...]
================================================================================
```

---

## Appendix B: Quick Command Reference

### Development Commands

```bash
# Setup
pip install -e .[dev]

# Testing
pytest tests/ -v
pytest tests/ --cov=src/markov_passgen --cov-report=html
pytest tests/unit/test_specific.py -v

# Formatting & Linting
black src/ tests/
flake8 src/ tests/ --max-line-length=100
mypy src/

# Build
python -m build
twine check dist/*

# Local installation test
pip install dist/*.whl
markov-passgen --version

# Git
git add .
git commit -m "Phase X: Description"
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin main
git push origin v1.0.0
```

### GitHub Actions Testing

```bash
# Lint locally (simulate workflow)
black --check src/ tests/
flake8 src/ tests/ --max-line-length=100

# Test locally (simulate workflow)
pytest tests/ -v --cov=src/markov_passgen --cov-report=xml

# Build locally (simulate workflow)
python -m build
twine check dist/*
```

---

## Summary

This development plan provides a comprehensive, autonomous-execution-optimized roadmap for building a production-ready Markov chain password generator. Key features:

1. **7 Phases**: Minimal → Standard → Advanced features
2. **SRP Architecture**: 14 classes, each with single responsibility
3. **Comprehensive Testing**: 70+ tests, use/abuse cases, 90%+ coverage
4. **Error Diagnosis**: Structured debugging with probability ranking
5. **Git Workflow**: Trunk-based, commit-per-phase, version tagging
6. **PyPI Ready**: Complete packaging with semantic versioning
7. **CI/CD Automation**: 4 GitHub Actions workflows for lint, test, publish, security
8. **Full Documentation**: README, architecture, usage, examples

**Estimated Timeline**: 12-15 hours autonomous execution
**Final Deliverable**: pip-installable package published to PyPI with automated CI/CD

---

END OF DEVELOPMENT PLAN
