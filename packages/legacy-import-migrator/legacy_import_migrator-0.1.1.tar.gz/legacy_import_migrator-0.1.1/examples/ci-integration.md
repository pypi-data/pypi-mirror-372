# CI Integration Examples

Various ways to integrate legacy-import-migrator in CI environments.

## GitHub Actions

### Method 1: Python -m execution (Recommended for v0.1.1+)
```yaml
- name: Install dependencies
  run: |
    pip install legacy-import-migrator

- name: Check legacy imports
  run: |
    python -m legacy_import_migrator check \
      --mode changed \
      --base ${{ github.event.pull_request.base.sha }} \
      --legacy-patterns "^old_module(\.|$)" \
      --allow "tests/legacy/**"
```

### Method 2: Direct CLI (if PATH is configured)
```yaml
- name: Check legacy imports
  run: |
    # May need to add pip install location to PATH
    export PATH="$HOME/.local/bin:$PATH"
    lim check --mode changed --base HEAD~1 --legacy-patterns "old_module"
```

### Method 3: Python script wrapper
```yaml
- name: Check legacy imports
  run: |
    python -c "
    from legacy_import_migrator.cli import main
    import sys
    sys.exit(main())
    " check --mode changed --legacy-patterns "old_module"
```

## GitLab CI

```yaml
legacy_import_check:
  stage: test
  script:
    - pip install legacy-import-migrator
    - python -m legacy_import_migrator check --mode changed --legacy-patterns "old_module"
  only:
    - merge_requests
```

## Jenkins

```groovy
pipeline {
    stages {
        stage('Legacy Import Check') {
            steps {
                sh 'pip install legacy-import-migrator'
                sh 'python -m legacy_import_migrator check --mode changed --legacy-patterns "old_module"'
            }
        }
    }
}
```

## CircleCI

```yaml
version: 2.1
jobs:
  legacy-check:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - run:
          name: Install and run legacy import check
          command: |
            pip install legacy-import-migrator
            python -m legacy_import_migrator check --mode changed --legacy-patterns "old_module"
```

## Docker

```dockerfile
FROM python:3.11-slim

RUN pip install legacy-import-migrator

# Use as base image for CI
ENTRYPOINT ["python", "-m", "legacy_import_migrator"]
```

## Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: legacy-imports
        name: Check legacy imports
        entry: python -m legacy_import_migrator check --mode changed
        language: system
        pass_filenames: false
        args: ['--legacy-patterns', 'old_module']
```

## Shell Script Wrapper

Create a `check-legacy.sh`:
```bash
#!/bin/bash
# CI wrapper for legacy-import-migrator

# Ensure package is installed
pip install -q legacy-import-migrator || exit 1

# Run check with proper error handling
python -m legacy_import_migrator check \
    --mode changed \
    --base "${BASE_COMMIT:-HEAD~1}" \
    --legacy-patterns "${LEGACY_PATTERNS:-old_module}" \
    --allow "${ALLOW_PATTERNS:-tests/legacy/**}" \
    --verbose

# Capture exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ No legacy imports found"
elif [ $EXIT_CODE -eq 2 ]; then
    echo "❌ Legacy imports detected - please fix before merging"
else
    echo "⚠️ Error during legacy import check"
fi

exit $EXIT_CODE
```

## Troubleshooting

### Issue: `lim: command not found`
**Solution**: Use `python -m legacy_import_migrator` instead

### Issue: `ModuleNotFoundError`
**Solution**: Ensure `pip install legacy-import-migrator` succeeded

### Issue: Shallow clone in CI
**Solution**: Use `fetch-depth: 0` in checkout action or configure BASE manually

### Issue: Windows encoding errors
**Solution**: Set environment variable `PYTHONUTF8=1`

## Environment Variables

- `LIM_BASE_REF`: Override base commit detection
- `PYTHONUTF8`: Force UTF-8 encoding (Windows)
- `LIM_DEBUG`: Enable debug output (v0.2.0+)

## Best Practices

1. **Always specify legacy patterns explicitly**
   - Don't rely on defaults
   - Use regex patterns for precision

2. **Use allow patterns for legitimate exceptions**
   - Test directories
   - Documentation examples
   - Migration shims

3. **Run in PR/MR pipelines**
   - Check only changed files for speed
   - Fail pipeline on violations

4. **Monitor trends with JSON output**
   ```bash
   python -m legacy_import_migrator scan \
     --json-out metrics/legacy-imports-$(date +%Y%m%d).json
   ```

5. **Gradual migration**
   - Start with allow patterns
   - Reduce allowlist over time
   - Track progress with baselines