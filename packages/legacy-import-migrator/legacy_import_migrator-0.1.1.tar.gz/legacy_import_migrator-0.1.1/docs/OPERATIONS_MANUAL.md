# Operations Manual

Legacy Import Migration Toolkit 運用マニュアル

**対象**: メンテナー、運用担当者  
**目的**: 日常運用、緊急対応、リリース作業の実行手順

---

## 🔧 日常運用

### **週次チェック (5分 / 毎週月曜)**

#### **1. ヘルスチェック**
```bash
# GitHub repo 確認
gh repo view strataregula/legacy-import-migrator

# CI status 確認
gh run list --limit 5

# Security alerts 確認
gh api repos/strataregula/legacy-import-migrator/security-advisories
```

#### **2. Issue/PR トリアージ**
```bash
# 新しいissue確認
gh issue list --state open --limit 10

# Critical/High priority issue確認  
gh issue list --label "priority:high,priority:critical"

# 古いissue確認 (30日以上)
gh issue list --state open | grep "30 days"
```

#### **3. world-simulation CI確認**
```bash
cd /c/Users/uraka/project/world-simulation

# 最新CI実行確認
gh run list --limit 3

# legacy-import関連エラー確認
gh run view --log | grep -i "legacy\|lim\|import"
```

### **月次メンテナンス (30分 / 毎月第1月曜)**

#### **1. Dependabot PR処理**
```bash
cd /c/Users/uraka/project/legacy-import-migrator

# Dependabot PR一覧
gh pr list --author app/dependabot

# 各PRレビュー・マージ
gh pr view [PR番号] --comments
gh pr merge [PR番号] --squash  # テスト通過確認後
```

#### **2. 依存関係手動チェック**
```bash
# 現在の依存関係
pip show legacy-import-migrator

# 利用可能アップデート確認
pip list --outdated

# セキュリティチェック
pip-audit
```

#### **3. Stats確認**
```bash
# PyPI download stats (外部ツール)
# https://pypistats.org/packages/legacy-import-migrator

# GitHub traffic確認
gh api repos/strataregula/legacy-import-migrator/traffic/views
gh api repos/strataregula/legacy-import-migrator/traffic/clones
```

---

## 📦 リリース作業

### **PATCH リリース (v0.1.x) - バグフィックス**

#### **事前準備**
```bash
cd /c/Users/uraka/project/legacy-import-migrator

# 最新状態確認
git status
git pull origin master

# テスト実行
pytest tests/ -v
python -c "from legacy_import_migrator.cli import main; main(['--version'])"
```

#### **バージョン更新**
```bash
# pyproject.toml編集
# version = "0.1.1"  # 現在のバージョンから+1

# バージョン確認
grep version pyproject.toml
```

#### **リリース実行**
```bash
# コミット・タグ
git add pyproject.toml
git commit -m "chore: bump version to 0.1.1"
git tag -a v0.1.1 -m "Release v0.1.1: Bug fixes and improvements

- Fix issue #X: Description
- Improve error handling in Y
- Update dependencies

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# プッシュ
git push origin master
git push origin v0.1.1

# ビルド・アップロード
python -m build
python -m twine upload --disable-progress-bar dist/*

# GitHub Release作成
gh release create v0.1.1 --title "v0.1.1 - Bug Fixes" --notes "See CHANGELOG.md for details" --generate-notes
```

### **MINOR リリース (v0.x.0) - 新機能**

#### **事前準備**
```bash
# feature branchから master merge確認
git log --oneline -5

# 全テスト実行
pytest tests/ --cov=legacy_import_migrator
python -m legacy_import_migrator.tests.integration_test  # もしあれば
```

#### **バージョン更新 + ドキュメント**
```bash
# pyproject.toml
# version = "0.2.0"

# CHANGELOG.md更新
# ## v0.2.0 - 2024-XX-XX
# ### Added
# - New command: lim report
# - Support for GitLab CI
# ### Changed
# - Improved error messages
# ### Fixed
# - Bug in allowlist processing

# README.md更新 (新機能の使用例追加)
```

#### **リリース実行**
```bash
# コミット・タグ
git add pyproject.toml CHANGELOG.md README.md
git commit -m "chore: release v0.2.0 with new features

### Added
- New lim report command for HTML output
- GitLab CI integration support
- Enhanced allowlist patterns

### Improved  
- Error messages clarity
- Performance for large repositories

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git tag -a v0.2.0 -m "Release v0.2.0: New Features"
git push origin master v0.2.0

# ビルド・アップロード
rm -rf dist/
python -m build
python -m twine upload --disable-progress-bar dist/*

# GitHub Release (詳細版)
gh release create v0.2.0 --title "v0.2.0 - New Features" --notes-file CHANGELOG.md
```

---

## 🚨 緊急対応

### **Critical Bug対応**

#### **1. 緊急確認 (15分以内)**
```bash
# Issue詳細確認
gh issue view [ISSUE番号]

# 影響範囲評価
# - PyPI download数確認
# - world-simulation CI影響確認
# - 他の依存プロジェクト確認
```

#### **2. 緊急パッチ作成 (2時間以内)**
```bash
# 緊急branch作成
git checkout -b hotfix/critical-bug-fix

# 最小限の修正実装
# テスト追加・実行
pytest tests/ -k "test_related_to_bug"

# コミット
git commit -m "hotfix: critical bug fix for issue #X"
```

#### **3. 緊急リリース (当日中)**
```bash
# master merge
git checkout master  
git merge hotfix/critical-bug-fix

# 緊急バージョンアップ
# version = "0.1.2" (patch increment)

git add pyproject.toml
git commit -m "chore: emergency release v0.1.2"
git tag -a v0.1.2 -m "Emergency release v0.1.2: Critical bug fix"
git push origin master v0.1.2

# 緊急PyPI upload
python -m build
python -m twine upload --disable-progress-bar dist/*

# GitHub Release
gh release create v0.1.2 --title "v0.1.2 - Emergency Fix" --notes "Critical bug fix for issue #X"
```

#### **4. 通知**
```bash
# Issue更新
gh issue comment [ISSUE番号] "Fixed in v0.1.2. Please upgrade: pip install --upgrade legacy-import-migrator"

# world-simulation CI更新確認
cd /c/Users/uraka/project/world-simulation
# 必要に応じてCI再実行
```

### **Security Issue対応**

#### **1. Private確認**
```bash
# Security advisory確認
gh api repos/strataregula/legacy-import-migrator/security-advisories

# 詳細分析
# - 脆弱性影響範囲
# - 攻撃可能性評価
# - 修正方針決定
```

#### **2. 非公開修正**
```bash
# Private development
git checkout -b security/CVE-2024-XXXX

# セキュリティ修正実装
# 最小限の変更で脆弱性解消

# Private testing
pytest tests/security/ -v
```

#### **3. Coordinated Disclosure**
```bash
# Security patch準備
# version increment (patch or minor depending on impact)

# PyPI upload
python -m build
python -m twine upload --disable-progress-bar dist/*

# Public disclosure
gh security-advisory create --severity high --title "Security Fix v0.1.3"
```

---

## 🐛 Issue Management

### **Issue Triage Process**

#### **新しいIssue処理**
```bash
# Issue確認
gh issue view [ISSUE番号]

# ラベル付け
gh issue edit [ISSUE番号] --add-label "priority:medium,category:bug"
gh issue edit [ISSUE番号] --add-assignee strataregula

# 初期返信テンプレート
gh issue comment [ISSUE番号] "Thanks for reporting! I'll investigate and get back to you within 24 hours."
```

#### **Priority Classification**

**Critical (即座)**
- セキュリティ脆弱性
- データ破損リスク  
- CI完全停止

**High (1週間以内)**
- 機能停止バグ
- パフォーマンス重大問題
- world-simulation影響

**Medium (1ヶ月以内)**
- 機能改善要求
- 使い勝手向上
- ドキュメント更新

**Low (時間ある時)**
- Nice-to-have機能
- 外部統合
- 最適化

### **コミュニケーションテンプレート**

#### **Bug Report返信**
```markdown
Hi @username,

Thanks for the detailed bug report! 🐛

I've reproduced the issue and identified the root cause. The problem occurs when [explanation].

I'll have a fix ready in the next patch release (v0.1.x), expected within [timeframe].

As a temporary workaround, you can [workaround steps].

I'll update this issue once the fix is released.
```

#### **Feature Request返信**
```markdown
Hi @username,

Thanks for the feature request! 🚀

This is an interesting use case. I can see how [feature] would be helpful for [use case].

I'm adding this to our backlog for the next minor release (v0.x.0). The implementation would likely involve [approach].

If you're interested in contributing, I'd be happy to provide guidance on the implementation approach.
```

#### **Release通知**
```markdown
🎉 This has been fixed/implemented in v0.1.x!

You can upgrade with:
```bash
pip install --upgrade legacy-import-migrator
```

Please let me know if you encounter any issues with the new version.
```

---

## 📊 Monitoring & Analytics

### **Key Metrics Tracking**

#### **Weekly Dashboard**
```bash
# GitHub metrics
echo "=== GitHub Stats ==="
gh api repos/strataregula/legacy-import-migrator | jq '.stargazers_count, .forks_count'

# Issues/PRs
echo "=== Issues/PRs ==="
gh issue list --state open | wc -l
gh pr list --state open | wc -l

# CI health
echo "=== CI Health ==="
gh run list --status failure --limit 5
```

#### **Monthly Report**
```bash
# PyPI stats (manual check)
echo "Check PyPI downloads: https://pypistats.org/packages/legacy-import-migrator"

# Version adoption
echo "Check version distribution from PyPI stats"

# world-simulation usage
cd /c/Users/uraka/project/world-simulation
git log --oneline --since="1 month ago" --grep="legacy"
```

---

## 🔄 Routine Maintenance

### **Quarterly Review (2時間)**

#### **Code Quality Review**
```bash
# Test coverage確認
pytest tests/ --cov=legacy_import_migrator --cov-report=html
# 目標: >90% coverage

# Code quality metrics
ruff check src/
mypy src/
```

#### **Documentation Review**
```bash
# README.md 最新性確認
# CONTRIBUTING.md 更新確認
# API documentation (if any) 更新
```

#### **Dependency Audit**
```bash
# セキュリティ監査
pip-audit

# 不要依存関係確認
pip-check

# パフォーマンス影響確認
python -m timeit "import legacy_import_migrator"
```

### **Annual Planning (1日)**

#### **Roadmap Review**
- Major version (v1.0.0) 検討
- Breaking changes計画
- 新機能prioritization

#### **Architecture Review**
- Code structure見直し
- Performance optimization
- Test strategy改善

---

## 📋 Checklists

### **Pre-Release Checklist**
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Version number incremented
- [ ] CHANGELOG.md updated
- [ ] Security scan clean
- [ ] world-simulation CI compatibility tested

### **Post-Release Checklist**
- [ ] PyPI upload confirmed
- [ ] GitHub release created
- [ ] Version tag pushed
- [ ] Issue notifications sent
- [ ] world-simulation CI updated (if needed)
- [ ] Monitoring alerts configured

### **Emergency Response Checklist**
- [ ] Issue severity assessed
- [ ] Stakeholders notified
- [ ] Hotfix branch created
- [ ] Minimal fix implemented
- [ ] Emergency testing completed
- [ ] Release deployed
- [ ] Users notified
- [ ] Post-mortem scheduled

---

## 📞 Contact & Escalation

### **Internal Escalation**
- **Primary**: strataregula GitHub account
- **Backup**: Project maintainer team
- **Emergency**: [Emergency contact if critical production impact]

### **External Communication**
- **GitHub Issues**: Primary support channel
- **GitHub Discussions**: Community questions
- **Security Issues**: security@[domain] or GitHub Security Advisory

---

**📅 This operations manual provides step-by-step procedures for all routine and emergency operations.**

---

*Generated with Claude Code - Legacy Import Migration Toolkit Operations Manual*