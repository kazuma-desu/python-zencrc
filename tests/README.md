# ZenCRC Tests

This directory contains tests for the ZenCRC package.

## Test Structure

- `unit/`: Unit tests for individual components
  - `test_crc32.py`: Tests for the core CRC32 functionality
  - `test_zencrc_cli.py`: Tests for the command-line interface

## Running Tests

You can run the tests using pytest:

```bash
# Install test dependencies
pip install -e ".[test]"

# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_crc32.py

# Run with coverage report
pytest --cov=zencrc --cov-report=term --cov-report=html
```

The coverage report will be generated in the `htmlcov/` directory.

## Test Configuration

The test configuration is defined in `pytest.ini` and `pyproject.toml`. The configuration includes:

- Test discovery patterns
- Coverage reporting
- Verbosity settings

## Adding New Tests

When adding new tests:

1. Follow the naming convention: `test_*.py` for test files, `Test*` for test classes, and `test_*` for test functions
2. Place unit tests in the `unit/` directory
3. Use appropriate assertions and mocks
4. Run the tests to ensure they pass before committing
