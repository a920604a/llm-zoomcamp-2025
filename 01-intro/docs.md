## ✅ 專案簡介：Course QA Search

此專案的主要目的是讓使用者輸入一個自然語言問題，後端會：

1. **向 Elasticsearch 查詢**與問題最相關的多筆 FAQ（包括問題、段落、課程資訊）。
2. **將這些文件組成 Prompt 給 LLM 模型**。
3. **讓 LLM 回答問題**，以提供更完整與自然的回答。

### 架構簡要：

* `app.py`：主程式邏輯，處理查詢、組 Prompt、呼叫 LLM、顯示結果。
* `fetch_data.py`：載入初始的 FAQ 文件資料。
* `es.py`：封裝 Elasticsearch 的 index 與 search 功能。
* `llm.py`：呼叫 LLM 模型（透過 OpenRouter 提供免費模型）。
* `Docker + Elasticsearch`：以 Docker Compose 啟動本地的 Elasticsearch。

---

## 📖 Elasticsearch + LLM 作為 RAG 的核心流程（給學習推薦系統的工程師）

### 🎯 RAG 是什麼？

RAG（Retrieval-Augmented Generation）是結合 **資訊檢索（Retrieval）** 和 **語言生成（Generation）** 的架構，用來讓 LLM 在回答問題時不靠「幻想」，而是 **依據實際資料來源** 給出更可靠的答案。

---

### 🧠 在這個專案中，RAG 流程如下：

1. **Retrieval：使用 Elasticsearch 做向量/文字檢索**

   * 根據使用者輸入的 Query，在多個欄位（如 `question`, `text`, `section`）中搜尋最相關的 FAQ。
   * 支援欄位加權（boost）控制查詢重心。
   * 回傳 Top N 答案（預設 5 筆）與其 relevance `_score`。

2. **Augmentation：組成 Prompt 給 LLM**

   * 利用 `build_prompt()` 函數，把多筆 FAQ 組成一個有上下文的 Prompt。
   * 加入清楚的指令，提示 LLM 根據「僅有的上下文」回答問題。

3. **Generation：讓 LLM 生成答案**

   * 呼叫 `llm()` 函式透過 OpenRouter API，用免費模型（如 DeepSeek、Claude 3.5）回傳完整回答。
   * LLM 不直接查資料，而是根據前面提供的檢索結果回答。

---

## 💡 為什麼適合推薦系統工程師入門？

推薦系統也常見「檢索」與「語意生成」的組合。這個專案展示了：

* 如何組建簡單但實用的文本資料庫（Elasticsearch）
* 如何動態組 Prompt 與外部 LLM 整合（Prompt Engineering）
* 如何封裝服務與建構 API 或 UI 結合（可加上 FastAPI）

---

## 🧪 延伸應用方向（給推薦系統工程師）

* 改為向量搜尋（Elasticsearch dense\_vector + embedding 模型）
* 加入使用者歷史，實作 personalized retrieval
* 接入商業化模型如 GPT-4、Claude 3.5 提升回答品質
* 儲存 Q\&A pairs，作為微調資料集，未來可自行訓練 LLM

---

如你正在學習推薦系統或希望把 LLM 整合進自己的系統，這個專案提供了一個清晰、實作導向的範例，無論是搜尋流程、Prompt 設計、或是如何串接外部模型，都非常值得參考與拓展。要進一步提升，可以接上向量資料庫（如 Qdrant、Weaviate）或自行建立 embeddings 進行更語意化的檢索。
