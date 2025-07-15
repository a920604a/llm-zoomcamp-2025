
# Cognee + DLT NYC Taxi Dataset 知識圖譜與語意查詢範例

本專案示範如何從 NYC Taxi 公共 API 擷取資料，使用 DLT 建立 ETL pipeline，將資料載入 DuckDB，並透過 Cognee 及 Neo4j 圖形資料庫構建知識圖譜，最後進行語意搜尋。

---

## 專案特色

- 從 REST API 取得 NYC Taxi 2009 年 6 月分的打車資料
- 以 Pandas 進行時間分段分類（前10天、中10天、後10天）
- 使用 DLT 建立管線，自動將資料寫入 DuckDB
- 利用 Cognee 將結構化資料導入 Neo4j 知識圖譜
- 提供多種查詢類型 (Graph Completion, RAG Completion) 的語意查詢範例

---

## 環境需求

- Python 3.8+
- Neo4j 4.x+
- DuckDB (由 DLT 自動安裝使用)
- Cognee Python SDK
- 其他套件：`requests`, `pandas`, `dlt`

---

## 安裝依賴

```bash
pip install requests pandas dlt cognee neo4j
```

---

## 環境變數設定

請先設定圖形資料庫與 LLM API 金鑰等環境變數，例如：

```bash
export GRAPH_DATABASE_PROVIDER=neo4j
export GRAPH_DATABASE_URL=bolt://localhost:7687
export GRAPH_DATABASE_USERNAME=neo4j
export GRAPH_DATABASE_PASSWORD=your_password_here
export LLM_API_KEY=your_openai_api_key
```

---

## 使用說明

### 1. 擷取資料並寫入 DuckDB

執行 `your_ingest_script.py`：

```bash
python your_ingest_script.py
```

程式將會從 API 擷取打車資料，並依時間分段打標籤，最後使用 DLT pipeline 載入 DuckDB。

### 2. 使用 Cognee 進行圖譜查詢

執行 `main.py`（或你的 Cognee 查詢腳本）：

```bash
python main.py
```

可透過 `search_cognee` 函式對指定節點集合執行語意查詢。

---

## 主要程式功能說明

* **fetch\_taxi\_data()**
  從 API 擷取資料，並轉換時間欄位、分段分類。

* **run\_pipeline(df)**
  建立 DLT pipeline，寫入 DuckDB。

* **search\_cognee(query, node\_set, query\_type)**
  非同步函式，使用 Cognee API 在指定節點集合查詢語意結果。

* **main()**
  範例查詢，查詢 Ticketmaster API 端點資訊。

---

## 範例查詢

```python
results = await search_cognee(
    query="What API endpoints are in the Ticketmaster api? Give me specific endpoint urls.",
    node_set=['developer.ticketmaster.com']
)
print(results[0])
```

---

## 專案結構建議

```
.
├── README.md
├── your_ingest_script.py    # 資料擷取與 DLT pipeline 腳本
├── main.py                 # Cognee 查詢執行腳本
├── requirements.txt
```

---

## 參考文件

* [Cognee 官方文件](https://docs.cognee.ai/)
* [DLT 文件](https://dlthub.com/docs/)
* [Neo4j 官方網站](https://neo4j.com/)
* [DuckDB](https://duckdb.org/)
* [OpenAI API](https://platform.openai.com/docs/api-reference)

---
