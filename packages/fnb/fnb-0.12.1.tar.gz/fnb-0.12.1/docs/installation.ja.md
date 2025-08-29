# fnb インストールガイド

このドキュメントは、fnb (Fetch'n'Backup) の包括的なインストール手順を説明します。

## システム要件

### 必須
- **Python**: 3.12以上
- **OS**: Windows、macOS、Linux (OS非依存)
- **rsync**: ローカルまたはリモートサーバーで利用可能

### 推奨
- **パッケージマネージャー**: uv (高速) または pip
- **ターミナル**: UTF-8互換のターミナルエミュレーター
- **SSH**: リモートサーバーアクセス用

## インストール方法

### 1. PyPIから (推奨)

#### pipを使用
```bash
# 基本インストール
pip install fnb

# ユーザーインストール
pip install --user fnb

# 最新版にアップグレード
pip install --upgrade fnb
```

#### uvを使用 (推奨)
```bash
# uvがインストールされていない場合
curl -LsSf https://astral.sh/uv/install.sh | sh

# fnbをインストール
uv pip install fnb

# プロジェクトに追加
uv add fnb
```

#### pipxを使用 (アプリケーション分離)
```bash
# pipxがインストールされていない場合
pip install pipx

# 分離環境でfnbをインストール
pipx install fnb
```

### 2. ソースから

#### 開発用インストール
```bash
# リポジトリをクローン
git clone https://gitlab.com/qumasan/fnb.git
cd fnb

# uvを使用 (推奨)
uv venv
source .venv/bin/activate  # Linux/macOS
# または .venv\Scripts\activate  # Windows
uv pip install -e .

# 従来のpipを使用
python -m venv venv
source venv/bin/activate    # Linux/macOS
# または venv\Scripts\activate    # Windows
pip install -e .
```

#### ビルドしてインストール
```bash
git clone https://gitlab.com/qumasan/fnb.git
cd fnb

# uvを使用してビルド
uv build
pip install dist/fnb-*.whl

# またはhatchlingを直接使用
pip install build
python -m build
pip install dist/fnb-*.whl
```

## プラットフォーム別セットアップ

### Windows

#### 前提条件
```powershell
# Python 3.12+のインストール確認
python --version

# Pythonが見つからない場合:
# Microsoft StoreまたはPython.orgからPython 3.12+をインストール
```

#### インストール手順
```powershell
# PowerShellまたはコマンドプロンプトで実行
pip install fnb

# インストール確認
fnb version
```

#### rsyncセットアップ (Windows)
```powershell
# WSL2を使用
wsl --install
wsl
sudo apt update && sudo apt install rsync

# またはMSYS2/Cygwinを使用
# https://www.msys2.org/ からインストール
```

### macOS

#### Homebrewを使用
```bash
# Homebrewを使用してPythonをインストール (推奨)
brew install python@3.12

# fnbをインストール
pip3 install fnb

# rsyncは通常プリインストール済み
rsync --version
```

#### pyenvを使用
```bash
# pyenvを使用してPythonをインストール
brew install pyenv
pyenv install 3.12.0
pyenv global 3.12.0

# fnbをインストール
pip install fnb
```

### Linux

#### Ubuntu/Debian
```bash
# Python 3.12+をインストール
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip

# fnbをインストール
pip3 install fnb

# rsyncをインストール (通常プリインストール済み)
sudo apt install rsync
```

#### CentOS/RHEL/Rocky Linux
```bash
# Python 3.12+をインストール
sudo dnf install python3.12 python3-pip

# fnbをインストール
pip3 install fnb

# rsyncをインストール
sudo dnf install rsync
```

#### Arch Linux
```bash
# Pythonをインストール
sudo pacman -S python python-pip

# fnbをインストール
pip install fnb

# rsyncをインストール
sudo pacman -S rsync
```

## インストール確認

インストールが成功したことを確認：

```bash
# バージョン確認
fnb version

# ヘルプ表示
fnb --help

# 設定ファイル初期化 (機能テスト)
fnb init --help
```

## 依存関係

fnbは以下のPythonパッケージに依存しています：

```
pexpect>=4.9.0      # SSH自動化
platformdirs>=4.3.8 # プラットフォーム固有パス
pydantic>=2.11.7    # 設定検証
python-dotenv>=1.0.1 # 環境変数
toml>=0.10.2        # 設定ファイル
typer>=0.14.2       # CLIフレームワーク
```

これらは自動的にインストールされます。

## トラブルシューティング

### よくある問題と解決方法

#### 1. Pythonバージョンエラー
```
ERROR: fnb requires Python 3.12 or higher
```

**解決方法:**
```bash
# 現在のバージョン確認
python --version

# Python 3.12+をインストール:
# - Windows: Microsoft StoreまたはPython.org
# - macOS: brew install python@3.12
# - Linux: パッケージマネージャーでpython3.12をインストール
```

#### 2. pipインストールエラー
```
ERROR: Could not find a version that satisfies the requirement fnb
```

**解決方法:**
```bash
# pipを最新版にアップデート
pip install --upgrade pip

# PyPIから直接インストール
pip install --index-url https://pypi.org/simple/ fnb
```

#### 3. 権限エラー (Linux/macOS)
```
ERROR: Permission denied
```

**解決方法:**
```bash
# ユーザー環境にインストール
pip install --user fnb

# または仮想環境を使用
python -m venv venv
source venv/bin/activate
pip install fnb
```

#### 4. rsyncが見つからない
```
ERROR: rsync command not found
```

**解決方法:**
```bash
# Linux
sudo apt install rsync  # Ubuntu/Debian
sudo dnf install rsync  # CentOS/RHEL

# macOS (通常プリインストール済み)
brew install rsync  # 最新版が必要な場合

# Windows
# WSL、MSYS2、またはCygwinを使用
```

#### 5. pexpectエラー (Windows開発時)
```
ERROR: pexpect is not supported on Windows
```

**解決方法:**
WindowsではSSHパスワード自動化に制限があります：
```bash
# WSL2を使用 (推奨)
wsl
pip install fnb

# または手動SSHパスワード入力
# pexpect機能は無効化されます
```

### ログ検査

問題が続く場合：

```bash
# 詳細インストール
pip install -v fnb

# Python環境情報
python -m pip show fnb
python -c "import sys; print(sys.path)"

# 設定ファイル場所確認
fnb status
```

## アップグレード

既存のfnbを最新版にアップグレード：

```bash
# pipを使用
pip install --upgrade fnb

# uvを使用
uv pip install --upgrade fnb

# pipxを使用
pipx upgrade fnb
```

## アンインストール

fnbの完全削除：

```bash
# パッケージをアンインストール
pip uninstall fnb

# 設定ファイルを削除 (オプション)
# Linux/macOS
rm -rf ~/.config/fnb/
rm -f ./fnb.toml
rm -f ./.env

# Windows
# %LOCALAPPDATA%\fnb\ フォルダを削除
# fnb.tomlと.envファイルを削除
```

## 次のステップ

インストール成功後：

- **クイックスタート**: [クイックスタートガイド](usage/quickstart.ja.md)を参照
- **設定**: [設定ファイル](usage/configuration.ja.md)について学習 (準備中)
- **使い方**: [コマンドリファレンス](usage/commands.ja.md)を読む (準備中)

## サポート

インストールに関する問題やサポート：

- **イシュートラッカー**: https://gitlab.com/qumasan/fnb/-/issues
- **ドキュメント**: https://qumasan.gitlab.io/fnb/
- **リポジトリ**: https://gitlab.com/qumasan/fnb

新しいイシューを作成する際は以下を含めてください：
- OSとバージョン
- Pythonバージョン (`python --version`)
- 完全なエラーメッセージ
- 使用したインストール方法
