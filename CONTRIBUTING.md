# Contributing to Markov PassGen

Thank you for your interest in contributing to Markov PassGen! This document provides guidelines for contributing to the project.

## Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, background, or identity.

### Expected Behavior
- Be respectful and considerate
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior
- Harassment, discrimination, or offensive comments
- Trolling, insulting/derogatory comments, or personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

## Getting Started

### Setting Up Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/markov-passgen.git
   cd markov-passgen
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Verify Installation**
   ```bash
   pytest
   markov-passgen --help
   ```

### Development Workflow

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write code following the style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Run Tests**
   ```bash
   pytest
   pytest --cov=src/markov_passgen --cov-report=html
   ```

4. **Check Code Quality**
   ```bash
   black src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

6. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Contribution Guidelines

### What to Contribute

We welcome contributions in the following areas:

#### Code Contributions
- **Bug Fixes**: Fix issues reported in GitHub Issues
- **New Features**: Implement features from the roadmap or propose new ones
- **Performance Improvements**: Optimize algorithms or data structures
- **Test Coverage**: Add tests for untested code paths

#### Documentation
- **API Documentation**: Add or improve docstrings
- **Tutorials**: Create guides for specific use cases
- **Examples**: Add example scripts or corpus files
- **README Improvements**: Clarify installation or usage instructions

#### Other Contributions
- **Bug Reports**: Report issues with clear reproduction steps
- **Feature Requests**: Propose new features with use cases
- **Code Reviews**: Review open pull requests
- **Community Support**: Answer questions in discussions

### Coding Standards

#### Python Style
Follow PEP 8 with these specifications:

```python
# Line length: 100 characters (configured in pyproject.toml)
# Indentation: 4 spaces
# Quotes: Double quotes for strings (enforced by black)

# Good example
class PasswordGenerator:
    """Generate passwords using Markov chain models.
    
    This class implements probabilistic password generation using n-gram
    frequency models. It supports length constraints and filtering.
    
    Attributes:
        model: N-gram frequency dictionary
        min_length: Minimum password length
        max_length: Maximum password length
    """
    
    def __init__(self, model: dict, min_length: int = 8, max_length: int = 16):
        """Initialize the password generator.
        
        Args:
            model: N-gram frequency dictionary from NGramBuilder
            min_length: Minimum password length (default: 8)
            max_length: Maximum password length (default: 16)
            
        Raises:
            ValueError: If min_length > max_length
        """
        if min_length > max_length:
            raise ValueError("min_length must be <= max_length")
        
        self.model = model
        self.min_length = min_length
        self.max_length = max_length
```

#### Naming Conventions
- **Classes**: `PascalCase` (e.g., `PasswordGenerator`)
- **Functions/Methods**: `snake_case` (e.g., `generate_password`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_NGRAM_SIZE`)
- **Private Methods**: `_leading_underscore` (e.g., `_select_next_char`)

#### Documentation
All public APIs must have docstrings:

```python
def generate(self, count: int = 10) -> list[str]:
    """Generate multiple passwords.
    
    Args:
        count: Number of passwords to generate (default: 10)
        
    Returns:
        List of generated password strings
        
    Raises:
        ValueError: If count is negative
        
    Example:
        >>> generator = PasswordGenerator(model)
        >>> passwords = generator.generate(count=5)
        >>> len(passwords)
        5
    """
```

### Testing Requirements

#### Test Coverage
- **Minimum**: 85% overall coverage
- **Core modules**: 90%+ coverage required
- **New features**: Must include tests

#### Test Structure
```python
# tests/unit/test_feature.py
import pytest
from markov_passgen.core import FeatureClass


class TestFeatureClass:
    """Test suite for FeatureClass."""
    
    def test_basic_functionality(self):
        """Test basic usage."""
        feature = FeatureClass()
        result = feature.process()
        assert result is not None
    
    def test_edge_case(self):
        """Test edge case handling."""
        feature = FeatureClass()
        with pytest.raises(ValueError):
            feature.process(invalid_input)
    
    def test_integration(self):
        """Test integration with other components."""
        # Integration test code
        pass
```

#### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_generator.py

# Run with coverage
pytest --cov=src/markov_passgen --cov-report=html

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

### Commit Message Guidelines

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

#### Examples
```
feat(generator): add support for custom alphabets

Implement custom alphabet configuration to allow non-ASCII
character generation. This enables support for international
character sets.

Closes #123
```

```
fix(filters): correct entropy calculation for empty strings

The entropy calculator was throwing division by zero errors
for empty strings. Added guard clause to return 0.0 for
empty inputs.

Fixes #456
```

```
docs(readme): add installation troubleshooting section

Added common installation issues and solutions based on
user feedback in GitHub Discussions.
```

### Pull Request Process

1. **Before Submitting**
   - Ensure all tests pass
   - Verify code coverage meets requirements
   - Run code quality checks (black, flake8, mypy)
   - Update documentation
   - Add entry to CHANGELOG.md (if applicable)

2. **PR Description**
   Include:
   - Summary of changes
   - Motivation and context
   - Testing performed
   - Related issues (use "Closes #123" or "Fixes #456")
   - Screenshots (for UI changes)

3. **Review Process**
   - At least one maintainer approval required
   - Address review feedback promptly
   - Keep PRs focused and reasonably sized
   - Rebase on main if conflicts occur

4. **After Merge**
   - Delete your feature branch
   - Update your fork's main branch

### Issue Guidelines

#### Reporting Bugs

Use the bug report template and include:

```markdown
**Describe the bug**
Clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. With options '...'
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment**
- OS: [e.g., Ubuntu 22.04, Windows 11]
- Python version: [e.g., 3.11.0]
- Package version: [e.g., 0.1.0]

**Additional context**
Any other relevant information.
```

#### Feature Requests

Use the feature request template:

```markdown
**Problem Description**
What problem does this feature solve?

**Proposed Solution**
Describe your proposed solution.

**Alternatives Considered**
Other solutions you've considered.

**Additional Context**
Use cases, examples, mockups, etc.
```

## Project Structure

```
markov-passgen/
├── src/markov_passgen/          # Source code
│   ├── core/                     # Core components
│   ├── filters/                  # Password filters
│   ├── transformers/             # Text/password transformers
│   ├── visualization/            # Visualization tools
│   └── cli.py                    # CLI interface
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── e2e/                      # End-to-end tests
├── docs/                         # Documentation
├── examples/                     # Example corpus files
├── pyproject.toml               # Project configuration
└── README.md                    # Project overview
```

## Development Phases

See [development-plan.md](development-plan.md) for the complete roadmap.

**Current Status**: Phase 6 complete (Visualization)
**Next**: Phase 7 (Documentation and Polish)

## Recognition

Contributors will be acknowledged in:
- README.md Contributors section
- Release notes
- GitHub contributors page

## Questions?

- **GitHub Discussions**: For questions and discussions
- **GitHub Issues**: For bug reports and feature requests
- **Email**: maintainer@markovpassgen.dev (for security issues)

## License

By contributing to Markov PassGen, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Markov PassGen! 🎉
