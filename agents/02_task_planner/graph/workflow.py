# graph/workflow.py
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from .nodes import TaskDecompositionNode, ResearchNode, PlanSynthesisNode


# グラフ全体の状態スキーマ
class State(TypedDict):
    goal: str
    tasks: str
    research: str
    final_plan: str


def create_workflow(model):
    # StateGraphインスタンスを生成
    workflow = StateGraph(State)

    # ノードを追加（callableオブジェクトでOK）
    workflow.add_node("decompose", TaskDecompositionNode(model))
    workflow.add_node("research", ResearchNode())
    workflow.add_node("synthesize", PlanSynthesisNode(model))

    # ノードの接続
    workflow.add_edge(START, "decompose")
    workflow.add_edge("decompose", "research")
    workflow.add_edge("research", "synthesize")
    workflow.add_edge("synthesize", END)

    # 実行可能なワークフローを返す
    chain = workflow.compile()
    return chain
