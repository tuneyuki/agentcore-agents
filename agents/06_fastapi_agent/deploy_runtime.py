import boto3

# ==========================================================
# 設定
# ==========================================================
REGION = "us-east-1"
ACCOUNT_ID = "180048383118"
ROLE_ARN = f"arn:aws:iam::{ACCOUNT_ID}:role/AmazonBedrockAgentCoreRuntimeExampleRole"
ECR_IMAGE = f"{ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com/fastapi_agent:latest"

# ==========================================================
# Bedrock AgentCore Control クライアント作成
# ==========================================================
client = boto3.client("bedrock-agentcore-control", region_name=REGION)

# ==========================================================
# エージェントランタイム作成
# ==========================================================
response = client.create_agent_runtime(
    agentRuntimeName="fastapi_agent_runtime",
    agentRuntimeArtifact={
        "containerConfiguration": {
            "containerUri": ECR_IMAGE
        }
    },
    networkConfiguration={"networkMode": "PUBLIC"},
    roleArn=ROLE_ARN
)

print("✅ Agent Runtime created successfully!")
print(f"🪪 Agent Runtime ARN: {response['agentRuntimeArn']}")
print(f"📡 Status: {response['status']}")
