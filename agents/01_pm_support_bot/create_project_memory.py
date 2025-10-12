import time
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.constants import StrategyType

# Memory Client初期化
client = MemoryClient(region_name="us-east-1")

# Memory Strategies定義（AWS仕様準拠）
strategies = [
    {
        # プロジェクト事実（Semantic）
        StrategyType.SEMANTIC.value: {
            "name": "ProjectFactsStrategy",
            "description": "プロジェクト中に発生した事実・イベントを記録",
            "namespaces": ["project_management/facts/{actorId}/{sessionId}"]
        }
    },
    {
        # ナレッジ・ノウハウ（User Preference）
        StrategyType.USER_PREFERENCE.value: {
            "name": "ProjectKnowledgeStrategy",
            "description": "プロジェクトを通じて得られた知見・ノウハウを長期的に保存",
            "namespaces": ["project_management/knowledge/{actorId}"]
        }
    },
    {
        # サマリー（Summary）
        StrategyType.SUMMARY.value: {
            "name": "ProjectSummaryStrategy",
            "description": "プロジェクトの進行経過・フェーズ概要を自動サマリ化",
            "namespaces": ["project_management/summaries/{actorId}/{sessionId}"]
        }
    }
]

print("🚀 Project Management Memory作成中...")
print("📝 設定内容:")
print(f"   - Semantic: プロジェクト事実を保存")
print(f"   - User Preference: プロジェクト知見を保存")
print(f"   - Summary: プロジェクト経過をサマリ化")

timestamp = int(time.time())
memory_name = f"ProjectManagementMemory_{timestamp}"

try:
    # Memory作成（365日保持）
    memory = client.create_memory(
        name=memory_name,
        strategies=strategies,
        description="プロジェクトマネジメント支援用Memoryリソース（事実・知見・サマリ）",
    )

    memory_id = memory["id"]
    print(f"\n✅ Memory作成完了！")
    print(f"   Memory ID: {memory_id}")
    print(f"   Status: {memory['status']}")

    # 各ストラテジー確認
    print("\n📋 生成されたStrategy IDs:")
    for strategy in memory.get("strategies", []):
        print(f"   - {strategy['type']}: {strategy['strategyId']}")
        print(f"     Namespace: {strategy['namespaces'][0]}")

    # .envファイル更新
    try:
        with open(".env", "r") as f:
            content = f.read()

        if "MEMORY_ID=" in content:
            updated = content.replace(
                "MEMORY_ID=placeholder", f"MEMORY_ID={memory_id}"
            )
        else:
            updated = content + f"\nMEMORY_ID={memory_id}\n"

        with open(".env", "w") as f:
            f.write(updated)

        print(f"\n🎉 .envファイルを自動更新しました！")

    except Exception as e:
        print(f"⚠️ .envファイル更新に失敗しました: {e}")
        print(f"手動で MEMORY_ID={memory_id} を追加してください。")

except Exception as e:
    print(f"❌ Failed to create memory: {e}")
