# リリース管理ガイド

このドキュメントは、fnb (Fetch'n'Backup) をPyPIにリリースするための包括的な手順を説明します。バージョン管理、テスト手順、配信ワークフローを含みます。

## 目次

- [リリース概要](#リリース概要)
- [前提条件](#前提条件)
- [バージョン管理](#バージョン管理)
- [リリースワークフロー](#リリースワークフロー)
- [PyPI配信](#pypi配信)
- [テストと検証](#テストと検証)
- [トラブルシューティング](#トラブルシューティング)
- [自動化CI/CD](#自動化cicd)

## リリース概要

fnbプロジェクトは、以下の自動化ワークフローでセマンティックバージョニングを使用します：
- **バージョン管理**: commitizenによる自動化
- **テスト**: 87%カバレッジのユニット・統合テスト
- **ビルド**: hatchlingバックエンドのuvビルドシステム
- **配信**: テスト用TestPyPI、本番用PyPI
- **ドキュメント**: 自動変更ログ生成

### リリース種別

- **パッチリリース** (0.10.1): バグ修正とマイナー改善
- **マイナーリリース** (0.11.0): 新機能、後方互換性あり
- **メジャーリリース** (1.0.0): 破壊的変更（準備ができた時）

## 前提条件

### 環境セットアップ

1. **開発環境**
   ```bash
   # クリーンな作業ディレクトリを確認
   git status

   # 最新のmainブランチに更新
   git checkout main
   git pull origin main
   ```

2. **必要なツール**
   - Python 3.12+
   - uvパッケージマネージャー
   - GitLab CLI (`glab`)
   - Taskランナー (`task`)

3. **APIトークン設定**

   プロジェクトルートに`.env`ファイルを作成：
   ```bash
   # PyPI本番APIトークン
   PYPI_API_TOKEN=pypi-your-production-token-here

   # TestPyPI APIトークン
   TESTPYPI_API_TOKEN=pypi-your-testpypi-token-here
   ```

   **⚠️ セキュリティ注意**: APIトークンをバージョン管理にコミットしないでください。`.env`を`.gitignore`に追加してください。

### APIトークンセットアップ

1. **PyPI本番トークン**
   - https://pypi.org/manage/account/token/ にアクセス
   - `fnb`プロジェクトに限定されたスコープのトークンを作成
   - `.env`に`PYPI_API_TOKEN`として追加

2. **TestPyPIトークン**
   - https://test.pypi.org/manage/account/token/ にアクセス
   - `fnb`プロジェクトに限定されたスコープのトークンを作成
   - `.env`に`TESTPYPI_API_TOKEN`として追加

## バージョン管理

### 自動バージョンアップ

プロジェクトは自動バージョン管理に[commitizen](https://commitizen-tools.github.io/commitizen/)を使用：

```bash
# バージョン変更をプレビュー（ドライラン）
task version

# バージョンアップと変更ログ更新を実行
task version:bump
```

### 手動バージョン設定

バージョンアップ時に自動更新されるファイル：
- `pyproject.toml:version`
- `src/fnb/__init__.py:__version__`
- `CHANGELOG.md`（慣例的コミット）

### バージョンスキーム

```toml
[tool.commitizen]
name = "cz_conventional_commits"
version = "0.10.0"
tag_format = "$version"
version_scheme = "semver"
update_changelog_on_bump = true
major_version_zero = true
```

## リリースワークフロー

### 1. クイックリリース（推奨）

ほとんどのリリースに対応する完全自動化ワークフロー：

```bash
# 完全リリースワークフロー（test → format → bump → release）
task release:full
```

このコマンドは以下を実行：
1. 統合テストを含むすべてのテストを実行
2. ruffでコードをフォーマット
3. pre-commitフックを実行
4. バージョンアップと変更ログ更新
5. タグ付きでGitLabリリース作成

### 2. ステップバイステップリリース

リリースプロセスをより制御したい場合：

```bash
# ステップ1: 包括的テスト実行
task test

# ステップ2: コードフォーマットと品質チェック
task lint
task lint:pre-commit

# ステップ3: バージョン変更をプレビュー
task version

# ステップ4: バージョンアップ
task version:bump

# ステップ5: GitLabリリース作成
task release
```

### 3. 開発テストワークフロー

リリース作成前に、完全なCIパイプラインをローカルでテスト：

```bash
# 完全CIパイプラインをシミュレート
task test:ci

# これは以下を実行：
# - カバレッジ付きユニットテスト
# - コードフォーマットチェック
# - pre-commitフック
```

## PyPI配信

### TestPyPI配信（最初に推奨）

本番前に常にTestPyPIでの配信をテスト：

```bash
# TestPyPIに配信
task publish:test
```

### 本番PyPI配信

TestPyPI検証成功後：

```bash
# 本番PyPIに配信
task publish:prod
```

### 配信プロセス詳細

両配信コマンドは以下を実行：
1. **ビルド**: `uv build`でwheelとソース配布を作成
2. **アップロード**: `uv publish`で各PyPIリポジトリにアップロード
3. **検証**: PyPIによる自動パッケージ検証

## テストと検証

### TestPyPI検証

TestPyPI配信後、パッケージを検証：

```bash
# 特定バージョンを検証（x.y.zを実際のバージョンに置換）
VERSION=x.y.z task verify:testpypi
```

検証プロセス：
1. `/tmp/fnb-test`に分離テスト環境作成
2. TestPyPIからパッケージをインストール
3. 核心機能をテスト：
   - `fnb version`コマンド
   - `fnb --help`コマンド
   - `fnb init --help`コマンド
   - モジュールインポート検証
4. 検証状況をレポート

### 手動検証

手動での検証も可能：

```bash
# テスト環境作成
cd /tmp
python3 -m venv test-fnb
source test-fnb/bin/activate

# TestPyPIからインストール
pip install --index-url https://test.pypi.org/simple/ \
           --extra-index-url https://pypi.org/simple/ \
           fnb==x.y.z

# 基本機能テスト
fnb --help
fnb version
fnb init --help

# クリーンアップ
deactivate
rm -rf test-fnb
```

### 本番検証

PyPI配信後、以下で検証：

```bash
# 本番PyPIからインストール
pip install fnb==x.y.z

# 機能テスト
fnb --help
fnb version
```

## トラブルシューティング

### よくある問題

1. **ビルド失敗**
   ```bash
   # ビルド環境をチェック
   uv build --verbose

   # よくある修正：
   # - pyproject.tomlメタデータを更新
   # - バージョン一貫性をチェック
   # - 依存関係指定を検証
   ```

2. **アップロード失敗**
   ```bash
   # APIトークンの有効性をチェック
   echo $PYPI_API_TOKEN
   echo $TESTPYPI_API_TOKEN

   # PyPIアカウント設定でトークン権限を検証
   ```

3. **バージョン競合**
   ```bash
   # 現在のバージョンをチェック
   cat pyproject.toml | grep version
   cat src/fnb/__init__.py | grep __version__

   # バージョン一貫性を強制
   task version:bump
   ```

4. **テスト失敗**
   ```bash
   # 詳細出力でテスト実行
   task test:unit -v

   # カバレッジレポートをチェック
   open htmlcov/index.html
   ```

### 復旧手順

1. **失敗したリリースの復旧**
   ```bash
   # バージョンアップ後にリリースが失敗した場合
   git reset --hard HEAD~1  # バージョンアップ前にリセット

   # または問題を修正して再試行
   task release
   ```

2. **PyPIアップロード失敗の復旧**
   ```bash
   # 失敗したパッケージを削除（可能な場合）
   # コード/設定の問題を修正
   # バージョンを増分して再試行
   task version:bump
   task publish:test  # 常に最初にテスト
   ```

## 自動化CI/CD

### GitLab CI統合

プロジェクトには自動化ワークフローが含まれます：

1. **自動TestPyPI配信**
   - gitタグプッシュでトリガー
   - 完全テストスイートを実行
   - TestPyPIに自動配信

2. **手動本番配信**
   - TestPyPI検証後に`task publish:prod`を使用
   - 安全のため手動実行が必要

### CI設定

GitLab CIは自動的に：
- ユニット・統合テストを実行
- コードフォーマットをチェック
- パッケージメタデータを検証
- タグ作成時にTestPyPIに配信

## リリースチェックリスト

### プレリリース

- [ ] すべてのテストが通過（`task test`）
- [ ] コードがフォーマット済み（`task lint`）
- [ ] pre-commitフックが通過（`task lint:pre-commit`）
- [ ] ドキュメントが更新済み
- [ ] CHANGELOG.mdがレビュー済み
- [ ] `.env`にAPIトークンが設定済み

### リリースプロセス

- [ ] バージョンアップ済み（`task version:bump`）
- [ ] GitLabリリース作成済み（`task release`）
- [ ] TestPyPI配信成功（`task publish:test`）
- [ ] TestPyPI検証通過（`VERSION=x.y.z task verify:testpypi`）
- [ ] 本番PyPI配信（`task publish:prod`）
- [ ] 本番検証完了

### ポストリリース

- [ ] リリースアナウンス（必要に応じて）
- [ ] ドキュメントサイト更新
- [ ] イシュートラッカー更新
- [ ] 次の開発サイクル計画

## リリーススケジュール

### 定期リリース

- **パッチリリース**: バグ修正に応じて必要時
- **マイナーリリース**: 月次または機能完成時
- **メジャーリリース**: 破壊的変更が必要時

### 緊急リリース

重要なセキュリティや機能問題の場合：
1. ホットフィックスブランチ作成
2. 最小限の修正実装
3. 高速テストとレビュー
4. 緊急リリース配信

## ベストプラクティス

### 開発

- 自動変更ログ生成のため慣例的コミットを使用
- 高いテストカバレッジを維持（目標: 87%+）
- 本番前にTestPyPIですべての変更をテスト
- リリース前に変更ログをレビュー

### セキュリティ

- APIトークンをコミットしない
- 最小スコープのAPIトークンを使用
- APIトークンを定期的にローテート
- リリース通知をモニター

### ドキュメント

- リリースと共にドキュメントを更新
- 正確なインストール手順を維持
- 破壊的変更を明確に文書化
- メジャーリリースには移行ガイドを提供

## サポートと連絡

リリース関連の問題：
- **バグレポート**: https://gitlab.com/qumasan/fnb/-/issues
- **ドキュメント**: https://qumasan.gitlab.io/fnb/
- **マージリクエスト**: https://gitlab.com/qumasan/fnb/-/merge_requests

---

**最終更新**: 2025-08-21 (v0.10.0)
**ドキュメントバージョン**: 1.0.0
