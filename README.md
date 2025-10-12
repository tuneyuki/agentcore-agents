# AgentCore Agents 

## 🧠 1. 思考・会話系エージェント

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

### **③ ストリーミング応答エージェント**

* **目的:** LangGraphを用いて、複数ステップの処理結果をリアルタイムで返すエージェントを構築する。
* **学習ポイント:** SSE（Server-Sent Events）による段階的応答と、LangGraphのステップ実行制御。
* **技術:** LangGraph・LangChain AWS（ChatBedrock）・AWS Bedrock AgentCoreを連携。
* **デモ例:** 「明日名古屋に行く計画を立てて」と依頼 → 各ステップ（分解→調査→統合）の結果を順にストリーミング出力。

---

### **④ Webリサーチャー**

* **目的:** Web検索し、情報を収集・要約する。
* **学習ポイント:** 外部API利用、情報統合、要約スキル。
* **技術:** Python + Requests / SerpAPI + LLM。
* **デモ例:** 「今月発表されたAIモデルをまとめて」→最新記事を要約。

---

### **⑤ ファイル解析エージェント**

* **目的:** CSV・PDFなどのファイルを読み込み、分析・要約。
* **学習ポイント:** ファイル入出力、構造化出力。
* **技術:** LangChain document loaders + Pandas + LLM。
* **デモ例:** 売上データCSVを解析して「傾向と課題」を報告。

---

### **⑥ DevOpsアシスタント**

* **目的:** ログを解析し、エラー原因と修正方法を提案。
* **学習ポイント:** ドメイン特化プロンプト設計、正規表現の活用。
* **技術:** Regex + LLM。
* **デモ例:** AWS CloudWatchログを読み、「このエラーの原因と対処法」を説明。

---

## 🧩 3. 知識・協働型エージェント

### **⑦ RAGベースQAエージェント**

* **目的:** 社内資料やドキュメントを検索して答える。
* **学習ポイント:** Embedding、ベクトル検索、RAG構成。
* **技術:** FAISS / Chroma + LangChain + OpenAI Embeddings。
* **デモ例:** 「このプロジェクトのKPIは？」→ドキュメントから自動回答。

---

### **⑧ チーム協調型エージェント**

* **目的:** 複数の役割（プランナー・リサーチャー・ライター）を持つエージェントが協力して1つのタスクを達成。
* **学習ポイント:** マルチエージェント・オーケストレーション。
* **技術:** CrewAI / AutoGen。
* **デモ例:** 「AIの未来について記事を書いて」→分担して執筆。

---

## 🖥️ 4. UI・応用系エージェント

### **⑨ Web UI連携チャットエージェント**

* **目的:** Webアプリ上で動くAIチャットを構築。
* **学習ポイント:** API連携、フロントエンドとの接続。
* **技術:** Flask + React / Next.js + Tailwind CSS。
* **デモ例:** 社内FAQボットや商品説明アシスタント。

---

### **⑩ 音声アシスタント**

* **目的:** 音声入力・音声出力対応のマルチモーダルAI。
* **学習ポイント:** 音声認識（STT）、音声合成（TTS）。
* **技術:** OpenAI Whisper + gTTS / Azure Speech。
* **デモ例:** 「今日の予定は？」と話しかけると音声で回答。

---

## 📘 学習ロードマップ（おすすめ順）

| ステップ | エージェント    | 学ぶ内容          |
| ---- | --------- | ------------- |
| ①    | 会話リフレクション | コンテキスト保持・会話構築 |
| ②    | タスク分解     | 推論構造・プロンプト設計  |
| ③    | 自己改善      | ループ構造・自己評価    |
| ④    | ファイル解析    | I/O操作と構造化応答   |
| ⑤    | Webリサーチ   | API連携と要約      |
| ⑥    | DevOps支援  | ログ解析・実践応用     |
| ⑦    | RAG QA    | ベクトル検索と知識活用   |
| ⑧    | チーム協調     | マルチエージェント連携   |
| ⑨    | UI連携      | Webアプリ統合      |
| ⑩    | 音声対応      | マルチモーダル処理     |

---

## 💡 提案：共通プロジェクト構成にすると便利！

もし10個をまとめて管理・デモするなら、こんな構成が便利です👇

```
ai-agents/
├─ agents/
│  ├─ 01_chat_reasoner/
│  ├─ 02_task_planner/
│  ├─ 03_self_reflector/
│  ├─ 04_web_researcher/
│  ├─ 05_file_analyzer/
│  ├─ 06_devops_assistant/
│  ├─ 07_rag_qa/
│  ├─ 08_multi_agent_team/
│  ├─ 09_web_ui/
│  └─ 10_voice_assistant/
├─ common/
│  ├─ utils/
│  ├─ memory/
│  └─ config/
├─ README.md
└─ requirements.txt
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
                "arn:aws:ecr:us-east-1:180048383118:repository/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:DescribeLogStreams",
                "logs:CreateLogGroup"
            ],
            "Resource": [
                "arn:aws:logs:us-east-1:180048383118:log-group:/aws/bedrock-agentcore/runtimes/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:DescribeLogGroups"
            ],
            "Resource": [
                "arn:aws:logs:us-east-1:180048383118:log-group:*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:us-east-1:180048383118:log-group:/aws/bedrock-agentcore/runtimes/*:log-stream:*"
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
                "arn:aws:bedrock-agentcore:us-east-1:180048383118:workload-identity-directory/default",
                "arn:aws:bedrock-agentcore:us-east-1:180048383118:workload-identity-directory/default/workload-identity/agentName-*"
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
                "arn:aws:bedrock:us-east-1:180048383118:*"
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
                "arn:aws:bedrock-agentcore:us-east-1:180048383118:memory/*"
            ]
        }
    ]
}
```