#!/usr/bin/env python3
"""
Hierarchy Processing Test Examples

このファイルで階層処理の動作を確認できます。
CLIを使わずに、直接Pythonコードでテストできます。
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from strataregula.hierarchy import (
    HierarchyMerger, 
    MergeStrategy, 
    HierarchyProcessor
)
import yaml


def test_basic_merge():
    """基本的なマージ処理のテスト"""
    print("=== 基本的なマージ処理のテスト ===")
    
    # 基本設定
    base_config = {
        'app': {
            'name': 'MyApp',
            'version': '1.0.0',
            'database': {
                'host': 'localhost',
                'port': 5432
            }
        },
        'features': ['auth', 'logging']
    }
    
    # オーバーライド設定
    override_config = {
        'app': {
            'version': '2.0.0',  # 基本型は置き換え
            'database': {
                'port': 5433,    # 階層内の基本型は置き換え
                'ssl': True      # 新しい設定を追加
            }
        },
        'features': ['auth', 'logging', 'caching']  # リストは追加
    }
    
    # スマート戦略でマージ
    merger = HierarchyMerger(MergeStrategy.SMART)
    result = merger.merge(base_config, override_config)
    
    print("基本設定:")
    print(yaml.dump(base_config, default_flow_style=False, allow_unicode=True))
    print("\nオーバーライド設定:")
    print(yaml.dump(override_config, default_flow_style=False, allow_unicode=True))
    print("\nマージ結果:")
    print(yaml.dump(result, default_flow_style=False, allow_unicode=True))
    
    return result


def test_environment_merge():
    """環境別設定マージのテスト"""
    print("\n=== 環境別設定マージのテスト ===")
    
    # 基本設定
    base_config = {
        'app': {
            'name': 'MyApp',
            'debug': False,
            'database': {
                'host': 'localhost',
                'port': 5432
            }
        }
    }
    
    # 開発環境設定
    dev_config = {
        'environment': 'development',
        'app': {
            'debug': True,
            'database': {
                'host': 'dev-db.local',
                'port': 5433
            }
        }
    }
    
    # 本番環境設定
    prod_config = {
        'environment': 'production',
        'app': {
            'debug': False,
            'database': {
                'host': 'prod-db.company.com',
                'port': 5432,
                'ssl': True,
                'max_connections': 100
            }
        }
    }
    
    # 環境別マージ
    merger = HierarchyMerger(MergeStrategy.SMART)
    
    # 開発環境
    dev_result = merger.merge_with_environment(base_config, dev_config, 'development')
    print("開発環境設定:")
    print(yaml.dump(dev_result, default_flow_style=False, allow_unicode=True))
    
    # 本番環境
    prod_result = merger.merge_with_environment(base_config, prod_config, 'production')
    print("\n本番環境設定:")
    print(yaml.dump(prod_result, default_flow_style=False, allow_unicode=True))
    
    return dev_result, prod_result


def test_list_merge_strategies():
    """リストマージ戦略のテスト"""
    print("\n=== リストマージ戦略のテスト ===")
    
    base_list = [
        {'id': 1, 'name': 'Item 1'},
        {'id': 2, 'name': 'Item 2'}
    ]
    
    override_list = [
        {'id': 1, 'name': 'Item 1 Updated'},  # 既存アイテムを更新
        {'id': 3, 'name': 'Item 3'}           # 新しいアイテムを追加
    ]
    
    strategies = [
        MergeStrategy.DEEP_COPY,
        MergeStrategy.MERGE,
        MergeStrategy.APPEND,
        MergeStrategy.SMART
    ]
    
    for strategy in strategies:
        print(f"\n--- {strategy.value} 戦略 ---")
        merger = HierarchyMerger(strategy)
        result = merger.merge(base_list, override_list)
        print("結果:")
        print(yaml.dump(result, default_flow_style=False, allow_unicode=True))


def test_conflict_resolution():
    """競合解決のテスト"""
    print("\n=== 競合解決のテスト ===")
    
    base_config = {
        'priority': 'low',
        'timeout': 30,
        'retries': 3
    }
    
    conflicts = [
        {
            'priority': 'medium',
            'timeout': 60,
            'priority_level': 'medium'
        },
        {
            'priority': 'high',
            'timeout': 120,
            'retries': 5,
            'priority_level': 'high'
        }
    ]
    
    # 優先順位を指定して競合を解決
    merger = HierarchyMerger(MergeStrategy.SMART)
    result = merger.resolve_conflicts(
        base_config, 
        conflicts, 
        priority_order=['low', 'medium', 'high']
    )
    
    print("基本設定:")
    print(yaml.dump(base_config, default_flow_style=False, allow_unicode=True))
    print("\n競合設定:")
    for i, conflict in enumerate(conflicts):
        print(f"競合 {i+1}:")
        print(yaml.dump(conflict, default_flow_style=False, allow_unicode=True))
    print("\n解決結果:")
    print(yaml.dump(result, default_flow_style=False, allow_unicode=True))
    
    return result


def test_processor_integration():
    """プロセッサ統合のテスト"""
    print("\n=== プロセッサ統合のテスト ===")
    
    # 設定ファイルの内容（実際のファイルの代わり）
    base_yaml = """
app:
  name: MyApp
  version: 1.0.0
  database:
    host: localhost
    port: 5432
features:
  - auth
  - logging
"""
    
    env_yaml = """
environment: development
app:
  debug: true
  database:
    host: dev-db.local
    port: 5433
features:
  - caching
  - monitoring
"""
    
    # プロセッサを使用
    processor = HierarchyProcessor(MergeStrategy.SMART)
    
    # 基本設定を読み込み
    base_config = yaml.safe_load(base_yaml)
    env_config = yaml.safe_load(env_yaml)
    
    # 環境設定を追加
    processor.environment_configs['development'] = env_config
    processor.base_config = base_config
    
    # マージ実行
    result = processor.get_merged_config(target_env='development')
    
    print("基本設定:")
    print(yaml.dump(base_config, default_flow_style=False, allow_unicode=True))
    print("\n開発環境設定:")
    print(yaml.dump(env_config, default_flow_style=False, allow_unicode=True))
    print("\nマージ結果:")
    print(yaml.dump(result, default_flow_style=False, allow_unicode=True))
    
    # 設定概要を表示
    summary = processor.get_config_summary()
    print("\n設定概要:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    return result


def main():
    """メイン関数"""
    print("階層処理テストを開始します...\n")
    
    try:
        # 各テストを実行
        test_basic_merge()
        test_environment_merge()
        test_list_merge_strategies()
        test_conflict_resolution()
        test_processor_integration()
        
        print("\n=== すべてのテストが完了しました ===")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
