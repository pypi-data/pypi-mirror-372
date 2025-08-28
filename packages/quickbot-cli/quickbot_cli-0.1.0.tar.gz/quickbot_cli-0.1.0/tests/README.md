<!--
SPDX-FileCopyrightText: 2025 Alexander Kalinovsky <a@k8y.ru>

SPDX-License-Identifier: Apache-2.0
-->

# CLI Tests

This directory contains comprehensive tests for the QuickBot CLI functionality.

## Test Structure

### `conftest.py`
Contains pytest fixtures and configuration:
- `cli_runner`: Typer CLI test runner
- `temp_dir`: Temporary directory for testing
- `mock_template_dir`: Mock template directory structure
- `mock_typer_prompt`: Mock for typer.prompt to avoid interactive input
- `mock_typer_secho`: Mock for typer.secho output
- `mock_typer_echo`: Mock for typer.echo output
- `mock_subprocess_run`: Mock for subprocess.run

### `test_cli.py`
Core unit tests covering:
- Template specification loading
- Variable prompting and validation
- Template file rendering
- Post-task execution
- Optional module inclusion/exclusion
- CLI command functionality
- Help and argument parsing

### `test_integration.py`
Integration tests covering:
- Full project generation workflow
- Module inclusion/exclusion scenarios
- Overwrite functionality
- End-to-end CLI operations

### `test_edge_cases.py`
Edge case and error handling tests:
- Boundary conditions
- Error scenarios
- Malformed input handling
- Deep nesting and large files

## Running Tests

### Using pytest directly
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/quickbot_cli --cov-report=html

# Run specific test file
pytest tests/test_cli.py

# Run specific test class
pytest tests/test_cli.py::TestLoadTemplateSpec

# Run specific test method
pytest tests/test_cli.py::TestLoadTemplateSpec::test_load_template_spec_with_valid_file
```

### Using the test runner script
```bash
python run_tests.py
```

### Using development dependencies
```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest
```

## Test Coverage

The test suite covers:

- **Template Loading**: YAML parsing, error handling, default values
- **Variable Handling**: Interactive prompts, validation, choices, regex
- **File Rendering**: Jinja2 templating, binary files, directory structure
- **Post Tasks**: Conditional execution, subprocess handling, error recovery
- **Optional Modules**: Alembic and Babel inclusion/exclusion
- **CLI Interface**: Command parsing, help, arguments, error handling
- **Integration**: End-to-end workflows, file operations, edge cases

## Adding New Tests

When adding new tests:

1. **Unit Tests**: Add to appropriate test class in `test_cli.py`
2. **Integration Tests**: Add to `test_integration.py`
3. **Edge Cases**: Add to `test_edge_cases.py`
4. **Fixtures**: Add to `conftest.py` if reusable

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Test Documentation
Each test should have a descriptive docstring explaining what it tests and why.

## Mocking Strategy

- **External Dependencies**: Use `unittest.mock.patch` for file system, subprocess, etc.
- **User Input**: Mock `typer.prompt` to avoid interactive input during tests
- **Output**: Mock `typer.secho` and `typer.echo` to capture and verify output
- **File Operations**: Use temporary directories to avoid affecting the real file system

## Continuous Integration

Tests are configured to run with:
- Coverage reporting (HTML, XML, terminal)
- Strict marker validation
- Verbose output for debugging
- Short traceback format for readability
