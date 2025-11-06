# Contributing to Mem-Layer

Thank you for your interest in contributing to Mem-Layer! This document provides guidelines and instructions for contributing.

## Getting Started

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/mem-layer.git
   cd mem-layer
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Verify Installation**
   ```bash
   pytest
   mem-layer --version
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

- Write clean, readable code
- Follow existing code style
- Add tests for new features
- Update documentation

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mem_layer --cov-report=html

# Run specific test file
pytest tests/unit/test_node.py

# Run specific test
pytest tests/unit/test_node.py::test_node_creation
```

### 4. Code Quality

```bash
# Format code
black src/ tests/

# Type checking
mypy src/

# Linting
ruff check src/
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Maintenance tasks

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Coding Standards

### Python Style

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use meaningful variable names
- Add docstrings to all public functions/classes

### Example

```python
def create_node(
    self,
    type: NodeType,
    content: str,
    tags: list[str] | None = None,
) -> Node:
    """Create a new node in the graph.

    Args:
        type: Type of node to create
        content: Node content
        tags: Optional list of tags

    Returns:
        Created node object

    Raises:
        ValidationException: If node data is invalid
    """
    if not content:
        raise ValidationException("Content cannot be empty")

    node = Node(type=type, content=content, tags=tags or [])
    return node
```

### Testing

- Write tests for all new features
- Aim for >90% test coverage
- Use descriptive test names
- Follow AAA pattern: Arrange, Act, Assert

```python
def test_node_creation():
    """Test creating a node with valid data."""
    # Arrange
    content = "Test node"
    tags = ["test"]

    # Act
    node = Node(type=NodeType.ENTITY, scope="test", content=content, tags=tags)

    # Assert
    assert node.content == content
    assert "test" in node.tags
```

## Project Structure

```
mem-layer/
├── src/mem_layer/          # Source code
│   ├── core/               # Core graph engine
│   ├── scope/              # Scope management
│   ├── persistence/        # Database layer
│   ├── query/              # Query engine
│   ├── cli/                # Command-line interface
│   └── utils/              # Utilities
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── fixtures/           # Test fixtures
├── examples/               # Example scripts
└── docs/                   # Documentation
```

## Adding New Features

### 1. Core Features

For core functionality (graph operations, persistence, etc.):

1. Add implementation in appropriate module
2. Add tests in `tests/unit/`
3. Update API if needed
4. Update CLI if needed
5. Update documentation

### 2. CLI Commands

To add a new CLI command:

1. Add command to `src/mem_layer/cli/main.py`
2. Use Click decorators
3. Add rich formatting for output
4. Add tests
5. Update CLI documentation

### 3. Node/Edge Types

To add a new node or edge type:

1. Add to enum in `src/mem_layer/core/node.py` or `edge.py`
2. Update documentation
3. Add tests
4. Consider if CLI needs updating

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def function(param1: str, param2: int) -> bool:
    """Short description of function.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
    """
```

### README Updates

When adding features:
- Update feature list in README.md
- Add usage examples
- Update quickstart if needed

### Architecture Updates

For significant changes:
- Update ARCHITECTURE.md
- Add diagrams if helpful
- Document design decisions

## Pull Request Process

1. **Title**: Clear, descriptive title
2. **Description**:
   - What changes were made
   - Why they were made
   - How to test them
3. **Tests**: All tests must pass
4. **Documentation**: Updated if needed
5. **Review**: Address review comments

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
How to test these changes

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] All tests pass
```

## Reporting Issues

### Bug Reports

Include:
- Mem-Layer version
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

### Feature Requests

Include:
- Use case
- Proposed solution
- Alternative solutions considered
- Additional context

## Community

- Be respectful and inclusive
- Help others when possible
- Provide constructive feedback
- Follow the code of conduct

## Questions?

- Open a discussion on GitHub
- Check existing issues
- Read the documentation

Thank you for contributing to Mem-Layer!
