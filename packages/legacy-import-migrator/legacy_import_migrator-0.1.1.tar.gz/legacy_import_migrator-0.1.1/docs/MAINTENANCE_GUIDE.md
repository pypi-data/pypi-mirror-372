# Maintenance & Versioning Guide

Legacy Import Migration Toolkit 運用フェーズ管理ガイド

## 🔄 運用フェーズの基本方針

### **Natural Growth Strategy**
- ✅ 技術実装・配布・ドキュメント整備完了
- 🎯 **world-simulation CI での実用運用**
- 📊 **実際のユーザー利用でのフィードバック収集**  
- 🔧 **必要に応じたメンテナンス & バージョンアップ**

無理にコミュニティ展開せず、**実用価値ベースの成長**を重視。

---

## 📦 バージョン管理戦略

### **セマンティックバージョニング (SemVer)**
- **MAJOR**: 破壊的変更 (JSON schema v2.0, CLI interface changes)
- **MINOR**: 新機能追加 (新しいコマンド、新しいオプション)
- **PATCH**: バグフィックス、小改善

### **現在のバージョン**: v0.1.0

### **想定される次のバージョン**

#### **v0.1.1-v0.1.x (PATCH)**
- バグフィックス
- パフォーマンス改善
- ドキュメント更新
- 依存関係アップデート

#### **v0.2.0 (MINOR)**
- 新コマンド追加 (例: `lim migrate`, `lim report`)
- 新出力形式 (例: HTML report, CSV export)
- 新しい allowlist パターン
- Git provider 対応拡張 (GitLab, Bitbucket)

#### **v1.0.0 (MAJOR)**
- JSON schema v2.0 (breaking change)
- CLI interface 大幅変更
- 設定ファイル対応

---

## 🔧 メンテナンス手順

### **日常メンテナンス**

#### **1. 依存関係更新**
```bash
# 月次実行推奨
cd /c/Users/uraka/project/legacy-import-migrator

# 依存関係チェック
pip list --outdated

# pyproject.toml 更新
# requirements: click>=8.1.0, rich>=13.0.0, pathspec>=0.12.0

# テスト実行
pytest tests/

# 問題なければ patch version bump
```

#### **2. セキュリティアップデート**
```bash
# GitHub Security Alerts 確認
# Dependabot PR 確認・マージ

# セキュリティスキャン
pip-audit

# 必要に応じて緊急パッチリリース
```

#### **3. CI ヘルスチェック**
```bash
# GitHub Actions status 確認
gh run list --limit 5

# world-simulation での利用状況確認
# エラーログ、使用統計確認
```

### **リリースプロセス**

#### **PATCH リリース (v0.1.x)**
1. **変更実装**
   ```bash
   git checkout -b fix/issue-description
   # 実装・テスト・コミット
   ```

2. **バージョン更新**
   ```bash
   # pyproject.toml version 更新
   version = "0.1.1"  # 0.1.0 → 0.1.1
   ```

3. **リリース実行**
   ```bash
   git tag -a v0.1.1 -m "Release v0.1.1: Bug fixes and improvements"
   git push origin v0.1.1
   
   # PyPI upload
   python -m build
   python -m twine upload --disable-progress-bar dist/*
   ```

#### **MINOR リリース (v0.x.0)**
1. **機能開発**
   ```bash
   git checkout -b feature/new-command
   # 実装・テスト・ドキュメント更新
   ```

2. **バージョン更新 + Release Notes**
   ```bash
   # pyproject.toml
   version = "0.2.0"
   
   # CHANGELOG.md 更新
   # GitHub Release Notes 準備
   ```

3. **リリース + アナウンス**
   ```bash
   # 通常リリースプロセス
   # 必要に応じて軽いコミュニティアナウンス
   ```

---

## 🐛 Issue 管理

### **Issue テンプレート設計**

#### **Bug Report Template**
```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command: `lim scan --legacy-patterns "..."`
2. See error

**Expected behavior**
What you expected to happen.

**Environment**
- OS: [e.g. Windows 11, Ubuntu 22.04]
- Python version: [e.g. 3.11.5]  
- Package version: [e.g. 0.1.0]

**Additional context**
Add any other context about the problem here.
```

#### **Feature Request Template**
```markdown
**Is your feature request related to a problem?**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Use case**
Describe your specific use case for this feature.

**Additional context**
Add any other context about the feature request here.
```

### **Issue 対応優先度**

#### **Critical (即座対応)**
- セキュリティ脆弱性
- データ破損リスク
- CI 完全停止

#### **High (1週間以内)**
- 機能停止バグ
- パフォーマンス重大問題
- world-simulation 影響

#### **Medium (1ヶ月以内)**
- 機能改善要求
- 使い勝手向上
- ドキュメント更新

#### **Low (時間ある時)**
- Nice-to-have 機能
- 外部統合
- 最適化

---

## 📊 ユーザーフィードバック収集

### **メトリクス追跡**

#### **PyPI Stats**
- ダウンロード数推移
- バージョン別利用状況  
- 地域別利用分布

#### **GitHub Insights**
- Stars/Forks 推移
- Issue/PR エンゲージメント
- Releases ダウンロード数

#### **world-simulation 内部使用**
- CI 実行頻度
- エラー発生率
- パフォーマンス metrics

### **フィードバック チャネル**

#### **Proactive Collection**
- GitHub Discussions 活用
- world-simulation チーム feedback
- CI エラー pattern analysis

#### **Reactive Support**  
- GitHub Issues 迅速対応
- Stack Overflow monitoring (legacy-import-migrator tag)
- 公開質問への回答

---

## 🚀 成長シナリオ

### **Phase 1: Stable Operation (現在～6ヶ月)**
- world-simulation での安定運用
- バグフィックス & 小改善
- 依存関係メンテナンス
- **目標**: 0 critical issues, 安定したCI実行

### **Phase 2: Natural Adoption (6ヶ月～1年)**  
- 自然なコミュニティ発見
- Issue/PR による機能要求
- 他プロジェクトでの利用例
- **目標**: 月間 100+ PyPI downloads

### **Phase 3: Community Growth (1年～)**
- 積極的コミュニティ展開（必要に応じて）
- プラグイン システム検討
- 他ツールとの統合
- **目標**: 月間 1000+ downloads, active contributors

---

## 🔄 定期メンテナンス スケジュール

### **Weekly** (10分)
- CI status 確認
- Critical issues 確認
- Security alerts 確認

### **Monthly** (30分)
- 依存関係更新検討
- PyPI stats 確認  
- Issue triage

### **Quarterly** (2時間)
- 機能要求評価
- ロードマップ更新
- ドキュメント見直し

### **Yearly** (1日)
- メジャーバージョン検討
- アーキテクチャ見直し
- 長期戦略評価

---

## 🎯 成功指標

### **Technical Health**
- ✅ CI success rate >95%
- ✅ Security vulnerabilities = 0
- ✅ Code coverage >90%
- ✅ Response time <24h for critical issues

### **User Satisfaction**
- ✅ GitHub stars growth
- ✅ Positive issue/PR feedback
- ✅ Low abandoned issue rate
- ✅ Active community discussions

### **Business Impact**
- ✅ world-simulation CI stability
- ✅ Migration efficiency improvement
- ✅ Developer productivity metrics
- ✅ Reduced manual migration effort

---

## 📋 緊急対応プロトコル

### **Critical Bug 発見時**
1. **即座実行** (30分以内)
   - Issue 作成・ラベル付け
   - 影響範囲評価
   - 緊急パッチ準備開始

2. **当日実行**
   - パッチ実装・テスト
   - 緊急リリース準備
   - 影響ユーザー通知

3. **翌日実行**
   - PyPI 緊急アップデート
   - GitHub Release
   - world-simulation CI アップデート

### **Security Issue 発見時**
1. **Private報告受付**
2. **非公開修正開発**  
3. **Coordinated disclosure**
4. **Security advisory 公開**

---

**📅 This maintenance guide ensures long-term sustainability and user value delivery.**

---

*Generated with Claude Code - Legacy Import Migration Toolkit Maintenance Guide*