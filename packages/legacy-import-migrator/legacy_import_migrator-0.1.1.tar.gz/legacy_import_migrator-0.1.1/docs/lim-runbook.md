# Legacy Import Migrator (LIM) Runbook

## Overview
LIM prevents introduction of legacy imports (`simroute_core.*`, `simroute_adapters.*`) during development.

## Expected Workflow
1. **PR Created** → LIM runs automatically
2. **Violations Found** → CI fails with clear error message
3. **Developer Fixes** → Update imports to new namespace
4. **CI Passes** → PR can be merged

## Common Commands

### Local Testing
```bash
# Check changed files
lim check --scope changed \
  --legacy-patterns "^simroute_core(\.|$)" \
  --legacy-patterns "^simroute_adapters(\.|$)" \
  --allow "tests/namespace/**" \
  --fail-when-blocking

# Full repository scan
lim scan --scope all --json-out full-report.json

# View baseline status
lim baseline --legacy-patterns "^simroute_core(\.|$)"
```

### Troubleshooting

**Issue**: `Cannot compute merge-base`  
**Solution**: Ensure full git history: `git fetch --unshallow`

**Issue**: False positives in tests  
**Solution**: Add to allowlist: `--allow "tests/legacy/**"`

**Issue**: Custom base commit needed  
**Solution**: Set environment: `export LIM_BASE_REF=v1.0.0`

## Migration Progress
- **Target**: `blocking: 0` (100% migration complete)
- **Current**: Check latest CI report or run `lim scan --scope all`
- **Baseline**: Tracked in `.cache/migration_baseline.json`

## Red → Green Process
1. **Identify violations**: Check CI logs or run `lim check --json-out report.json`
2. **Fix imports**: Update to new namespace (e.g., `simroute_core` → `simroute.core`)
3. **Verify locally**: Run `lim check --scope changed --fail-when-blocking`
4. **Push changes**: CI should turn green