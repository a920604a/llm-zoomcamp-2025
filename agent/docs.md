
## 🔍 什麼是 RAG（Retrieval-Augmented Generation）？

RAG 是一種結合 **搜尋引擎** 與 **語言模型（LLM）** 的應用架構，用來改善 LLM 回答問題的準確性與根據性。其流程分為三個主要步驟：

1. **Search（檢索）**
   根據使用者的提問，到外部資料來源（如 FAQ、文件、知識庫）中搜尋相關內容。

2. **Prompt（構建提示）**
   將搜尋結果組合成一個上下文提示（prompt），給 LLM 使用。

3. **LLM（生成回答）**
   語言模型根據這些上下文資料生成回覆，讓回覆更「有根據（grounded）」。

📌 **優點**：

* 解決 LLM「胡謅」（hallucination）問題
* 不需 retrain 模型即可擴充知識

---

## 🧠 什麼是 Agentic RAG？

Agentic RAG 是一種 **進階版 RAG**，讓 LLM 不只是 passively 使用 context，而是具備**決策能力與互動流程控制能力**。
它不只是單一查詢 + 回答，而是像「一個能主動思考的助理」，能根據任務決定是否要再查詢、重查、或直接回答。

### 特徵如下：

* **具有狀態與記憶**（保留前一次查詢/動作）
* **能決定何時查詢與何時回答**
* **能進行多輪查詢與推理**
* **能選擇使用哪個工具（tool）來完成任務**

範例行為：

```text
使用者問：「我要如何參加這門課？」

Agent 回答：「我要搜尋 FAQ，找關於報名的資訊」
→ 執行搜尋
→ 再次產生回答：「請至 Telegram 加入群組並依說明註冊」
```

---

## 🔁 什麼是 Agentic Search？

Agentic Search 是 Agentic RAG 中的一個子流程，專注於 **智能化的資料檢索階段**，強調以下能力：

1. **主動提出搜尋關鍵字**（非只用原始提問）
2. **根據目前 context 決定是否再次搜尋**
3. **迭代搜尋與彙整資料**
4. **避免重複查詢與過多查詢**

例如：

```text
提問：「如何在模組 1 表現良好？」

Agent 發現 context 不足 → 自己拆解出：
- 「module 1 requirement」
- 「homework module 1」
- 「project deadline module 1」
→ 多輪搜尋 → 整合 context → 再回答
```

📌 這讓模型可以深入探索問題，擁有類似人類的「找資料 + 歸納」能力。

---

### 📊 總結比較表：

| 模型類型           | 搜尋能力  | 決策能力 | 工具使用 | 多輪互動 | 範例                |
| -------------- | ----- | ---- | ---- | ---- | ----------------- |
| RAG            | ✅     | ❌    | ❌    | ❌    | 搜尋一次 FAQ → 回答     |
| Agentic RAG    | ✅     | ✅    | ✅    | ✅    | 決定是否要查詢、用工具、或直接回答 |
| Agentic Search | ✅（多次） | ✅    | ✅    | ✅    | 拆關鍵字、反覆查詢再整合      |

---

當我們在說 **Function Calling**（函式呼叫）時，指的是讓 **大型語言模型（LLM）** 在對話中能夠「主動」選擇使用開發者提供的特定函式，來完成某些它無法自己完成的任務，例如查資料、呼叫外部 API、或修改資料庫內容。

---

## 🔧 Function Calling 是什麼？

Function Calling 是 OpenAI 等 LLM 提供者的一種能力，允許開發者定義一組 **工具（functions）**，讓 LLM 在理解使用者問題後，**自行決定要不要使用這些工具**，並以結構化格式輸出工具的名稱與參數。

### 🧠 一句話總結：

> 讓 AI 知道「我可以幫你查資料、加資料、做計算」，然後 **AI 自己決定什麼時候需要叫你幫忙做**。

---

## 🔍 什麼時候需要用 Function Calling？

當你有一個 AI 助理，它：

* 需要查詢資料庫（RAG）
* 需要存入資料庫（例如使用者新增一筆記錄）
* 要根據特定參數做 API 查詢（如查天氣、股票）
* 要操作你系統的某些功能（例如幫使用者預約）

就可以透過 Function Calling 把這些功能暴露給 AI 助理使用。

---

## 🧱 基本架構

1. **定義函式描述（JSON 格式）**
   告訴 AI：「這個函式叫什麼、功能是什麼、接受哪些參數」

```python
search_tool = {
    "type": "function",
    "name": "search",
    "description": "Search the FAQ database",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query text to look up in the course FAQ."
            }
        },
        "required": ["query"]
    }
}
```

2. **將工具傳給 LLM（如 GPT-4）**

```python
response = client.responses.create(
    model="gpt-4o",
    input=chat_messages,
    tools=[search_tool]
)
```

3. **LLM 自動判斷是否呼叫工具**

```json
{
  "type": "function_call",
  "name": "search",
  "arguments": "{\"query\": \"how to join the course\"}",
  "call_id": "call_xyz"
}
```

4. **你在後端根據 `name` 和 `arguments` 呼叫對應的 Python 函式：**

```python
if call.name == "search":
    results = search(query=call.arguments["query"])
```

5. **將結果送回 LLM，讓它繼續生成回答**

```python
chat_messages.append({
    "type": "function_call_output",
    "call_id": call.call_id,
    "output": results
})
```

---

## ✅ 優點

* LLM 不再是「純聊天」，而能操作真實世界的資源。
* 可以建構 **具備決策能力** 的智能助理（Agent）。
* 輕鬆串接 RAG、資料庫、API、商業邏輯。
* 避免讓 LLM「瞎猜」，提高準確度與可控性。

---

## 📌 舉例：搜尋 FAQ

使用者問：

> 「我可以現在加入這門課嗎？」

LLM 判斷：「我不知道，得去查一下 FAQ」，所以回應：

```json
{
  "action": "function_call",
  "name": "search",
  "arguments": "{\"query\": \"how to join the course\"}"
}
```

你就幫它執行 `search("how to join the course")`，再把結果塞回去讓它繼續回答。

---

## 📘 延伸：和 Agent 的關係？

Function Calling 是 Agent 運作的核心能力之一。

* Agent 可以根據上下文與目標，自主決定是否要用工具
* Function Calling 提供「可以使用哪些工具」給 Agent
* 多輪呼叫 + 記憶上下文 = 強大的 Agentic Flow

