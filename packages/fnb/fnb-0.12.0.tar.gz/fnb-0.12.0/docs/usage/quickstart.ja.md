# クイックスタート

このガイドでは、fnbを使って最初のバックアップを実行するまでの手順を説明します。

## インストール

```bash
# uv を使用してプロジェクトセットアップ
uv venv
uv pip install -e .
```

詳細は[インストールガイド](../installation.ja.md)を参照してください。

## 初期設定

### 1. 設定ファイルの作成

```bash
# 設定ファイルを作成
fnb init
```

このコマンドで以下のファイルが生成されます：

- `fnb.toml` - バックアップタスクの設定
- `.env.plain` - 認証情報のテンプレート

### 2. 設定ファイルの編集

```bash
# バックアップタスクの設定
vi fnb.toml

# 認証情報の設定
vi .env.plain
cp .env.plain .env
```

設定ファイルの詳細は[設定ファイル](configuration.ja.md)を参照してください。

## 最初のバックアップ実行

### 設定確認

```bash
# 設定内容の確認
fnb status
```

### バックアップ実行

```bash
# Fetch + Backup を一括実行
fnb sync logs
```

### 個別実行

```bash
# リモートからローカルにデータを取得
fnb fetch logs

# ローカルからクラウドストレージにバックアップ
fnb backup logs
```

## 🔐 環境変数の暗号化（推奨）

セキュリティを強化するため、パスワードは暗号化して保存することを推奨します。

```bash
# 環境変数を暗号化
dotenvx encrypt -f .env
# .env: 暗号化されたパスワード
# .env.keys: 秘密鍵

# fnbコマンドを実行
dotenvx run -- fnb sync logs
```

## 次のステップ

- [基本コマンド](commands.ja.md) - 全コマンドの詳細な使い方
- [設定ファイル](configuration.ja.md) - より詳細な設定方法
- [例](examples.ja.md) - 実際の設定例
