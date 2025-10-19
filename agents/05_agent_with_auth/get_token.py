import os
import base64
import hmac
import hashlib
import boto3
from dotenv import load_dotenv

# ==========================================================
# 1. .env から環境変数を読み込み
# ==========================================================
load_dotenv()

REGION = "us-east-1"
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USERNAME = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# ==========================================================
# 2. SECRET_HASH を生成（Client Secretが有効なため必須）
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
# 3. Cognito クライアント作成
# ==========================================================
client = boto3.client("cognito-idp", region_name=REGION)

# ==========================================================
# 4. 認証リクエストを実行
# ==========================================================
try:
    secret_hash = generate_secret_hash(USERNAME, CLIENT_ID, CLIENT_SECRET)
    response = client.initiate_auth(
        ClientId=CLIENT_ID,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={
            "USERNAME": USERNAME,
            "PASSWORD": PASSWORD,
            "SECRET_HASH": secret_hash,
        },
    )

    # ==========================================================
    # 5. トークンを表示
    # ==========================================================
    auth = response["AuthenticationResult"]
    print("\n✅ 認証成功！Cognito トークンを取得しました\n")
    print("Access Token:\n", auth["AccessToken"])
    print("\nID Token:\n", auth["IdToken"])
    print("\nRefresh Token:\n", auth["RefreshToken"])

except client.exceptions.NotAuthorizedException as e:
    print("❌ 認証エラー: ユーザー名またはパスワードが間違っています。")
    print(e)
except client.exceptions.UserNotFoundException:
    print("❌ 指定されたユーザーが存在しません。")
except Exception as e:
    print("⚠️ 予期しないエラー:", str(e))
