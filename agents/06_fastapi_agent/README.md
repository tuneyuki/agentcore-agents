🚀 ECR デプロイ手順（us-east-1 / fastapi_agent）
🧱 リポジトリ作成
aws ecr create-repository --repository-name fastapi_agent --region us-east-1

🔐 ECR ログイン
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ccount_id>.dkr.ecr.us-east-1.amazonaws.com

🏗️ ビルド＆プッシュ（ARM64対応）
docker buildx build --platform linux/arm64 -t <account_id>.dkr.ecr.us-east-1.amazonaws.com/fastapi_agent:latest --push .

🔍 プッシュ確認
aws ecr describe-images --repository-name fastapi_agent --region us-east-1

