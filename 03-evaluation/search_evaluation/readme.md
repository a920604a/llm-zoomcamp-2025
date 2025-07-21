

# 🧠 課程問答搜尋系統：Elasticsearch vs MinSearch

## 📌 目標

建立一套問答搜尋系統，針對「課程內容相關問題」，找出最適合的答案，並透過 **Hit Rate** 與 **MRR (Mean Reciprocal Rank)** 評估查詢效果。

---

## 📁 1. 資料準備

### 🔹 文件來源：`documents-with-ids.json`

```json
{
  "id": "abc123",
  "course": "data-engineering-zoomcamp",
  "question": "When does the course start?",
  "section": "Introduction",
  "text": "The course starts in January every year."
}
```

### 🔹 評估資料集：`ground-truth-data.csv`

```csv
question,course,document
"When does the course start?",data-engineering-zoomcamp,abc123
```

---

## ⚙️ 2. Elasticsearch 設定與建立

### ✴️ 初始化 Elasticsearch client

```python
from elasticsearch import Elasticsearch
es_client = Elasticsearch('http://localhost:9200')
```

### ✴️ 建立索引設定與對應 mapping

```python
index_settings = {
    "settings": {"number_of_shards": 1, "number_of_replicas": 0},
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            "section": {"type": "text"},
            "question": {"type": "text"},
            "course": {"type": "keyword"},
            "id": {"type": "keyword"}
        }
    }
}
es_client.indices.delete(index="course-questions", ignore_unavailable=True)
es_client.indices.create(index="course-questions", body=index_settings)
```

### ✴️ 將文件寫入 Elasticsearch

```python
for doc in documents:
    es_client.index(index="course-questions", document=doc)
```

---

## 🔍 3. 查詢函式：Elasticsearch

```python
def elastic_search(query, course):
    search_query = {
        "size": 5,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["question^3", "text", "section"],
                        "type": "best_fields"
                    }
                },
                "filter": {
                    "term": {"course": course}
                }
            }
        }
    }
    response = es_client.search(index="course-questions", body=search_query)
    return [hit['_source'] for hit in response['hits']['hits']]
```

---

## 🧪 4. 效能指標：Hit Rate 與 MRR

### ✅ Hit Rate

```python
def hit_rate(relevance_total):
    return sum(any(line) for line in relevance_total) / len(relevance_total)
```

### ✅ Mean Reciprocal Rank (MRR)

```python
def mrr(relevance_total):
    total = 0
    for line in relevance_total:
        for rank, val in enumerate(line):
            if val:
                total += 1 / (rank + 1)
                break
    return total / len(relevance_total)
```

---

## 🧪 5. 評估查詢效能

### 🔄 通用評估函式

```python
def evaluate(ground_truth, search_function):
    relevance_total = []
    for q in ground_truth:
        results = search_function(q)
        relevance = [r['id'] == q['document'] for r in results]
        relevance_total.append(relevance)
    return {
        'hit_rate': hit_rate(relevance_total),
        'mrr': mrr(relevance_total)
    }
```

---

## 🧩 6. MinSearch 搜尋系統

### ✴️ 建立記憶體內索引

```python
import minsearch
index = minsearch.Index(
    text_fields=["question", "text", "section"],
    keyword_fields=["course", "id"]
)
index.fit(documents)
```

### ✴️ 查詢函式（含 boost）

```python
def minsearch_search(query, course):
    boost = {'question': 3.0, 'section': 0.5}
    return index.search(
        query=query,
        filter_dict={'course': course},
        boost_dict=boost,
        num_results=5
    )
```

---

## 📊 7. 結果比較

```python
evaluate(ground_truth, lambda q: elastic_search(q['question'], q['course']))
# => {'hit_rate': 0.739, 'mrr': 0.603}

evaluate(ground_truth, lambda q: minsearch_search(q['question'], q['course']))
# => {'hit_rate': 0.705, 'mrr': 0.575}
```

| 搜尋引擎          | Hit Rate | MRR   |
| ------------- | -------- | ----- |
| Elasticsearch | 0.739    | 0.603 |
| MinSearch     | 0.705    | 0.575 |

---

## ✅ 小結與延伸

* **Elasticsearch** 適合大型資料量與 production 使用。
* **MinSearch** 輕量、快速，適合 prototyping 與本機開發。
* Boost 權重設計對搜尋效果影響明顯。
* 可以延伸測試：

  * 使用 `BM25` vs `dense vector search`
  * 引入 Embedding 向量搜尋（FAISS, Elasticsearch dense\_vector）
