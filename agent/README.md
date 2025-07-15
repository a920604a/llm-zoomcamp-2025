
# 智能問答系統 (Agentic RAG with Function Calling)

本專案示範如何打造一套基於 Retrieval-Augmented Generation (RAG) 架構的智能問答系統，結合 FAQ 檢索資料庫與大型語言模型 (LLM)，並支援多功能工具呼叫 (Function Calling)，實現更靈活的深度問答與資料擴充。

---

## 專案特色

- **RAG 架構**：先從 FAQ 資料庫檢索相關上下文，再透過 LLM 生成答案。
- **多階段深度搜尋**：系統會根據上下文不斷產生多個搜尋關鍵字，逐步擴充背景資料，提升回答品質。
- **多功能工具呼叫**：支援多個函式工具 (如搜尋 FAQ、手動新增 FAQ 條目等)，並由 LLM 決定何時呼叫哪個工具。
- **互動式問答介面**：可在命令列與 Jupyter Notebook 中執行，並顯示函式呼叫過程與結果，方便開發與除錯。

---

## 功能說明

### FAQ 檢索

- 使用 `minsearch` 套件建立可擴充的索引，支援多欄位文本與關鍵字過濾。
- 利用多欄位加權搜尋提升匹配準確度。
- 可動態加入新的 FAQ 問答條目。

### LLM 聊天機制

- 使用 OpenAI API (示範為 `gpt-4o-mini` 模型) 產生自然語言回答。
- 內建多輪互動機制，根據上下文及函式呼叫結果持續進行回答優化。
- 根據系統設計可自動判斷何時利用 FAQ 資料、何時使用自身知識回答。

### 函式呼叫 (Function Calling)

- 定義工具介面與參數格式（JSON Schema），並透過 LLM 呼叫相應工具。
- 回傳工具結果後，LLM 會根據結果進行下一步處理。
- 目前支援 FAQ 搜尋與新增 FAQ 條目兩種工具。

---

## 安裝需求

```bash
pip install openai minsearch ipython markdown requests
```

> 請自行安裝並設定 OpenAI API 金鑰。

---

## 使用說明

1. **下載 FAQ 文件集並建立索引**

```python
import requests
from minsearch import AppendableIndex

docs_url = 'https://github.com/alexeygrigorev/llm-rag-workshop/raw/main/notebooks/documents.json'
docs_response = requests.get(docs_url)
documents_raw = docs_response.json()

documents = []
for course in documents_raw:
    for doc in course['documents']:
        doc['course'] = course['course']
        documents.append(doc)

index = AppendableIndex(
    text_fields=["question", "text", "section"],
    keyword_fields=["course"]
)
index.fit(documents)

```


2. **定義檢索函式**

```python
def search(query):
    boost = {'question': 3.0, 'section': 0.5}
    results = index.search(
        query=query,
        filter_dict={'course': 'data-engineering-zoomcamp'},
        boost_dict=boost,
        num_results=5,
        output_ids=True
    )
    return results
```

3. **定義問答助手與工具**

* `search` 函式作為檢索工具，並依需求可新增 `add_entry` 函式新增 FAQ。
* 使用提供的 `ChatAssistant` 類別管理對話與函式呼叫流程。

4. **啟動互動問答**

```python
tools = Tools()
tools.add_tool(search, search_tool_description)
tools.add_tool(add_entry, add_entry_description)

developer_prompt = """
You're a course teaching assistant.
You're given a question from a course student and your task is to answer it.
Use FAQ if your own knowledge is not sufficient to answer the question.
At the end of each response, ask the user a follow up question based on your answer.
""".strip()

chat_interface = ChatInterface()
chat = ChatAssistant(tools, developer_prompt, chat_interface, client)
chat.run()
```

輸入問題即可與智能問答系統互動，輸入 `stop` 可結束。

---

## 專案架構說明

```
.
├── README.md                  # 專案說明文件
├── main.py                   # 主執行檔，啟動問答流程
├── chat_assistant.py         # 聊天助理與工具呼叫實作
├── requirements.txt          # Python 依賴套件列表
└── documents.json            # FAQ 文件集 (可動態從網路下載)
```

---

## 參考資源

* [Retrieval-Augmented Generation (RAG)](https://arxiv.org/abs/2005.11401)
* [minsearch](https://github.com/alexeygrigorev/minsearch)
* [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
* [RAG Agents Workshop (GitHub)](https://github.com/alexeygrigorev/rag-agents-workshop)

---

## 聯絡資訊

如有問題或建議，歡迎聯絡 \[你的聯絡方式]

---
