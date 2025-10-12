import os
import logging
import traceback
from dotenv import load_dotenv
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from graph.workflow import create_workflow

# ==========================================================
# 初期設定
# ==========================================================
load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# boto / urllib の詳細デバッグを抑制
logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("boto3").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# ログ設定
console_handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


# ==========================================================
# Bedrock AgentCore 設定
# ==========================================================
app = BedrockAgentCoreApp()

REGION = os.getenv("REGION", "us-east-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-lite-v1:0")

try:
    logger.info(f"🧠 Initializing Bedrock model: {MODEL_ID} ({REGION})")
    model = BedrockModel(model_id=MODEL_ID, region_name=REGION)
    agent = Agent(model=model)
    logger.info("✅ Bedrock model and Strands agent initialized successfully.")
except Exception as e:
    logger.error("❌ Failed to initialize BedrockModel or Agent.")
    logger.error(traceback.format_exc())
    raise e


# ==========================================================
# エントリーポイント
# ==========================================================
@app.entrypoint
def invoke(payload):
    """
    LangGraphベースのタスク分解プランナー
    """
    logger.info("🚀 Received invoke request.")
    user_goal = payload.get("prompt", "")
    logger.info(f"🎯 User goal: {user_goal}")

    try:
        # LangGraph構築
        logger.info("🔧 Building workflow graph...")
        graph = create_workflow(agent)

        # 初期状態
        state = {"goal": user_goal}

        # グラフ実行
        logger.info("🧩 Running graph execution via LangGraph.invoke() ...")
        result = graph.invoke(state)
        logger.info("✅ Graph execution finished.")

        # 結果確認
        if not isinstance(result, dict):
            logger.warning(f"⚠️ Unexpected result type: {type(result)}")
            result = {"final_plan": str(result)}

        final_plan = result.get("final_plan", "（結果なし）")

        logger.info("✅ Workflow completed successfully.")
        return {
            "goal": user_goal,
            "plan": final_plan
        }

    except Exception as e:
        logger.error("❌ Error during LangGraph execution:")
        logger.error(traceback.format_exc())
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }


# ==========================================================
# ローカル実行用
# ==========================================================
if __name__ == "__main__":
    logger.info("🧩 Running agent locally (debug mode).")
    try:
        app.run()
    except Exception as e:
        logger.error("❌ Fatal error while running app.")
        logger.error(traceback.format_exc())
        raise e
