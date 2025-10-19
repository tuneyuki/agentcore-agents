# 05_agent_with_auth.py
import os
import logging
from bedrock_agentcore import BedrockAgentCoreApp
from openai import OpenAI

# ==========================================================
# Setup
# ==========================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = BedrockAgentCoreApp()


# ==========================================================
# Entry Point
# ==========================================================
@app.entrypoint
def invoke(payload, context=None):
    user_message = payload.get("prompt", "Hello!")
    logger.info(f"🟢 Prompt: {repr(user_message)}")

    # 追加: contextからトークン情報を取得（存在する場合のみ）
    if context and "identity" in context:
        identity = context["identity"]
        logger.info(f"🔒 Authenticated User: {identity}")

    result = client.responses.create(
        model="gpt-4.1-mini",
        input=user_message
    )

    raw_output = result.output_text.replace("\n", "\\n")
    logger.info(f"🔵 Output(raw): {raw_output}")

    return {"result": result.output_text}



# ==========================================================
# Run locally
# ==========================================================
if __name__ == "__main__":
    logger.info("Starting Bedrock AgentCore App...")
    app.run()
