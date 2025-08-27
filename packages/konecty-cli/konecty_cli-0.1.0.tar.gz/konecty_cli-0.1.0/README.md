# Konecty CLI

A command-line interface for Konecty utilities.

### Using uvx (Recommended)

You can run the CLI directly using `uvx`:

```bash
uvx konecty-cli --help
```

## Development

This project uses Make to manage dev scripts. You can list available development commands with `make help`

### Setup Development Environment

Install development dependencies:

```bash
make install-dev
```

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov
```

### Code Quality

The project uses several tools to maintain code quality:

- **Black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting
- **mypy** - Type checking

Run all checks:

```bash
# Run all quality checks (format, lint, type-check, test)
make check

# Or run individual checks:
make format    # Format code with black and isort
make lint      # Run flake8 linter
make type-check # Run mypy type checker
```

### Building and Publishing

```bash
# Build the package
make build

# Clean build artifacts
make clean
```
