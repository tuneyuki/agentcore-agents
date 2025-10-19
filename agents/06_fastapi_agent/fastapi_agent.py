from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
from openai import OpenAI
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# ==========================================================
# Setup
# ==========================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="OpenAI Agent Server", version="1.0.0")

# OpenAIクライアント初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ==========================================================
# リクエスト／レスポンスモデル
# ==========================================================
class InvocationRequest(BaseModel):
    input: Dict[str, Any]

class InvocationResponse(BaseModel):
    output: Dict[str, Any]


# ==========================================================
# エージェント呼び出しAPI
# ==========================================================
@app.post("/invocations", response_model=InvocationResponse)
async def invoke_agent(request: InvocationRequest):
    try:
        user_message = request.input.get("prompt", "")
        if not user_message:
            raise HTTPException(
                status_code=400,
                detail="No prompt found in input. Please provide a 'prompt' key in the input."
            )

        logger.info(f"🟢 Prompt: {repr(user_message)}")

        # OpenAI Responses API呼び出し
        result = client.responses.create(
            model="gpt-4.1-mini",
            input=user_message
        )

        raw_output = result.output_text.replace("\n", "\\n")
        logger.info(f"🔵 Output(raw): {raw_output}")

        response = {
            "message": result.output_text,
            "timestamp": datetime.utcnow().isoformat()
        }

        return InvocationResponse(output=response)

    except Exception as e:
        logger.exception("Agent processing failed")
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")


# ==========================================================
# ヘルスチェックAPI
# ==========================================================
@app.get("/ping")
async def ping():
    return {"status": "healthy"}


# ==========================================================
# ローカル起動
# ==========================================================
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting OpenAI FastAPI Server on port 8080 ...")
    uvicorn.run(app, host="0.0.0.0", port=8080)
