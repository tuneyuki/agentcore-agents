import os
import json
import uuid
import hmac
import base64
import hashlib
import boto3
import requests
import urllib.parse
from dotenv import load_dotenv

# ==========================================================
# 1. Load environment variables
# ==========================================================
load_dotenv()

REGION = "us-east-1"
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USERNAME = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD").strip('"')
AGENT_ARN = os.getenv("AGENT_ARN")


# ==========================================================
# 2. Generate SECRET_HASH (必須)
# ==========================================================
def generate_secret_hash(username, client_id, client_secret):
    message = username + client_id
    dig = hmac.new(
        client_secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(dig).decode()


# ==========================================================
# 3. Get Access Token from Cognito
# ==========================================================
def get_access_token():
    client = boto3.client("cognito-idp", region_name=REGION)
    secret_hash = generate_secret_hash(USERNAME, CLIENT_ID, CLIENT_SECRET)

    print("=== Step 1: Get Cognito Access Token ===")
    print(f"🔑 Authenticating as {USERNAME}")

    try:
        response = client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": USERNAME,
                "PASSWORD": PASSWORD,
                "SECRET_HASH": secret_hash,
            },
        )
        token = response["AuthenticationResult"]["AccessToken"]
        print("✅ 認証成功: Access Token 取得済み\n")
        return token
    except client.exceptions.NotAuthorizedException:
        raise RuntimeError("❌ ユーザー名またはパスワードが正しくありません。")
    except Exception as e:
        raise RuntimeError(f"⚠️ トークン取得エラー: {e}")


# ==========================================================
# 4. Invoke AgentCore Runtime (OAuth mode)
# ==========================================================
def invoke_agent(access_token, prompt):
    escaped_arn = urllib.parse.quote(AGENT_ARN, safe="")
    url = f"https://bedrock-agentcore.{REGION}.amazonaws.com/runtimes/{escaped_arn}/invocations?qualifier=DEFAULT"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Amzn-Trace-Id": f"trace-{uuid.uuid4()}",
        "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": str(uuid.uuid4()),
    }

    payload = {"prompt": prompt}

    print("=== Step 2: Invoke AgentCore Runtime ===")
    print(f"🚀 Agent ARN: {AGENT_ARN}\n")

    resp = requests.post(url, headers=headers, data=json.dumps(payload))

    print(f"📡 Status: {resp.status_code}")
    if resp.status_code == 200:
        print("\n✅ Response:")
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    else:
        print("\n❌ Error:")
        print(resp.text[:1000])


# ==========================================================
# 5. Main
# ==========================================================
if __name__ == "__main__":
    PROMPT = "Hey, tell me a short joke."

    token = get_access_token()
    invoke_agent(token, PROMPT)
