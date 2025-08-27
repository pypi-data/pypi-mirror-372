# Quick Reference Card

Legacy Import Migration Toolkit 運用クイックリファレンス

**印刷推奨** - 日常運用での手元参考用

---

## 🚨 緊急時コマンド

### **Critical Bug Hotfix**
```bash
# 1. 緊急branch
git checkout -b hotfix/critical-bug-fix

# 2. 修正・テスト・コミット
pytest tests/ -k "related_test"
git commit -m "hotfix: critical fix for #X"

# 3. 緊急リリース
git checkout master && git merge hotfix/critical-bug-fix
# version bump in pyproject.toml
git commit -m "chore: emergency release v0.1.X"
git tag v0.1.X && git push origin master v0.1.X
python -m build && python -m twine upload --disable-progress-bar dist/*
```

### **Security Issue**
```bash
# Private fix → Coordinated disclosure
git checkout -b security/fix-CVE-YYYY-XXXX
# 修正・テスト後
python -m build && python -m twine upload dist/*
gh security-advisory create --severity high
```

---

## 📅 定期メンテナンス

### **週次チェック (5分)**
```bash
gh repo view strataregula/legacy-import-migrator
gh run list --limit 5
gh issue list --label "priority:high,priority:critical"
```

### **月次メンテナンス (30分)**
```bash
# Dependabot PR処理
gh pr list --author app/dependabot
gh pr merge [PR] --squash

# Stats確認
gh api repos/strataregula/legacy-import-migrator/traffic/views
```

---

## 📦 リリースコマンド

### **PATCH (Bug Fix)**
```bash
# version bump: 0.1.0 → 0.1.1
git commit -m "chore: bump version to 0.1.1"
git tag v0.1.1 && git push origin master v0.1.1
python -m build && python -m twine upload --disable-progress-bar dist/*
gh release create v0.1.1 --generate-notes
```

### **MINOR (New Features)**
```bash
# version bump: 0.1.0 → 0.2.0  
# Update: pyproject.toml, CHANGELOG.md, README.md
git commit -m "chore: release v0.2.0 with new features"
git tag v0.2.0 && git push origin master v0.2.0
python -m build && python -m twine upload --disable-progress-bar dist/*
gh release create v0.2.0 --notes-file CHANGELOG.md
```

---

## 🐛 Issue Management

### **Priority Labels**
- `priority:critical` - Security, Data loss, CI down
- `priority:high` - Function broken, Performance issue  
- `priority:medium` - Enhancement, UX improvement
- `priority:low` - Nice-to-have, Optimization

### **Response Templates**

**Bug Report**
```markdown
Thanks for the detailed report! 🐛
I've reproduced the issue. Root cause: [explanation]
Fix expected in v0.1.x within [timeframe].
Workaround: [steps]
```

**Feature Request**  
```markdown
Thanks for the suggestion! 🚀
Interesting use case for [scenario].
Adding to v0.x.0 backlog. Implementation: [approach]
Interested in contributing?
```

---

## 📊 Health Check Commands

### **GitHub Status**
```bash
gh api repos/strataregula/legacy-import-migrator | jq '.stargazers_count'
gh issue list --state open | wc -l
gh run list --status failure --limit 3
```

### **PyPI Status**
```bash
pip show legacy-import-migrator
# Check: https://pypistats.org/packages/legacy-import-migrator
```

### **world-simulation CI Status**
```bash
cd /c/Users/uraka/project/world-simulation
gh run list --limit 3
gh run view --log | grep -i "legacy\|lim"
```

---

## 🔧 Testing Commands

### **Pre-Release Tests**
```bash
pytest tests/ -v
python -c "from legacy_import_migrator.cli import main; main(['--version'])"
pip-audit  # Security scan
```

### **Integration Test**
```bash
# Test CLI functionality
lim --help
lim scan --legacy-patterns "test" --help
echo "import test" | lim check --legacy-patterns "test"
```

---

## 📁 Key File Locations

### **Version Management**
- `pyproject.toml` - Package version
- `src/legacy_import_migrator/__init__.py` - Code version

### **Documentation**  
- `README.md` - Main documentation
- `CHANGELOG.md` - Version history
- `docs/MAINTENANCE_GUIDE.md` - Full maintenance docs

### **Configuration**
- `.github/dependabot.yml` - Auto-updates
- `.github/workflows/ci.yml` - CI pipeline
- `.github/ISSUE_TEMPLATE/` - Issue templates

---

## 🌐 Important URLs

### **Package Management**
- **PyPI**: https://pypi.org/project/legacy-import-migrator/
- **GitHub**: https://github.com/strataregula/legacy-import-migrator
- **Stats**: https://pypistats.org/packages/legacy-import-migrator

### **Monitoring**
- **CI Status**: https://github.com/strataregula/legacy-import-migrator/actions
- **Issues**: https://github.com/strataregula/legacy-import-migrator/issues
- **Security**: https://github.com/strataregula/legacy-import-migrator/security

---

## ⚡ Common Issues & Solutions

### **Build Fails**
```bash
# Clean build
rm -rf dist/ build/ *.egg-info/
python -m build
```

### **Upload Fails**
```bash
# Check credentials
python -m twine check dist/*
# Windows encoding fix
set PYTHONIOENCODING=UTF-8
python -m twine upload --disable-progress-bar dist/*
```

### **CI Fails**
```bash
# Local reproduction
pytest tests/ --verbose
ruff check src/
```

---

## 📞 Emergency Contacts

### **Critical Production Issues**
1. **Create Issue**: `gh issue create --title "CRITICAL: [description]" --label priority:critical`
2. **Immediate Action**: Follow hotfix procedure above
3. **Communication**: Update issue every 30min during resolution

### **Security Vulnerabilities**  
1. **Private Report**: GitHub Security Advisory
2. **Immediate Assessment**: Severity evaluation
3. **Coordinated Response**: Private fix → Public disclosure

---

## 📋 Pre-Flight Checklist

### **Before Any Release**
- [ ] All tests pass locally
- [ ] Version number updated
- [ ] CHANGELOG.md updated  
- [ ] Security scan clean
- [ ] world-simulation compatibility verified

### **After Release**
- [ ] PyPI upload confirmed
- [ ] GitHub release created
- [ ] Issues notified
- [ ] world-simulation CI updated

---

**💡 Keep this card handy for quick reference during operations!**

---

*Legacy Import Migration Toolkit Quick Reference v1.0*