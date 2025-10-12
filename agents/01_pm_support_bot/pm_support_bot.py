import os
import uuid
import time
import logging
from dotenv import load_dotenv
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemoryClient
from strands import Agent
from strands.models import BedrockModel

# ==========================================================
# 初期設定
# ==========================================================
load_dotenv()

# Prefer DEBUG while wiring memory; switch back to INFO later
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()

REGION = os.getenv("REGION", "us-east-1")
memory_client = MemoryClient(region_name=REGION)


# Memory設定（name でも id でもOK。name の場合は id に解決）
MEMORY_ID = os.getenv("BEDROCK_AGENTCORE_MEMORY_ID")
logger.info(f"Using MEMORY_ID={MEMORY_ID}")

# モデル設定
model = BedrockModel(
    model_id=os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-lite-v1:0"),
    region_name=REGION,
)
agent = Agent(model=model)

# ==========================================================
# ユーティリティ関数
# ==========================================================

def save_event(memory_id, actor_id, session_id, text, role="USER"):
    """短期メモリにイベントを保存（最終決定版）"""
    try:
        response = memory_client.create_event(
            memory_id=memory_id,
            actor_id=actor_id,
            session_id=session_id,
            messages=[(text, role)],   # ✅ timestamp は不要
        )
        logger.debug(f"create_event response: {response}")
        logger.info("✅ Event stored successfully")
    except Exception:
        logger.exception("❌ Failed to store event")


def _extract_texts_from_event(e):
    """
    Handle both modern ('messages') and legacy ('payload') shapes.
    Returns a list of strings for that event.
    """
    out = []
    # Newer shape: messages=[(text, role)] or list of dicts
    msgs = e.get("messages")
    if msgs:
        for m in msgs:
            # Could be tuple/list (text, role) or dict {"text":..., "role":...}
            if isinstance(m, (list, tuple)) and len(m) >= 1:
                out.append(str(m[0]))
            elif isinstance(m, dict) and "text" in m:
                out.append(str(m["text"]))
    # Legacy shape: payload -> conversational -> content.text
    if not out and e.get("payload"):
        for p in e["payload"]:
            conv = p.get("conversational")
            if conv and conv.get("content") and "text" in conv["content"]:
                out.append(str(conv["content"]["text"]))
    return out

def list_recent_events(memory_id, actor_id, session_id, limit=5):
    """短期メモリから直近の会話を取得"""
    try:
        events = memory_client.list_events(
            memory_id=memory_id,
            actor_id=actor_id,
            session_id=session_id,
            max_results=limit,
        )
        logger.debug(f"list_events returned {len(events)} events")
        lines = []
        for e in events:
            lines.extend(_extract_texts_from_event(e))
        return lines
    except Exception as e:
        logger.exception("⚠️ Failed to list events")
        return []

def retrieve_longterm(memory_id, namespace, query, top_k=5):
    """Long-term Memoryから情報を検索（要：ACTIVE な戦略 & 正しい namespace）"""
    try:
        records = memory_client.retrieve_memories(
            memory_id=memory_id,
            namespace=namespace,  # e.g., "/summaries/{actorId}/{sessionId}"
            query=query,
            top_k=top_k,
        )
        logger.debug(f"retrieve_memories {namespace=} returned {len(records)} records")
        return [r.get("content", {}).get("text", "") for r in records if r.get("content")]
    except Exception:
        logger.exception("⚠️ Long-term Memory retrieval failed")
        return []

# ==========================================================
# メインエントリポイント
# ==========================================================

@app.entrypoint
def invoke(payload):
    """
    📘 プロジェクトマネジメント支援エージェント
    - 会話を短期記憶に保存 (create_event)
    - Long-term Memory（要ストラテジー）を参照
    - 過去の知見を踏まえて応答
    """
    actor_id = payload.get("actorId", "pm_default")
    session_id = payload.get("sessionId", "project_alpha")
    user_message = payload.get("prompt", "")

    logger.info(f"👤 Actor: {actor_id}, 🗂 Session: {session_id}")
    logger.info(f"💬 Message: {user_message}")

    # ====== Step 1: 短期メモリに保存 ======
    save_event(MEMORY_ID, actor_id, session_id, user_message, role="USER")

    # ====== Step 2: 過去の文脈（Short-term Memory）を参照 ======
    recent_events = list_recent_events(MEMORY_ID, actor_id, session_id, limit=10)
    context = "\n".join([f"- {e}" for e in recent_events]) if recent_events else "（なし）"

    # ====== Step 3: Long-term Memory（過去の知識）を参照 ======
    # ⚠️ These namespaces MUST match the strategies you attached when creating/upgrading the memory.
    facts_namespace     = f"project_management/facts/{actor_id}/{session_id}"
    knowledge_namespace = f"project_management/knowledge/{actor_id}"
    summary_namespace   = f"project_management/summaries/{actor_id}/{session_id}"

    facts     = retrieve_longterm(MEMORY_ID, facts_namespace,     "進捗 状況")
    knowledge = retrieve_longterm(MEMORY_ID, knowledge_namespace, "学び 改善")
    summaries = retrieve_longterm(MEMORY_ID, summary_namespace,   "要約 サマリー")

    # ====== Step 4: モデルへの入力を組み立て ======
    prompt = f"""
あなたはプロジェクトマネジメント支援アシスタントです。

プロジェクトID: {session_id}
ユーザーID: {actor_id}

最近の会話履歴:
{context}

過去の事実（Facts Memory）:
{chr(10).join(facts) if facts else "（なし）"}

過去の知識（Knowledge Memory）:
{chr(10).join(knowledge) if knowledge else "（なし）"}

過去の経過・サマリ（Summary Memory）:
{chr(10).join(summaries) if summaries else "（なし）"}

ユーザーの最新発言:
「{user_message}」

上記の文脈・履歴・知識を踏まえ、
自然で具体的な応答を返してください。
""".strip()

    model_response = agent(prompt)
    assistant_text = str(model_response)

    # ====== Step 5: 応答を短期メモリに保存 ======
    save_event(MEMORY_ID, actor_id, session_id, assistant_text, role="ASSISTANT")

    # ====== Step 6: 結果を返却 ======
    return {
        "response": assistant_text,
        "context_used": context,
        "facts_found": len(facts),
        "knowledge_found": len(knowledge),
        "summary_found": len(summaries),
    }

if __name__ == "__main__":
    app.run()
