import logging
from langchain_community.tools import DuckDuckGoSearchResults
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

# ==========================================================
# ① Task Decomposition Node
# ==========================================================
class TaskDecompositionNode:
    """ユーザー目標を階層的に分解"""

    def __init__(self, model):
        self.model = model  # this is a strands.Agent

    def __call__(self, state):
        goal = state["goal"]
        logger.info("🧠 [TaskDecompositionNode] START")
        logger.info(f"🎯 Goal: {goal}")

        prompt = f"""
あなたは優秀なタスク分解プランナーです。
目標「{goal}」を実現するための大項目とサブタスクを整理してください。
"""

        try:
            # 🔹 Agent は __call__ で実行し、結果は AgentResult
            result = self.model(prompt)
            text = str(result)
            logger.info("✅ [TaskDecompositionNode] Completed successfully")
            logger.debug(f"[TaskDecompositionNode] Output:\n{text[:1000]}")
            return {"tasks": text}
        except Exception as e:
            logger.error("❌ [TaskDecompositionNode] Failed")
            logger.exception(e)
            return {"tasks": f"⚠️ エラー: {e}"}


# ==========================================================
# ② Research Node
# ==========================================================
class ResearchNode:
    """各タスクの関連情報をDuckDuckGoから取得"""

    def __init__(self, max_results=3, output_format="list"):
        self.search_tool = DuckDuckGoSearchResults(
            output_format=output_format,
            num_results=max_results,
        )

    def __call__(self, state):
        tasks = state.get("tasks", "")
        if not isinstance(tasks, str):
            tasks = str(tasks)

        logger.info("🔍 [ResearchNode] START")
        logger.debug(f"[ResearchNode] Input tasks:\n{tasks[:500]}")

        summaries = []

        for line in tasks.splitlines():
            query = line.strip()
            if not query:
                continue
            logger.info(f"🔎 [ResearchNode] Searching for: {query}")
            try:
                results = self.search_tool.invoke(query)
                if isinstance(results, str):
                    summaries.append(f"### {query}\n{results}")
                elif isinstance(results, list):
                    formatted = "\n".join(
                        [f"- {r.get('title', 'No title')} ({r.get('link', '')})"
                         for r in results]
                    )
                    summaries.append(f"### {query}\n{formatted}")
                else:
                    summaries.append(f"### {query}\n{str(results)}")
                logger.info(f"✅ [ResearchNode] Search completed for: {query}")
            except Exception as e:
                logger.warning(f"⚠️ [ResearchNode] Search failed for '{query}': {e}")
                summaries.append(f"### {query}\n⚠️ 検索中にエラー: {e}")

        result_text = "\n\n".join(summaries)
        logger.info("✅ [ResearchNode] Completed all searches")
        logger.debug(f"[ResearchNode] Output:\n{result_text[:1000]}")

        return {"research": result_text}


# ==========================================================
# ③ Plan Synthesis Node
# ==========================================================
class PlanSynthesisNode:
    """全体プランをまとめる"""

    def __init__(self, model):
        self.model = model  # strands.Agent

    def __call__(self, state):
        tasks = state.get("tasks", "")
        research = state.get("research", "")

        if not isinstance(tasks, str):
            tasks = str(tasks)
        if not isinstance(research, str):
            research = str(research)

        logger.info("🧩 [PlanSynthesisNode] START")
        logger.debug(f"[PlanSynthesisNode] Input (tasks + research) sizes: "
                     f"{len(tasks)} chars, {len(research)} chars")

        prompt = f"""
以下のタスク分解とリサーチ情報をもとに、実行可能なプランを統合してください。

# タスク分解:
{tasks}

# 調査情報:
{research}

出力フォーマット:
1. 目的の要約
2. 実行ステップ（階層構造）
3. 参考情報のまとめ
"""

        try:
            result = self.model(prompt)
            result_text = str(result)
            logger.info("✅ [PlanSynthesisNode] Completed successfully")
            logger.debug(f"[PlanSynthesisNode] Output:\n{result_text[:1000]}")
            return {"final_plan": result_text}
        except Exception as e:
            logger.error("❌ [PlanSynthesisNode] Failed")
            logger.exception(e)
            return {"final_plan": f"⚠️ エラー: {e}"}
