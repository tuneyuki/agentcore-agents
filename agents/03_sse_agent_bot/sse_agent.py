import os
import logging
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# ==========================================================
# Logging
# ==========================================================
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# ==========================================================
# Model setup
# ==========================================================
chat = ChatBedrock(
    model_id=os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-lite-v1:0"),
    region_name=os.getenv("REGION", "us-east-1"),
    provider="amazon",
)

# ==========================================================
# Define State schema
# ==========================================================
class State(TypedDict):
    goal: str
    tasks: str
    research: str
    plan: str

# ==========================================================
# Define nodes
# ==========================================================
def decompose(state: State):
    goal = state["goal"]
    logger.info(f"[decompose] goal={goal}")
    res = chat.invoke([HumanMessage(content=f"Break down the goal '{goal}' into clear steps.")])
    return {"tasks": res.content}

def research(state: State):
    tasks = state["tasks"]
    logger.info(f"[research] tasks={tasks[:60]}...")
    res = chat.invoke([HumanMessage(content=f"Do quick research for these tasks:\n{tasks}")])
    return {"research": res.content}

def synthesize(state: State):
    goal = state["goal"]
    tasks = state["tasks"]
    research_summary = state["research"]
    logger.info("[synthesize] combining info")
    res = chat.invoke([HumanMessage(content=f"Combine into a final plan for '{goal}'.\n\nTasks:\n{tasks}\n\nResearch:\n{research_summary}")])
    return {"plan": res.content}

# ==========================================================
# Build LangGraph
# ==========================================================
workflow = StateGraph(State)
workflow.add_node("decompose", decompose)
workflow.add_node("research", research)
workflow.add_node("synthesize", synthesize)

workflow.add_edge(START, "decompose")
workflow.add_edge("decompose", "research")
workflow.add_edge("research", "synthesize")
workflow.add_edge("synthesize", END)

graph = workflow.compile()

# ==========================================================
# AgentCore App
# ==========================================================
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload, context=None):
    goal = payload.get("prompt", "No goal provided")
    state = {"goal": goal}
    logger.info(f"🚀 Starting LangGraph workflow for goal: {goal}")

    try:
        for partial_state in graph.stream(state):  # ✅ only one value per iteration
            # partial_state is the latest incremental state dict
            for key, value in partial_state.items():
                if key == "goal":
                    continue  # skip the static field
                yield f'data: {{"event": "update:{key}", "content": "{value}"}}\n\n'
                logger.info(f"✅ Updated field '{key}'")

        # after stream finishes, get final state
        final_state = graph.invoke(state)
        final_plan = final_state.get("plan", "(no final plan)")
        yield f'data: {{"event": "final", "content": "{final_plan}"}}\n\n'
        logger.info("🎉 Workflow complete.")

    except Exception as e:
        logger.exception("❌ Error during workflow execution.")
        yield f'data: {{"event": "error", "content": "{str(e)}"}}\n\n'


if __name__ == "__main__":
    logger.info("🧩 Running SSE LangGraph agent locally...")
    app.run()
