# ==========================================================
# 01_agentcore_code_interpreter_agent.py
# ==========================================================

import os
import json
from bedrock_agentcore import BedrockAgentCoreApp
from bedrock_agentcore.tools.code_interpreter_client import code_session
from strands import Agent, tool
from strands.models import BedrockModel


# ==========================================================
# 1. System Prompt
# ==========================================================
SYSTEM_PROMPT = """You are a helpful AI assistant that validates all answers through code execution.

VALIDATION PRINCIPLES:
1. When making claims about code, algorithms, or calculations - write code to verify them
2. Use execute_python to test mathematical calculations, algorithms, and logic
3. Create test scripts to validate your understanding before giving answers
4. Always show your work with actual code execution
5. If uncertain, explicitly state limitations and validate what you can

APPROACH:
- If asked about a programming concept, implement it in code to demonstrate
- If asked for calculations, compute them programmatically AND show the code
- If implementing algorithms, include test cases to prove correctness
- Document your validation process for transparency
- The state is maintained between executions, so you can refer to previous results

TOOL AVAILABLE:
- execute_python: Run Python code and see output
"""


# ==========================================================
# 2. Define Code Interpreter Tool
# ==========================================================
@tool
def execute_python(code: str, description: str = "") -> str:
    """Execute Python code in an isolated Code Interpreter session."""
    if description:
        code = f"# {description}\n{code}"

    print(f"\n[CodeInterpreter] Executing code:\n{code}\n")

    with code_session(os.getenv("REGION", "us-east-1")) as code_client:
        response = code_client.invoke(
            "executeCode",
            {"code": code, "language": "python", "clearContext": False},
        )

        for event in response["stream"]:
            if "event" in event and event["event"] == "end":
                break
            if "result" in event:
                return json.dumps(event["result"], indent=2)

    return json.dumps({"error": "No result received"}, indent=2)


# ==========================================================
# 3. Configure AgentCore App and Strands Agent
# ==========================================================
app = BedrockAgentCoreApp()

model = BedrockModel(
    model_id=os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-lite-v1:0"),
    region_name=os.getenv("REGION", "us-east-1"),
)

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[execute_python],
)


# ==========================================================
# 4. Define the entrypoint
# ==========================================================
@app.entrypoint
def invoke(payload):
    """Main entrypoint — process incoming request and execute code validation"""
    query = payload.get("prompt", "Can all the planets in the solar system fit between the earth and moon?")
    print(f"\n[Invoke] Received payload: {payload}")

    result = agent(query)

    return {
        "input": query,
        "result": result.message,
    }


# ==========================================================
# 5. Run in AgentCore runtime
# ==========================================================
if __name__ == "__main__":
    app.run()

