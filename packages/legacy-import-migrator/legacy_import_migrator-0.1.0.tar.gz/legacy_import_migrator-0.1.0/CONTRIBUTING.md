# Contributing to Legacy Import Migration Toolkit

Thank you for your interest in contributing to the Legacy Import Migration Toolkit! 

## 🚀 Quick Setup

```bash
# Clone and setup development environment
git clone https://github.com/strataregula/legacy-import-migrator
cd legacy-import-migrator

# Install in development mode
pip install -e ".[dev]"

# Run tests to verify setup
pytest
```

## 🧪 Development Workflow

### Code Quality

We use several tools to maintain code quality:

```bash
# Linting and formatting
ruff check src tests
ruff format src tests

# Type checking (optional)
mypy src/legacy_import_migrator --ignore-missing-imports

# Testing with coverage
pytest --cov=legacy_import_migrator
```

### Testing

- Write tests for new functionality in `tests/`
- Maintain high test coverage (target: >90%)
- Include both unit tests and integration tests
- Test CLI commands using temporary directories

### CLI Testing

Test CLI commands manually:

```bash
# Test basic functionality
lim --help
lim scan --legacy-patterns "test_pattern" --roots "src"
lim baseline --write --legacy-patterns "test_pattern" --roots "src"
lim check --legacy-patterns "test_pattern" --mode all --roots "src"
```

## 📋 Contribution Guidelines

### Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes
4. **Test** thoroughly (run full test suite)
5. **Commit** with clear messages
6. **Push** to your fork
7. **Open** a pull request

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add support for custom baseline locations
fix: handle Unicode errors in file scanning  
docs: update CLI usage examples
test: add integration tests for checker module
```

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for new code
- Write docstrings for public functions and classes
- Keep functions focused and testable

## 🎯 Areas for Contribution

### High Priority
- Performance improvements for large codebases
- Additional output formats (YAML, CSV)
- Integration with more CI systems
- Enhanced error messages and diagnostics

### Medium Priority  
- Plugin system for custom legacy patterns
- Interactive migration assistance
- Web dashboard for progress visualization
- Support for other programming languages

### Documentation
- More usage examples
- Migration strategy guides
- Troubleshooting documentation
- Video tutorials

## 🔧 Technical Architecture

### Core Components

- **`tracker.py`**: Main scanning and progress tracking logic
- **`checker.py`**: CI-oriented legacy import checking  
- **`cli/`**: Command-line interface implementations

### Key Design Principles

1. **AST-based**: Precise import detection using Python AST
2. **Git-integrated**: Leverage Git for change detection
3. **CI-friendly**: Designed for automation and scripting
4. **Schema-stable**: v1 JSON output format is contractual

### Adding New Features

When adding features, consider:

- **Backward compatibility**: Don't break existing JSON schema
- **Performance**: Large codebases should scan efficiently  
- **Cross-platform**: Support Windows, macOS, and Linux
- **Error handling**: Graceful degradation with helpful messages

## 🐛 Bug Reports

When reporting bugs, please include:

- Python version and OS
- Complete command that failed
- Full error message and traceback
- Sample repository structure (if relevant)

## 💡 Feature Requests

For new features, please describe:

- **Use case**: What problem does it solve?
- **Scope**: How broad is the feature?
- **Examples**: Concrete usage examples
- **Alternatives**: Other solutions considered

## 📞 Questions?

- Open an issue for questions about usage
- Check existing issues before creating new ones
- Use clear, descriptive titles

## 📜 License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

---

**Thank you for helping make legacy import migration easier for everyone!** 🎉