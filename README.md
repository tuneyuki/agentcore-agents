# AgentCore Agents 

## エージェント一覧

### **0 ベースエージェント**

* **目的:** チャット機能のみを提供する、AgentCoreのベースAgent
* **技術:** StrandsでLLMを呼び出している

---

### **① プロジェクトマネジメント支援エージェント**

* **目的:** Bedrock AgentCoreのメモリ機能を活用し、過去の会話や知識を参照してプロジェクト管理を支援する。
* **学習ポイント:** 短期メモリ（Short-term）と長期メモリ（Long-term）の連携による文脈保持。
* **技術:** AWS Bedrock AgentCore Memory・Strands Agent・Bedrock Modelを統合。
* **デモ例:** 「今週の進捗をまとめて」と入力 → 過去の会話と知識を参照して要約を生成。

---

### **② タスク分解プランナーエージェント**

* **目的:** ユーザーの目標を分解し、リサーチと統合を行って実行可能なプランを作成する。
* **学習ポイント:** LangGraphを用いたステップ型ワークフロー構築と、外部検索（DuckDuckGo）連携。
* **技術:** LangGraph・LangChain Community Tools・AWS Bedrock AgentCore・Strands Agentを組み合わせ。
* **デモ例:** 「新規プロジェクトの準備をしたい」と入力 → 分解→調査→統合の3段階で実行計画を生成。

---

### **③ ストリーミング応答タスク分解プランナーエージェント**

* **目的:** LangGraphを用いて、複数ステップの処理結果をリアルタイムで返すエージェントを構築する。
* **学習ポイント:** SSE（Server-Sent Events）による段階的応答と、LangGraphのステップ実行制御。
* **技術:** LangGraph・LangChain AWS（ChatBedrock）・AWS Bedrock AgentCoreを連携。
* **デモ例:** 「明日名古屋に行く計画を立てて」と依頼 → 各ステップ（分解→調査→統合）の結果を順にストリーミング出力。

---

### **④ CodeInterpreterエージェント**

- **目的:**  生成した回答を実際のPythonコードで検証し、計算・論理・アルゴリズムの正確性を確認する。
- **学習ポイント:**  Bedrock AgentCoreのCode Interpreter機能をツールとして統合し、Strands Agent経由で実行・結果検証を行う。
- **技術:**  AWS Bedrock AgentCore・Strands Agent・Bedrock Model・Code Interpreter Client を連携。
- **デモ例:**  「Can all the planets in the solar system fit between the earth and moon?」と入力 →  コードを自動生成・実行し、計算結果を基に結論を提示。


---


## フォルダ構成

```
ai-agents/
├─ agents/
│  ├─ 00_base_agent/
│  ├─ 01_pm_support_bot/
│  ├─ 02_task_planner/
│  ├─ 03_sse_agent_bot/
│  └─ 04_code_interpreter_bot/
├─ common/ # いずれ作る
│  ├─ utils/
│  ├─ memory/
│  └─ config/
└─ README.md
```


## IAM

* BedrockAgentCorePolicy

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ECRImageAccess",
            "Effect": "Allow",
            "Action": [
                "ecr:BatchGetImage",
                "ecr:GetDownloadUrlForLayer"
            ],
            "Resource": [
                "arn:aws:ecr:us-east-1:xxxxxxxxxxxx:repository/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:DescribeLogStreams",
                "logs:CreateLogGroup"
            ],
            "Resource": [
                "arn:aws:logs:us-east-1:xxxxxxxxxxxx:log-group:/aws/bedrock-agentcore/runtimes/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:DescribeLogGroups"
            ],
            "Resource": [
                "arn:aws:logs:us-east-1:xxxxxxxxxxxx:log-group:*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:us-east-1:xxxxxxxxxxxx:log-group:/aws/bedrock-agentcore/runtimes/*:log-stream:*"
            ]
        },
        {
            "Sid": "ECRTokenAccess",
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "xray:PutTraceSegments",
                "xray:PutTelemetryRecords",
                "xray:GetSamplingRules",
                "xray:GetSamplingTargets"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Resource": "*",
            "Action": "cloudwatch:PutMetricData",
            "Condition": {
                "StringEquals": {
                    "cloudwatch:namespace": "bedrock-agentcore"
                }
            }
        },
        {
            "Sid": "GetAgentAccessToken",
            "Effect": "Allow",
            "Action": [
                "bedrock-agentcore:GetWorkloadAccessToken",
                "bedrock-agentcore:GetWorkloadAccessTokenForJWT",
                "bedrock-agentcore:GetWorkloadAccessTokenForUserId"
            ],
            "Resource": [
                "arn:aws:bedrock-agentcore:us-east-1:xxxxxxxxxxxx:workload-identity-directory/default",
                "arn:aws:bedrock-agentcore:us-east-1:xxxxxxxxxxxx:workload-identity-directory/default/workload-identity/agentName-*"
            ]
        },
        {
            "Sid": "BedrockModelInvocation",
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/*",
                "arn:aws:bedrock:us-east-1:xxxxxxxxxxxx:*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock-agentcore:ListEvents",
                "bedrock-agentcore:CreateEvent",
                "bedrock-agentcore:GetEvent",
                "bedrock-agentcore:ListMemories",
                "bedrock-agentcore:GetMemory"
            ],
            "Resource": [
                "arn:aws:bedrock-agentcore:us-east-1:xxxxxxxxxxxx:memory/*"
            ]
        }
    ]
}
```


## 得た学び
### 1 Memory

* Short Term Memoryの読み取りとLong Term Memoryの読み取りのPermissionは異なる。
* Long Term Memoryの読み取りには、`bedrock-agentcore:RetrieveMemoryRecords` が必要だった。

```
		{
			"Effect": "Allow",
			"Action": [
				"bedrock-agentcore:ListEvents",
				"bedrock-agentcore:CreateEvent",
				"bedrock-agentcore:GetEvent",
				"bedrock-agentcore:ListMemories",
				"bedrock-agentcore:GetMemory",
				"bedrock-agentcore:RetrieveMemoryRecords"
			],
			"Resource": [
				"arn:aws:bedrock-agentcore:us-east-1:xxxxxxxxxxxx:memory/*"
			]
		}
```

### 3 SSE
* yieldで自在に途中のリターンを返却できる。


### 4 Code Interpreter
* Tool としてCodeInterpreterを登録したら、適切な回答を返すまで複数回のInterpreter呼び出しが行われうる。
<<<<<<< HEAD
=======

### 5. Agent with Auth
* 環境変数は、`agentcore launch` コマンドの引数で簡単に指定できる

```
agentcore launch --env OPENAI_API_KEY="sk-proj-xxxxxxxx"
```

* CognitoのUserPoolにユーザー初回追加した状態では、APIでのログインができない。ユーザーが初回ログインしてPW変更することで、初めて有効化される。
* IDProviderは、デフォルトではUSERNAME/PASSWORDでの認証はDisableになっている。Enableしてあげる必要がある。あとから変更もできる。

#### 🔑 認証付き AgentCore 呼び出しのポイントまとめ

---

##### 🧩 1. 認証モードを「OAuth」に設定する

- AgentCore Runtime を作るときに、  
    Cognito の設定（`discoveryUrl` と `allowedClients`）を指定する必要がある。
- これを設定しないと IAM 認証モード扱いになり、OAuth トークンが無視される。
    

---

##### 🔐 2. Cognito クライアントに「Client Secret」がある場合は必ず SECRET_HASH を使う

- Cognito の App Client を “Secret 付き” で作ったら、  
    その Secret で署名した `SECRET_HASH` を送らないと認証エラーになる。
- Secret 無しのクライアントなら不要。

---

##### 👤 3. Cognito ユーザーは「Force change password」を解除しておく

- ユーザー作成直後は一時パスワード状態になっていてログインできない。
- 管理者コマンドやコンソールで **「パスワードを恒久化」** しておく必要がある。

---

##### 🚫 4. boto3 では OAuth Agent を直接呼べない

- `boto3.client('bedrock-agentcore')` は IAM 用（SigV4）専用。
- OAuth 認証で呼ぶ場合は **`requests.post()` で HTTPS 直接呼び出し** が必要。

---

##### 🎟️ 5. Token の種類に注意

- Cognito は 3 種のトークンを返す：
    - AccessToken ✅ → API呼び出し用（これを使う）
    - IdToken ❌ → 表示用
    - RefreshToken → 再認証用
- AgentCore に渡すのは **AccessToken** 一択。
    

---

##### 🌐 6. 正しい呼び出しURLを使う

- Agent 呼び出しのエンドポイントは  
    `/runtimes/{AgentARN}/invocations`。
- `/identities/oauth2/invoke` は別用途（使わない）。


### 6. fastapi_agent
* Agentcore-starter-kitを使わない場合は、自分でECRにDockerビルドしてプッシュしてやる必要があるため、Dockerが動かせる環境でないと使えない。

- 🚀 ECR デプロイ手順（us-east-1 / fastapi_agent）
	- 🧱 リポジトリ作成
	- aws ecr create-repository --repository-name fastapi_agent --region us-east-1

- 🔐 ECR ログイン
	- aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ccount_id>.dkr.ecr.us-east-1.amazonaws.com

- 🏗️ ビルド＆プッシュ（ARM64対応）
	- docker buildx build --platform linux/arm64 -t <account_id>.dkr.ecr.us-east-1.amazonaws.com/fastapi_agent:latest --push .

- 🔍 プッシュ確認
	- aws ecr describe-images --repository-name fastapi_agent --region us-east-1

### 7. customer support agent.

* AWS SSM
>>>>>>> 76c87af (add auth)
