這段程式碼是為一個 **課程問答系統的搜尋引擎效能評估專案**，比較兩種搜尋方法：Elasticsearch 與 minsearch（記憶體內輕量搜尋器）的查詢效果（Hit Rate 與 MRR）。

---

## 📚 教材教學說明

### 一、專案目標

建立一套問答搜尋系統，從一組已知問答文件中，找出最相關的資料，並評估查詢的表現（準確率與排序品質）。

---

### 二、資料格式

#### `documents-with-ids.json`

這是要索引的原始文件，每筆資料長這樣：

```json
{
  "id": "abc123",
  "course": "data-engineering-zoomcamp",
  "question": "When does the course start?",
  "section": "Introduction",
  "text": "The course starts in January every year."
}
```

#### `ground-truth-data.csv`

這是查詢評估集，每筆資料長這樣：

```csv
question,course,document
"When does the course start?",data-engineering-zoomcamp,abc123
```

---

### 三、使用 Elasticsearch

#### 1️⃣ 建立 Index 與 Mapping

```python
index_settings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            "section": {"type": "text"},
            "question": {"type": "text"},
            "course": {"type": "keyword"},
            "id": {"type": "keyword"},
        }
    }
}
```

#### 2️⃣ 將資料寫入 ES

```python
for doc in documents:
    es_client.index(index=index_name, document=doc)
```

#### 3️⃣ 搜尋函式定義

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
                    "term": {
                        "course": course
                    }
                }
            }
        }
    }
    ...
```

---

### 四、搜尋效能評估

#### 🔹 Hit Rate

命中率（至少一筆正確答案出現在 top-5）：

```python
def hit_rate(relevance_total):
    return sum(any(line) for line in relevance_total) / len(relevance_total)
```

#### 🔹 Mean Reciprocal Rank (MRR)

取前 5 答案中，正確答案出現的位置的倒數：

```python
def mrr(relevance_total):
    total_score = 0.0
    for line in relevance_total:
        for rank, correct in enumerate(line):
            if correct:
                total_score += 1 / (rank + 1)
                break
    return total_score / len(relevance_total)
```

---

### 五、minsearch 搜尋

#### 1️⃣ 建立記憶體索引

```python
index = minsearch.Index(
    text_fields=["question", "text", "section"],
    keyword_fields=["course", "id"]
)
index.fit(documents)
```

#### 2️⃣ 查詢並加權

```python
def minsearch_search(query, course):
    boost = {'question': 3.0, 'section': 0.5}
    ...
```

---

### 六、統一評估函式

```python
def evaluate(ground_truth, search_function):
    relevance_total = []
    for q in ground_truth:
        results = search_function(q)
        relevance = [d['id'] == q['document'] for d in results]
        relevance_total.append(relevance)

    return {
        'hit_rate': hit_rate(relevance_total),
        'mrr': mrr(relevance_total),
    }
```

---

### 七、範例結果對照（假設）

```python
evaluate(ground_truth, lambda q: elastic_search(q['question'], q['course']))
# {'hit_rate': 0.74, 'mrr': 0.60}

evaluate(ground_truth, lambda q: minsearch_search(q['question'], q['course']))
# {'hit_rate': 0.68, 'mrr': 0.55}
```

---

## ✅ 教學小結

| 模組              | 功能                          |
| --------------- | --------------------------- |
| `Elasticsearch` | 專業、高效的全文檢索引擎                |
| `minsearch`     | 輕量級、記憶體內搜尋工具，適合 prototyping |
| `MRR/HitRate`   | 搜尋效能評估指標，衡量準確性與排序           |
