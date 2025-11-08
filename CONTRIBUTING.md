# Contributing to PostgreSQL DataLoader

First off, thank you for considering contributing to PostgreSQL DataLoader! It's people like you that make this tool better for everyone.

## Code of Conduct

This project and everyone participating in it is governed by respect, professionalism, and inclusivity. By participating, you are expected to uphold these values.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Bug Report Template:**
```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Environment:**
 - OS: [e.g. Windows 10, Ubuntu 20.04]
 - Python Version: [e.g. 3.9.0]
 - PostgreSQL Version: [e.g. 13.4]
 - Package Version: [e.g. 1.0.0]

**Additional context**
Add any other context about the problem here.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- Use a clear and descriptive title
- Provide a detailed description of the suggested enhancement
- Explain why this enhancement would be useful
- List any similar features in other tools (if applicable)

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code, add tests
3. Ensure the test suite passes
4. Make sure your code follows the existing style
5. Write a clear commit message
6. Update documentation as needed

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/postgresql-dataloader.git
cd postgresql-dataloader
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

### 4. Set Up Database

```bash
# Create a test database
createdb test_postgresql_dataloader

# Copy environment template
cp .env.example .env

# Edit .env with your test database credentials
```

### 5. Run Tests

```bash
pytest tests/  # If tests are available
python examples/basic_usage.py  # Test basic functionality
```

## Style Guidelines

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- Line length: 100 characters (not 79)
- Use 4 spaces for indentation
- Use docstrings for all public functions
- Use type hints where appropriate

### Example:

```python
def my_function(param1: str, param2: int = 5) -> bool:
    """
    Brief description of function.

    Detailed description if needed.

    Args:
        param1 (str): Description of param1.
        param2 (int, optional): Description of param2. Defaults to 5.

    Returns:
        bool: Description of return value.

    Example:
        >>> my_function("test", 10)
        True
    """
    # Implementation
    return True
```

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests liberally

**Good Examples:**
```
Add support for PostgreSQL arrays
Fix connection timeout issue (#123)
Update documentation for create_table_from_dataframe
Refactor data type mapping logic
```

## Project Structure

```
postgresql-dataloader/
├── src/
│   └── postgresql_dataloader.py  # Main module
├── data/
│   ├── sample_customer_demographics.csv
│   └── sample_customer_transactions.csv
├── examples/
│   ├── basic_usage.py
│   └── advanced_operations.py
├── docs/
│   └── API_DOCUMENTATION.md
├── tests/                         # Unit tests (to be added)
│   ├── test_connection.py
│   ├── test_table_operations.py
│   └── test_data_operations.py
├── .gitignore
├── .env.example
├── requirements.txt
├── LICENSE
├── README.md
├── CONTRIBUTING.md
└── setup.py                       # To be added
```

## Areas for Contribution

We especially welcome contributions in these areas:

### High Priority
- [ ] Unit tests and test coverage
- [ ] Support for JSON and JSONB data types
- [ ] Connection pooling
- [ ] Async operations support
- [ ] CLI tool implementation

### Medium Priority
- [ ] Additional database dialects (MySQL, SQLite)
- [ ] Query builder functionality
- [ ] Data migration tools
- [ ] Performance benchmarks
- [ ] Docker containerization

### Documentation
- [ ] More usage examples
- [ ] Video tutorials
- [ ] API reference improvements
- [ ] Troubleshooting guide
- [ ] Best practices guide

## Testing Guidelines

### Writing Tests

```python
import unittest
from src.postgresql_dataloader import get_connection

class TestConnection(unittest.TestCase):
    def test_connection_success(self):
        """Test successful database connection"""
        conn = get_connection()
        self.assertIsNotNone(conn)
        conn.close()

    def test_connection_failure(self):
        """Test connection with invalid credentials"""
        conn = get_connection(
            host="invalid_host",
            database="invalid_db"
        )
        self.assertIsNone(conn)
```

### Test Coverage

We aim for:
- Minimum 80% code coverage
- All public functions tested
- Edge cases covered
- Error handling tested

## Documentation Guidelines

### Docstring Format

```python
def function_name(param1: type, param2: type) -> return_type:
    """
    Brief one-line description.

    Longer description if needed. Can span multiple lines.
    Explain what the function does, not how it does it.

    Args:
        param1 (type): Description of param1.
        param2 (type): Description of param2.

    Returns:
        return_type: Description of return value.

    Raises:
        ExceptionType: When and why this exception is raised.

    Example:
        >>> function_name("value1", 42)
        expected_result

    Note:
        Any important notes or warnings.
    """
    pass
```

### README Updates

When adding new features:
1. Update the Features section
2. Add to Table of Contents if needed
3. Include usage examples
4. Update API Reference if applicable

## Release Process

1. Update version in `setup.py` and `__init__.py`
2. Update CHANGELOG.md
3. Create a release branch
4. Run full test suite
5. Create pull request to main
6. Tag release after merge
7. Publish to PyPI (maintainers only)

## Getting Help

- **Documentation:** Check [README.md](README.md) and [docs/](docs/)
- **Examples:** See [examples/](examples/)
- **Issues:** Browse or create [GitHub Issues](https://github.com/yourusername/postgresql-dataloader/issues)
- **Discussions:** Join [GitHub Discussions](https://github.com/yourusername/postgresql-dataloader/discussions)

## Recognition

Contributors will be recognized in:
- README.md Contributors section
- Release notes
- CONTRIBUTORS.md file

Thank you for contributing to PostgreSQL DataLoader! 🎉
