## 🔍 LIM Battle Test Purpose
Verify legacy-import-migrator CI behavior on world-simulation.

## What Changed
- Added intentional legacy imports to test LIM detection
- Added infrastructure for LIM validation workflows

## Validation Checklist
- [ ] CI job fails with `blocking findings: N` and exits with code 1
- [ ] JSON v1.0 schema generated correctly (`"version": "1.0"`)
- [ ] Allowlist properly excludes `tests/namespace/**` paths
- [ ] Shallow clone handling works (`fetch-depth: 0`)
- [ ] Windows/UTF-8 handling robust (no encoding crashes)
- [ ] Remove violations → CI turns green ✅

## Expected Behavior
**Phase 1 (This PR)**: CI should **FAIL RED** 🔴  
**Phase 2 (Follow-up)**: Remove violations → CI should **PASS GREEN** ✅

## LIM Command Reference
```bash
# Local testing
lim check --scope changed \
  --legacy-patterns "^simroute_core(\.|$)" \
  --legacy-patterns "^simroute_adapters(\.|$)" \
  --allow "tests/namespace/**" \
  --json-out lim-report.json \
  --fail-when-blocking

# View results  
cat lim-report.json | jq '.summary'
```

## Next Phase
After CI failure confirmation → remove violations → verify green → PyPI publication ready