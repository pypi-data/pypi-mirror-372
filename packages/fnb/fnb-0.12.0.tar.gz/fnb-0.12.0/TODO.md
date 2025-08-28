# fnb - Development TODO List

プロジェクト全体を分析した結果に基づく、**未完了**のGitLab issue提案です。優先度と工数を考慮して分類しました。

> **✅ 完了済みタスク**: [DONE.md](./DONE.md) を参照

## 🔴 優先度: 高 (High Priority)

### 1. 設定検証の強化 (Enhanced Configuration Validation)
**現状**: 基本的なPydantic検証のみ
**課題**:
- パス存在確認が実行時のみ
- ホスト接続確認なし
- rsyncオプションの妥当性検証なし

**工数**: 中（2-3日）

### ~~2. ログ機能の実装 (Implement Logging System)~~ ✅ **COMPLETED** (2025-08-28)
**現状**: ~~print文ベースの出力のみ~~ → loguru基盤の構造化ログシステム完備
**完了内容**:
- 構造化ログシステム実装（loguru）
- CLI統合（--log-level, --verbose, --quiet）
- 実行履歴の自動保存・ローテーション
- ユーザー出力とログの完全分離
- プラットフォーム対応ログファイル管理

**実績工数**: 3日
**GitLab Issue**: [#44 feat: implement logging system with loguru](https://gitlab.com/qumasan/fnb/-/issues/44) ✅ **CLOSED**

## 🟡 優先度: 中 (Medium Priority)

### 3. プログレス表示機能 (Progress Display for Large Transfers)
**現状**: rsync実行中の進捗が見えない
**課題**:
- 大容量ファイル転送時の状況不明
- 推定完了時間なし

**工数**: 中（2-3日）

### 4. 設定ファイル管理機能の拡張 (Configuration Management Enhancement)
**現状**: 基本的な設定読み込みのみ
**課題**:
- 設定ファイルの分割・統合機能なし
- プロファイル（環境別設定）機能なし
- 設定テンプレート管理なし

**工数**: 大（4-5日）

### 5. バックアップ履歴・統計機能 (Backup History and Statistics)
**現状**: 実行結果の記録なし
**課題**:
- 実行履歴の保存なし
- 転送統計情報なし
- 失敗率などの分析機能なし

**工数**: 大（4-5日）

## 🟢 優先度: 低 (Low Priority / Enhancement)

### 6. 並列実行機能 (Parallel Execution Support)
**現状**: タスクの逐次実行のみ
**課題**:
- 複数タスクの同時実行不可
- CPU/ネットワーク効率化の余地

**工数**: 大（5-6日）

### 7. Web UI / Dashboard (Optional Web Interface)
**現状**: CLIのみ
**課題**:
- 視覚的なステータス確認機能なし
- ログ閲覧の利便性低い

**工数**: 特大（1-2週間）

### 8. 高度な同期戦略 (Advanced Synchronization Strategies)
**現状**: rsyncベースの基本同期のみ
**課題**:
- 増分バックアップ機能なし
- 重複排除機能なし
- バージョニング機能なし

**工数**: 特大（1-2週間）

---

## 📊 推奨開発順序

**Phase 1 (即効性重視)**:
1. 設定検証強化
2. ~~ログ機能実装~~ ✅ **COMPLETED**

**Phase 2 (ユーザビリティ向上)**:
3. プログレス表示
4. 設定管理機能拡張

**Phase 3 (機能拡張)**:
5. バックアップ履歴・統計
6. 並列実行機能

**Phase 4 (長期的改善)**:
7. Web UI
8. 高度同期戦略

**総課題数**: 8個
**推定総工数**: 20-30日

---

## 🎯 実装状況サマリー

### 🔄 実装待ち (GitLab Issues未作成)
1. 設定検証の強化
2. ~~ログ機能の実装~~ ✅ **COMPLETED**
3. プログレス表示機能
4. 設定ファイル管理機能の拡張
5. バックアップ履歴・統計機能
6. 並列実行機能
7. Web UI / Dashboard
8. 高度な同期戦略

---

## 📚 ドキュメント改善マイルストーン (Documentation Enhancement Milestone)

PyPI配信対応に伴い、ユーザーと開発者の両方をサポートする包括的なドキュメント整備を実装中です。

### 🔴 フェーズ1: 基本ドキュメント整備（優先度：High）

**[#24 README.md包括的更新](https://gitlab.com/qumasan/fnb/-/issues/24)**
- PyPIインストール手順の追加
- 既存Gitインストール手順との統合
- 基本使用例の更新

**[#25 インストールガイド専用ドキュメント作成](https://gitlab.com/qumasan/fnb/-/issues/25)**
- INSTALLATION.mdファイル作成
- プラットフォーム別セットアップ手順
- トラブルシューティング基本事項

### 🟡 フェーズ2: 開発者向けドキュメント（優先度：High）

**[#26 CONTRIBUTING.md作成](https://gitlab.com/qumasan/fnb/-/issues/26)**
- 開発参加ガイドライン
- コード規約とPRプロセス
- 開発環境構築手順

**[#27 RELEASING.md作成](https://gitlab.com/qumasan/fnb/-/issues/27)**
- PyPI配信完全手順書
- TestPyPI検証プロセス
- バージョン管理ワークフロー

**[#28 TROUBLESHOOTING.md作成](https://gitlab.com/qumasan/fnb/-/issues/28)**
- よくあるビルドエラー集
- PyPI配信トラブル対応
- 依存関係問題解決策

### 🟢 フェーズ3: MkDocsサイト拡張（優先度：Medium）

**[#29 MkDocsインストールガイドページ追加](https://gitlab.com/qumasan/fnb/-/issues/29)**
- 詳細インストール手順
- プラットフォーム別注意事項
- アップグレード手順

**[#30 MkDocs配信プロセス解説ページ作成](https://gitlab.com/qumasan/fnb/-/issues/30)**
- 開発者向け配信フロー
- 自動化CI/CDプロセス
- リリース戦略説明

**[#31 MkDocs API仕様ドキュメント拡張](https://gitlab.com/qumasan/fnb/-/issues/31)**
- API参照の拡充
- メタデータ情報追加
- 使用例とサンプルコード

### 🔵 フェーズ4: コード品質とメンテナンス（優先度：Medium）

**[#32 docstring完全性向上](https://gitlab.com/qumasan/fnb/-/issues/32)**
- 全モジュールdocstring監査
- Google形式統一
- 使用例の追加

**[#33 型ヒント完全性チェック](https://gitlab.com/qumasan/fnb/-/issues/33)**
- 既存コード型ヒント検証
- mypy設定調整
- 型安全性向上

### ⚪ フェーズ5: ユーザーエクスペリエンス向上（優先度：Low）

**[#34 バージョン履歴とCHANGELOG連携](https://gitlab.com/qumasan/fnb/-/issues/34)**
- MkDocsでのCHANGELOG表示
- リリースノート自動化
- 破壊的変更明確化

**[#35 サンプル設定とテンプレート更新](https://gitlab.com/qumasan/fnb/-/issues/35)**
- PyPI配信後使用例
- assetsテンプレート見直し
- チュートリアル形式ガイド

**ドキュメント改善総課題数**: 12個（関連issue#18から分割）
**推定総工数**: 8-12日

---

### 📈 次のアクション
1. **ドキュメント整備**: フェーズ1（基本）→フェーズ2（開発者）の順で実装
2. **新機能開始**: 設定検証の強化のGitLab Issue作成（ログ機能実装完了済み）
3. **フェーズ1継続**: 残り優先度高機能（設定検証強化）の実装
4. **継続運用**: v0.11.2の安定運用と改善点収集

## 🎯 現在のプロジェクト状況 (v0.11.2)

- **Test Coverage**: 87% (目標83%+を上回って達成済み) ✅
- **PyPI配信**: 本番運用開始済み ✅
- **自動化ワークフロー**: TestPyPI自動配信・PyPI手動配信 ✅
- **Release Management**: 完全自動化ワークフロー実装済み ✅
- **Documentation**: 開発・リリース・配信手順完全文書化 ✅
- **Renovate Integration**: 自動依存関係管理・セキュリティスキャン ✅ **NEW in v0.11.0**
- **Internationalization**: 多言語ドキュメント基盤・英語優先 ✅ **NEW in v0.11.0**
- **Release Notes Management**: 構造化リリースノート・ユーザーフレンドリー ✅ **NEW in v0.11.0**
- **ReadTheDocs Integration**: バージョン管理ドキュメント・自動ビルド ✅ **NEW in v0.11.2**
- **Structured Logging System**: loguru基盤・CLI統合・自動ローテーション ✅ **NEW in v0.11.3-dev**

**完了済みタスク詳細**: [DONE.md](./DONE.md) を参照

---

*最終更新: 2025-08-28 ログ機能実装完了・v0.11.3-dev時点*
