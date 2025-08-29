# セキュリティガイド

このガイドでは、`.env`ファイルでの平文パスワード保存を超えた、fnbの安全な認証方法について説明します。

## 概要

デフォルトでは、fnbは`.env`ファイル経由でSSHパスワード認証をサポートしていますが、このアプローチではパスワードが平文で保存されます。このガイドでは、より安全な代替手段とベストプラクティスを紹介します。

## 認証方法（推奨順序）

### 1. SSH鍵認証（最も安全）

SSH鍵認証により、パスワード保存の必要性を完全に排除できます。

#### SSH鍵の設定

```bash
# SSH鍵ペアを生成（秘密鍵・公開鍵ファイルを作成）
ssh-keygen -t ed25519 -f ~/.ssh/fnb_key

# 公開鍵をリモートサーバーにコピー（~/.ssh/authorized_keysに追加）
ssh-copy-id -i ~/.ssh/fnb_key.pub user@server.com

# SSH設定でキーを指定
echo "Host server.com
  IdentityFile ~/.ssh/fnb_key
  IdentitiesOnly yes" >> ~/.ssh/config
```

**コマンドの説明:**
- `ssh-keygen`: 新しいSSH鍵ペア（秘密鍵 + 公開鍵）を作成
  - `-t ed25519`: 現代的なEd25519アルゴリズムを使用（推奨）
  - `-f ~/.ssh/fnb_key`: 出力ファイルパスを指定
- `ssh-copy-id`: 公開鍵をリモートサーバーにコピー
  - `-i ~/.ssh/fnb_key.pub`: コピーする公開鍵を指定
  - リモートサーバーの`~/.ssh/authorized_keys`に自動で追加

#### 利点

- **パスワード保存不要** - 最も安全なオプション
- **自動認証** - 手動操作不要
- **キーローテーション** - キーの取り消しと交換が簡単
- **標準的な慣行** - 広く採用されているセキュリティ標準

#### 設定

SSH鍵を使用する場合、`.env`ファイルからパスワードエントリを削除してください：

```bash
# .envから以下の行を削除
# FNB_PASSWORD_USER_SERVER_COM=mypassword
# FNB_PASSWORD_DEFAULT=defaultpassword
```

### 2. macOSキーチェーン統合

平文ファイルの代わりに、macOSキーチェーンにパスワードを安全に保存します。

#### キーチェーン保存の設定

```bash
# パスワードをキーチェーンに保存
security add-generic-password \
  -s "fnb-ssh" \
  -a "user@server.com" \
  -w "your-password"

# キーチェーンからパスワードを取得
security find-generic-password \
  -s "fnb-ssh" \
  -a "user@server.com" \
  -w
```

**コマンドの説明:**

- `security add-generic-password`: macOSキーチェーンにパスワードを保存
    - `-s "fnb-ssh"`: サービス名（このパスワードエントリの識別子）
    - `-a "user@server.com"`: アカウント名（通常はSSH接続文字列）
    - `-w "your-password"`: 保存するパスワード（このオプションなしで対話的に入力も可能）
- `security find-generic-password`: キーチェーンからパスワードを取得
    - `-s "fnb-ssh"`: 検索するサービス名
    - `-a "user@server.com"`: 一致させるアカウント名
    - `-w`: パスワードのみを出力（このオプションなしではすべてのメタデータを表示）

#### 実装ノート

この方法は、キーチェーン統合をサポートするためにfnbの`env.py`モジュールの拡張が必要です。現在の実装は`.env`ファイルのみサポートしています。

### 3. dotenvx暗号化

既存のfnbワークフローとの互換性を保ちながら、dotenvxを使用して`.env`ファイルを暗号化します。

#### dotenvxのセットアップ

```bash
# dotenvxをインストール
npm install -g @dotenvx/dotenvx

# または他のパッケージマネージャーを使用
brew install dotenvx/brew/dotenvx
curl -fsS https://dotenvx.sh/install.sh | sh
```

#### 既存の.envファイルを暗号化

```bash
# 既存の.envファイルを暗号化
dotenvx encrypt

# これにより.envファイルがその場で暗号化され、.env.keysが作成されます
# 元の.envの内容は暗号化されました
```

#### 暗号化後のファイル構造

```
.env           # 暗号化ファイル（コミット可能）
.env.keys      # 復号化キー（コミット禁止）
```

#### fnbでの使用方法

```bash
# 暗号化された環境でfnbを実行
dotenvx run -- fnb fetch backup-server

# または環境に復号化キーを設定
export DOTENV_KEY="dotenv://:key_1234...@dotenvx.com/vault/.env.vault?environment=production"
fnb fetch backup-server

# 手動確認用の復号化（参考のみ）
dotenvx decrypt
```

#### 利点

- **後方互換性** - 既存のfnb実装と動作
- **暗号化ストレージ** - パスワードが保存時に暗号化
- **環境分離** - 開発/ステージング/本番用の異なるキー
- **バージョン管理安全** - 暗号化された`.env`の安全なコミット

#### Git設定

```bash
# .gitignoreに追加
echo ".env.keys" >> .gitignore

# 暗号化された.envはコミット可能（暗号化済み）
git add .env
```

### 4. GPG暗号化

GPGを使用してパスワードファイルに追加のセキュリティレイヤーを提供します。

#### GPG暗号化の設定

```bash
# 暗号化パスワードファイルを作成
echo "mypassword" | gpg --symmetric --armor > ~/.config/fnb/password.gpg

# 制限的な権限を設定
chmod 600 ~/.config/fnb/password.gpg

# 必要時に復号化
gpg --decrypt ~/.config/fnb/password.gpg
```

**コマンドの説明:**

- `gpg --symmetric --armor`: 対称暗号化を使用してデータを暗号化
    - `--symmetric`: パスフレーズベースの暗号化（公開鍵・秘密鍵不要）
    - `--armor`: ASCII形式の出力を作成（テキスト形式、扱いやすい）
    - 対話的に提供するパスフレーズで暗号化される
- `gpg --decrypt`: GPG暗号化ファイルを復号化
    - 暗号化時に使用したパスフレーズの入力を促す
    - `--quiet`: ステータスメッセージを抑制するオプション
    - `--batch`: 非対話モード用オプション（他の方法でパスフレーズ提供が必要）

#### fnbとの統合

この方法は、実行時にパスワードを復号化するために現在の実装の拡張が必要です。

### 5. 対話式パスワード入力

fnbは保存されたパスワードが見つからない場合、自動的に対話式パスワード入力にフォールバックします。

#### 現在の動作

環境変数やその他のソースにパスワードが見つからない場合、fnbは自動的に対話式パスワード入力にフォールバックします：

1. fnbが設定されたソースからパスワードの取得を試行
2. パスワードが見つからない場合（`ssh_password = None`）
3. rsyncがパスワード自動化なしで実行
4. SSHがターミナルでユーザーにパスワードを促す
5. ユーザーが対話的にパスワードを入力

#### 利点

- **設定不要** - すぐに使用可能
- **最高のセキュリティ** - パスワード保存なし
- **標準的なSSH動作** - 馴染みのあるユーザー体験
- **フォールバック機構** - 他の方法が失敗した場合でも利用可能

#### 使用例

```bash
# .envファイルやパスワード設定なし
fnb fetch backup-server

# 出力:
# Fetching backup-server from user@server:~/data/ to ./backup/
# user@server's password: [ユーザーがパスワードを入力]
# Fetch completed successfully: backup-server
```

#### このモードが有効になる条件

- `.env`ファイルが存在しない
- 環境変数`FNB_PASSWORD_*`が設定されていない
- 他のパスワードソース（キーチェーン、GPG）が設定されていないか失敗
- SSH鍵認証が設定されていない

## 現在の.envファイルセキュリティ

`.env`ファイルを引き続き使用する必要がある場合は、以下のセキュリティプラクティスにしたがってください：

### ファイル権限

```bash
# 制限的な権限を設定
chmod 600 .env
chmod 600 ~/.config/fnb/.env

# 権限を確認
ls -la .env
# 表示されるべき内容: -rw------- (600)
```

### 環境変数形式

```bash
# ホスト固有のパスワード（推奨）
FNB_PASSWORD_USER_EXAMPLE_COM=hostspecificpassword

# デフォルトパスワード（セキュリティが劣る）
FNB_PASSWORD_DEFAULT=defaultpassword
```

### Gitセキュリティ

```bash
# .envが.gitignoreに含まれていることを確認
echo ".env" >> .gitignore
echo "*.env" >> .gitignore

# 誤ってコミットされた場合、gitヒストリから.envを削除
git rm --cached .env
git commit -m "Remove .env from version control"
```

## セキュリティベストプラクティス

### 1. 最小権限の原則

- 特定のアクセススコープを持つSSH鍵を使用
- 共有またはデフォルトパスワードを避ける
- 定期的な認証情報のローテーション

### 2. 環境の分離

- 異なる環境用に別々のSSH鍵を使用
- 制限されたアクセス権を持つ環境固有の`.env`ファイルを維持
- `.env`ファイルをバージョン管理にコミットしない

### 3. モニタリングと監査

- サーバーログを通じたSSH鍵使用の監視
- 保存された認証情報の定期的なセキュリティ監査
- 使用されるすべての認証方法の文書化

### 4. バックアップセキュリティ

- 可能な場合はバックアップ先を暗号化
- バックアップ保存場所のセキュリティ確保
- 定期的なバックアップ整合性検証

## 平文パスワードからの移行

### ステップ1: 現在の設定を監査

```bash
# 現在の.envファイルを確認
ls -la .env ~/.config/fnb/.env

# 設定されたホストを確認
fnb status
```

### ステップ2: SSH鍵を実装

```bash
# 設定内の各ホストに対して
ssh-keygen -t ed25519 -f ~/.ssh/fnb_key_hostname
ssh-copy-id -i ~/.ssh/fnb_key_hostname.pub user@hostname
```

### ステップ3: SSH設定を更新

```bash
# ~/.ssh/configに追加
Host hostname1
  IdentityFile ~/.ssh/fnb_key_hostname1
  IdentitiesOnly yes

Host hostname2
  IdentityFile ~/.ssh/fnb_key_hostname2
  IdentitiesOnly yes
```

### ステップ4: テストとクリーンアップ

```bash
# 接続をテスト
ssh user@hostname1
ssh user@hostname2

# .envファイルからパスワードを削除
# 他の環境変数が必要な場合はファイルを保持
```

## トラブルシューティング

### SSH鍵の問題

```bash
# SSHエージェントを確認
ssh-add -l

# 必要に応じてエージェントにキーを追加
ssh-add ~/.ssh/fnb_key

# 接続をテスト
ssh -v user@server.com
```

### 権限の問題

```bash
# SSHディレクトリ権限を修正
chmod 700 ~/.ssh
chmod 600 ~/.ssh/config
chmod 600 ~/.ssh/fnb_key*
chmod 644 ~/.ssh/fnb_key*.pub
```

### キーチェーンの問題（macOS）

```bash
# 保存されたパスワードを一覧表示
security dump-keychain | grep fnb-ssh

# 保存されたパスワードを更新
security delete-generic-password -s "fnb-ssh" -a "user@server.com"
security add-generic-password -s "fnb-ssh" -a "user@server.com" -w "newpassword"
```

## 関連項目

- [設定ガイド](configuration.md) - fnbの基本設定
- [例](examples.md) - セキュリティを考慮した設定例
- [貢献](../development/contributing.md) - 開発時のセキュリティ考慮事項
