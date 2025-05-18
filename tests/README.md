# Markdown Decision Process Test Suite

This directory contains the test suite for the Markdown Decision Process (MDP) package.

## Running Tests

The `run_all_tests.py` script is an enhanced test runner that provides several useful features beyond standard pytest functionality. It helps work around various issues that may arise during testing, such as import errors.

### Basic Usage

```bash
# Run all tests
python3 run_all_tests.py

# Run tests with verbose output
python3 run_all_tests.py -v 2

# List available test modules
python3 run_all_tests.py --list
```

### Focused Testing

To focus on specific tests:

```bash
# Run tests for a specific module
python3 run_all_tests.py --module document

# Skip known failing tests
python3 run_all_tests.py --skip-failing

# Run only tests expected to succeed
python3 run_all_tests.py --only-successful
```

### Handling Import Issues

If you encounter import errors when running tests, you can use the `--fix-imports` flag to automatically fix common import issues:

```bash
python3 run_all_tests.py --fix-imports
```

This creates temporary versions of test files with corrected imports to allow tests to run even if the original imports don't match the current codebase structure.

### Other Features

```bash
# Install the package in development mode before running tests
python3 run_all_tests.py --develop

# Generate a test coverage report
python3 run_all_tests.py --coverage

# Show environment information
python3 run_all_tests.py --env-info

# Run with debug output
python3 run_all_tests.py --debug
```

## Test Structure

Each test file in this directory follows the naming convention `test_*.py` and tests a specific module or functionality of the MDP package.

## Known Issues

Some tests might fail due to:

1. Missing modules or imports
2. Changes in the API since tests were written
3. Expectations in tests that don't match current implementation

Use the `--skip-failing` flag to skip known problematic tests.

## Getting Help

To see all available options:

```bash
python3 run_all_tests.py --help
``` 