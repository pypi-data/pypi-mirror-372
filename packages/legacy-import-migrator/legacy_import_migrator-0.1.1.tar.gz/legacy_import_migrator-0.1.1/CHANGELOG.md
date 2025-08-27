# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-08-27

### Added
- `__main__.py` module for `python -m legacy_import_migrator` execution support
- Comprehensive CI integration guide with examples for GitHub Actions, GitLab, Jenkins, CircleCI
- Feedback loop infrastructure for continuous improvement
- Automated CI failure tracking workflow
- Detailed troubleshooting documentation

### Fixed
- CLI PATH issues in CI environments - now supports multiple execution methods
- Windows UTF-8 encoding problems with proper environment variable guidance
- Module import errors when using `python -m` execution

### Improved
- CI integration reliability with three different execution methods
- Documentation with real-world CI examples and best practices
- Error messages and troubleshooting guidance
- Feedback collection system for continuous improvement

### Documentation
- Added `examples/ci-integration.md` with platform-specific examples
- Created `docs/FEEDBACK_LOOP_PROCESS.md` for operational excellence
- Established `docs/ci-feedback/` directory for issue tracking
- Updated README with improved installation instructions

## [0.1.0] - 2025-08-27

### Initial Release
- AST-based legacy import detection
- CLI commands: `scan`, `check`, `baseline`
- JSON v1.0 output schema
- Git integration with changed file detection
- Cross-platform support (Linux, macOS, Windows)
- Flexible allowlist patterns
- CI/CD optimized design
- Progress tracking with baseline system
- Comprehensive test suite with >90% coverage
- Full documentation and examples

---

[0.1.1]: https://github.com/strataregula/legacy-import-migrator/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/strataregula/legacy-import-migrator/releases/tag/v0.1.0