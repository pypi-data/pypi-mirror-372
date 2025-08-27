# Legacy Import Migration Toolkit (LIM)

AST-based legacy import tracking and migration toolkit for Python codebases undergoing namespace migrations.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)

## 🚀 Quick Start (5 minutes)

### Installation

```bash
# Via pip
pip install legacy-import-migrator

# Via pipx (recommended)
pipx install legacy-import-migrator

# Development installation
git clone https://github.com/strataregula/legacy-import-migrator
cd legacy-import-migrator
pip install -e .
```

### Basic Usage

```bash
# 1. Scan all files for legacy imports
lim scan --legacy-patterns "old_module,legacy_pkg" --json-out .cache/migration.json

# 2. Create baseline for progress tracking
lim baseline --write --legacy-patterns "old_module,legacy_pkg"

# 3. Check changed files in CI (exits with code 2 if violations found)
lim check --legacy-patterns "old_module,legacy_pkg"

# 4. Track progress over time
lim scan --scope changed --legacy-patterns "old_module,legacy_pkg" --fail-when-blocking
```

### CI Integration (GitHub Actions)

```yaml
# .github/workflows/legacy-imports.yml
name: Check Legacy Imports
on: [pull_request]

jobs:
  check-imports:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Required for changed file detection
          
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
          
      - run: pip install legacy-import-migrator
      
      - name: Check for legacy imports
        run: |
          lim check --legacy-patterns "old_module,legacy_namespace" \
                    --allow "tests/legacy/**" \
                    --allow "docs/examples/**"
```

## 📊 Features

- **AST-based scanning**: Precisely detects import statements, ignoring comments and strings
- **Progress tracking**: Baseline system to measure migration progress over time  
- **CI integration**: Designed for automated checking in CI/CD pipelines
- **Flexible allowlists**: Support for glob patterns and inline `LEGACY-ALLOW` markers
- **Cross-platform**: Works on Linux, macOS, and Windows
- **Rich output**: Both human-readable and JSON output formats
- **Git integration**: Automatic base commit detection for changed file analysis

## 📋 Commands

### `lim scan` - Scan for Legacy Imports

Comprehensive scanning with progress tracking:

```bash
lim scan --legacy-patterns "old_pkg,legacy_module" \
         --scope all \
         --roots "src,tests" \
         --allow "tests/legacy/**" \
         --json-out .cache/migration.json \
         --print-files
```

**Options:**
- `--scope`: `all` (scan everything) or `changed` (changed files only)
- `--base`: Base commit for changed file detection (default: auto)
- `--roots`: Comma-separated search directories (default: `src,tests`)
- `--legacy-patterns`: **Required** - Legacy import patterns to track
- `--allow`: Allow patterns (can be used multiple times)
- `--json-out`: Output results to JSON file
- `--fail-when-blocking`: Exit with code 2 if blocking imports found
- `--print-files`: Show files with blocking imports

### `lim check` - CI-Oriented Checking  

Lightweight checking for CI environments:

```bash
lim check --legacy-patterns "old_pkg,legacy_module" \
          --mode changed \
          --allow "tests/legacy/**"
```

**Options:**
- `--mode`: `changed` (default) or `all`
- `--base`: Base commit for changed files (default: auto)
- `--legacy-patterns`: **Required** - Legacy patterns to check
- `--allow`: Allow patterns for exceptions
- `--allow-marker`: Inline marker for exceptions (default: `LEGACY-ALLOW`)

### `lim baseline` - Baseline Management

Create and manage migration baselines:

```bash
# Create new baseline
lim baseline --write --legacy-patterns "old_pkg,legacy_module"

# View current baseline
lim baseline --legacy-patterns "old_pkg,legacy_module"
```

## 📄 JSON Output Schema (v1)

The `--json-out` option produces stable JSON output for CI integration and dashboards:

```json
{
  "version": "1.0",
  "repo_root": "/path/to/repo",
  "scope": "all|changed", 
  "files_scanned": 150,
  "imports": {
    "blocking": 23,
    "allowed": 5,
    "total": 28,
    "baseline_blocking": 50,
    "progress_percent": 54.0
  },
  "blocking_by_file": [
    ["src/main.py", 8],
    ["src/utils.py", 5]
  ],
  "baseline": {
    "file": ".cache/migration_baseline.json",
    "commit": "abc123def"
  }
}
```

**Schema Stability**: This v1 schema is **contractually stable**. Any breaking changes will use v2 with different version identifier.

## 🛠️ Configuration Patterns

### Allow Patterns

Support for flexible exception handling:

```bash
# Glob patterns
--allow "tests/legacy/**"           # All files under tests/legacy/
--allow "tests/**/test_*legacy*.py" # Legacy-specific test files
--allow "docs/examples/**"          # Documentation examples

# Multiple patterns
lim scan --allow "pattern1" --allow "pattern2" --legacy-patterns "old_pkg"

# Inline markers in files
# Add LEGACY-ALLOW comment to any file:
```

```python
# This file intentionally uses legacy imports: LEGACY-ALLOW
from old_module import legacy_function
```

### Common Legacy Patterns

```bash
# Single module
--legacy-patterns "old_module"

# Multiple modules  
--legacy-patterns "old_pkg,legacy_module,deprecated_utils"

# With src prefix (common in older codebases)
--legacy-patterns "src.old_module,old_module"
```

## 🔧 Troubleshooting

### Shallow Git Repositories

**Issue**: `Cannot compute BASE for --scope changed. Repository may be shallow`

**Solution**: 
```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0  # Fetch full history
```

Or fetch specific branch:
```bash
git fetch --no-tags --prune origin +refs/heads/main:refs/remotes/origin/main
```

### Missing Origin Remote

**Issue**: Base commit detection fails in local repositories

**Solution**: The tool automatically falls back to recent commit history. For explicit control:
```bash
lim scan --base HEAD~1 --scope changed
```

### Windows UTF-8 Issues

**Issue**: Unicode characters in output or file names

**Solution**: Set environment variable:
```bash
set PYTHONIOENCODING=UTF-8
```

Or use UTF-8 mode:
```bash 
set PYTHONUTF8=1
```

## 🎯 Migration Strategy

### 1. Establish Baseline
```bash
# Scan current state and set baseline
lim baseline --write --legacy-patterns "old_module"
```

### 2. Monitor Progress
```bash
# Regular progress scans
lim scan --legacy-patterns "old_module" --json-out reports/migration-$(date +%Y%m%d).json
```

### 3. Prevent Regressions  
```bash
# In CI: fail if new legacy imports introduced
lim check --legacy-patterns "old_module"
```

### 4. Track Completion
- Monitor `progress_percent` in JSON output
- Target: `blocking: 0` for migration completion
- Archive baseline once migration is complete

## 🚀 Advanced Usage

### Dashboard Integration

Use JSON output to build migration dashboards:

```bash
# Generate daily reports
lim scan --legacy-patterns "old_pkg" --json-out "reports/$(date +%Y%m%d)-migration.json"

# CI artifact collection  
lim scan --json-out migration-report.json
# Upload migration-report.json as CI artifact
```

### Custom Baseline Location

```bash
lim scan --baseline-file ".migration/custom-baseline.json" --legacy-patterns "old_pkg"
```

### Verbose Analysis

```bash
lim scan --verbose --print-files --legacy-patterns "old_pkg"
```

## 📈 Extensibility

The toolkit is designed for extension:

- **Custom patterns**: Easy addition of new legacy pattern types
- **Output formats**: JSON schema designed for dashboard integration  
- **CI integration**: Exit codes and output designed for automation
- **Baseline strategies**: Flexible baseline management for different workflows

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📜 License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by the Legacy Import Migrator Team**