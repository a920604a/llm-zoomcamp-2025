
# 📘 Qdrant 向量搜尋應用說明文件

## 專案簡介

本專案展示如何使用 [`FastEmbed`](https://github.com/anzu-inc/fastembed) 進行文字嵌入（Text Embedding），並結合 [`Qdrant`](https://qdrant.tech/) 向量資料庫進行相似度搜尋，實作 FAQ 問題匹配、嵌入模型比較與向量查詢任務。

---

## 📦 使用套件

* `fastembed`: 輕量化文字嵌入工具，支援多種 HuggingFace 模型
* `qdrant-client`: Python SDK，用於操作 Qdrant 向量資料庫
* `numpy`: 用於計算 cosine similarity
* `requests`: 用於下載遠端 JSON 資料

---

## 📐 主要嵌入模型

| 模型名稱                                 | 維度  | 說明             |
| ------------------------------------ | --- | -------------- |
| `jinaai/jina-embeddings-v2-small-en` | 512 | Jina 提供的英文嵌入模型 |
| `BAAI/bge-small-en`                  | 384 | 適合語意相似度比對      |

---

## 🧪 功能說明

### Q1. 單句 Embedding 並取最大最小值

```python
embed_model = TextEmbedding(model_name="jinaai/jina-embeddings-v2-small-en")
embedding = list(embed_model.embed([query]))[0]
```

* 使用指定模型將查詢句子轉換為向量
* 可進行統計分析（如 min/max）

---

### Q2. 兩句之間的 Cosine Similarity

```python
similarity = np.dot(q_vector, doc_vector)
```

* 嵌入兩個句子後，使用點積計算語意相似度（前提是已正規化）

---

### Q3. 將問句集合上傳至 Qdrant 並進行向量搜尋

```python
client.create_collection(...)
client.upsert(points=...)
client.query_points(...)
```

* 使用 `models.Document(text=..., model=...)` 自動完成嵌入與索引
* 支援 payload 回傳原始問題與對應內容

---

### Q4. 改良索引內容為「question + text」

```python
full_text = doc['question'] + ' ' + doc['text']
```

* 提升搜尋品質
* 支援完整語境理解與排序

---

### Q5. 比較嵌入模型維度

```python
models = TextEmbedding.list_supported_models()
min_model = min(models, key=lambda x: x['dim'])
```

* 自動選出最小維度的嵌入模型（可用於資源有限情況）

---

### Q6. 自外部來源載入資料並建立索引

```python
docs_url = 'https://github.com/.../documents.json'
```

* 針對 `machine-learning-zoomcamp` 課程進行資料篩選與索引
* 使用 `BAAI/bge-small-en` 嵌入內容並上傳至 Qdrant
* 查詢邏輯與 Q3 類似，但採用了不同資料來源與模型

---

## 🧪 查詢範例

```python
res = search("I just discovered the course. Can I join now?")
```

輸出格式範例：

```text
最相似文件 ID: 0
相似度分數: 0.9235
問題: Course - Can I still join the course after the start date?
內容摘要: Yes, even if you don't register, you're still eligible to submit the homeworks...
```

---

## 🛠️ 可擴充功能建議

* 增加前端查詢介面（例如 Streamlit）
* 將搜尋結果結合回答生成（RAG 架構）
* 多語言嵌入支援（例如 `bge-m3`）

---

## 📂 專案結構建議

```
project/
├── main.py               # 主程式邏輯
├── docs.md               # 說明文件
├── requirements.txt      # 套件依賴
└── utils.py              # 嵌入與查詢工具函數（可選）
```

---

## 📌 注意事項

* 若使用 `models.Document(text=..., model=...)`，需確保 Qdrant 支援直接嵌入，否則須本地先轉換為向量。
* 若 FastEmbed 模型下載較慢，請考慮使用 GPU 或換用較小模型。
* Qdrant 預設埠為 `6333`，可透過 Docker 或本機安裝啟動。

---

如需補充 `requirements.txt`、完整分段模組化程式或建立測試資料，歡迎補充需求。
