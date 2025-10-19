import boto3
import json
import uuid

# ==========================================================
# 設定
# ==========================================================
REGION = "us-east-1"
ACCOUNT_ID = "180048383118"
AGENT_RUNTIME_ARN = "arn:aws:bedrock-agentcore:us-east-1:180048383118:runtime/fastapi_agent_runtime-5gAW0D4DnM"

# ==========================================================
# クライアント作成
# ==========================================================
agent_core_client = boto3.client("bedrock-agentcore", region_name=REGION)

# ==========================================================
# 入力ペイロード
# ==========================================================
payload = json.dumps({
    "input": {"prompt": "Explain machine learning in simple terms"}
})

# セッションIDは33文字以上（ユニーク値にする）
runtime_session_id = f"session-{uuid.uuid4().hex}"

# ==========================================================
# エージェント呼び出し
# ==========================================================
response = agent_core_client.invoke_agent_runtime(
    agentRuntimeArn=AGENT_RUNTIME_ARN,
    runtimeSessionId=runtime_session_id,
    payload=payload,
    qualifier="DEFAULT"
)

# ==========================================================
# 応答取得と整形
# ==========================================================
response_body = response["response"].read()
response_data = json.loads(response_body)

print("✅ Agent invoked successfully!")
print("🧠 Agent Response:")
print(json.dumps(response_data, indent=2, ensure_ascii=False))
