# deploy_runtime.py
import os
from bedrock_agentcore_starter_toolkit import Runtime
from boto3.session import Session
from dotenv import load_dotenv
from bedrock_agentcore_starter_toolkit import Runtime# ==========================================================
# 環境変数読み込み
# ==========================================================
load_dotenv()  # DISCOVERY_URL, CLIENT_ID を読み込む

# AWS セッション
boto_session = Session()
region = boto_session.region_name

# 既存の実行ロールを指定（自動作成しない）
execution_role_arn = (
    f"arn:aws:iam::{boto_session.client('sts').get_caller_identity()['Account']}:role/"
    "AmazonBedrockAgentCoreRuntimeExampleRole"
)

# ==========================================================
# Runtime 設定
# ==========================================================
runtime = Runtime()
response = runtime.configure(
    entrypoint="agent_with_auth.py",             # ← 実際のエージェントファイル名
    region=region,
    agent_name="agent_with_auth",
    auto_create_execution_role=False,            # ← 既存ロールを使うのでFalse
    execution_role=execution_role_arn,           # ← 明示的に指定
    auto_create_ecr=True,
    requirements_file="requirements.txt",
    authorizer_configuration={
        "customJWTAuthorizer": {
            "discoveryUrl": os.getenv("DISCOVERY_URL"),
            "allowedClients": [os.getenv("CLIENT_ID")]
        }
    }
)

print("✅ Runtime configured using existing role.")
print(response)

# ==========================================================
# Runtime 起動
# ==========================================================
launch_response = runtime.launch()
print("🚀 AgentCore Runtime launched.")
print(launch_response)
