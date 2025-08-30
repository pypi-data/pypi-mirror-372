# Hash Algorithm Architecture Docs

本フォルダは、ハッシュ/インターニング/高速化に関する設計資料のハブです。立場の異なる2文書を**並列に**提示します。

## 📚 資料
1. **設計パターン集（クラシック/OOP志向）**  
   [HASH_ALGORITHM_PACKAGING_PATTERNS.md](HASH_ALGORITHM_PACKAGING_PATTERNS.md)

2. **現代的批判と再設計（関数型/型安全/非同期志向）**  
   [MODERN_HASH_ARCHITECTURE_CRITIQUE.md](MODERN_HASH_ARCHITECTURE_CRITIQUE.md)

## 🧭 読み方
- **体系で掴む** → パターン集
- **最新思想で掴む** → 批判と再設計
- **方針決定時は両方を読み比べ**、要件に応じて折衷/選択

## 📋 設計の要点

### クラシックアプローチ (PATTERNS.md)
- **Strategy + Factory**: 用途別分類
- **Plugin Registry**: 拡張性重視
- **Performance-Driven**: 性能最適化
- **Microservice**: 分散・スケーラビリティ

### モダンアプローチ (CRITIQUE.md)
- **Functional Pipeline**: 関数型コンポジション
- **Type-Level Selection**: 型安全性
- **Reactive Streaming**: 非同期処理
- **Zero-Cost Abstraction**: パフォーマンス

## 🎯 実装推奨

| 要件 | 推奨アプローチ | 理由 |
|------|-------------|------|
| **ライブラリ設計** | モダン + 型安全性 | コンパイル時保証 |
| **レガシー統合** | クラシック + アダプター | 段階的移行 |
| **高性能システム** | モダン + ゼロコスト | 最適化 |
| **エンタープライズ** | クラシック + 既存パターン | 保守性 |

## 🔗 関連
- 歴史とビジョン: [../history/STRATAREGULA_VISION.md](../history/STRATAREGULA_VISION.md)
- StrataRegula Ecosystem の設計思想とハッシュアーキテクチャの関係

---

**ハブ作成**: Claude Code  
**作成日**: 2025-08-28  
**対象**: StrataRegula v0.3.0 Hash Architecture Integration