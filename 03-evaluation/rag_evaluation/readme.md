# RAG 系統評估流程筆記（以 Machine Learning Zoomcamp FAQ 為例）

---

## 1. 資料載入與準備

### 載入 FAQ documents

```python
url_prefix = 'https://raw.githubusercontent.com/DataTalksClub/llm-zoomcamp/main/03-evaluation/'
docs_url = url_prefix + 'search_evaluation/documents-with-ids.json'
documents = requests.get(docs_url).json()
```

### Ground Truth 載入與過濾

```python
df_ground_truth = pd.read_csv(url_prefix + 'search_evaluation/ground-truth-data.csv')
df_ground_truth = df_ground_truth[df_ground_truth.course == 'machine-learning-zoomcamp']
ground_truth = df_ground_truth.to_dict(orient='records')
```

---

## 2. 向量化 FAQ（使用 sentence-transformers）

### 安裝必要套件

```bash
pip install sentence-transformers
```

### 使用模型並產生向量

```python
model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
vectors = [model.encode(doc['question'] + ' ' + doc['text']) for doc in documents]
```

---

## 3. 使用 minsearch 建立向量索引器

```python
from minsearch import VectorSearch
vindex = VectorSearch(keyword_fields=['course'])
vindex.fit(vectors, documents)
```

---

## 4. 查詢系統：RAG Pipeline

### 向量查詢

```python
def question_text_vector(q):
    v_q = model.encode(q['question'])
    return vindex.search(v_q, filter_dict={'course': q['course']}, num_results=5)
```

### Prompt 組裝（根據搜尋結果）

```python
def build_prompt(query, search_results):
    context = "\n\n".join([
        f"section: {doc['section']}\nquestion: {doc['question']}\nanswer: {doc['text']}"
        for doc in search_results
    ])
    return f"""
You're a course teaching assistant. Answer the QUESTION based on the CONTEXT from the FAQ database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {query}

CONTEXT:
{context}
""".strip()
```

### 調用 OpenAI Chat API

```python
def llm(prompt, model='gpt-4o'):
    return client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content
```

### 完整 RAG 呼叫流程

```python
def rag(query: dict, model='gpt-4o') -> str:
    results = question_text_vector(query)
    prompt = build_prompt(query['question'], results)
    return llm(prompt, model)
```

---

## 5. 以 Cosine Similarity 評估回答品質

### 回答向量比對

```python
def compute_similarity(record):
    v_llm = model.encode(record['answer_llm'])
    v_orig = model.encode(record['answer_orig'])
    return v_llm.dot(v_orig)
```

### 統計描述

```python
df['cosine'] = df.apply(compute_similarity, axis=1)
df['cosine'].describe()
```

### 視覺化

```python
sns.distplot(df_gpt4o['cosine'], label='4o')
sns.distplot(df_gpt4o_mini['cosine'], label='4o-mini')
plt.legend()
```

---

## 6. LLM as a Judge：人工智慧評分機制

### Prompt Template (A → Q → A′)

```python
prompt1_template = """
You are an expert evaluator for a Retrieval-Augmented Generation (RAG) system.
Your task is to analyze the relevance of the generated answer compared to the original answer provided.
Classify as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Original Answer: {answer_orig}
Generated Question: {question}
Generated Answer: {answer_llm}

Respond with JSON:
{{
  "Relevance": ..., "Explanation": ...
}}
"""
```

### Prompt Template (Q → A′)

```python
prompt2_template = """
You are an expert evaluator for a Retrieval-Augmented Generation (RAG) system.
Your task is to analyze the relevance of the generated answer to the given question.
Classify as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Question: {question}
Generated Answer: {answer_llm}

Respond with JSON:
{{
  "Relevance": ..., "Explanation": ...
}}
"""
```

### 批次判斷並轉為 DataFrame

```python
evaluations = [llm(prompt1_template.format(**rec), model='gpt-4o-mini') for rec in samples]
df_eval = pd.DataFrame([json.loads(e) for e in evaluations])
df_eval.Relevance.value_counts()
```

---

## 7. 匯出結果

```python
df_gpt4o.to_csv('data/results-gpt4o-cosine.csv', index=False)
df_evaluations.to_csv('data/evaluations-aqa.csv', index=False)
```

---

## 結論

* 本流程整合了 minsearch 檢索、向量查詢、OpenAI 回答與雙重評估（cosine similarity + LLM-as-a-judge）。
* 能夠快速試驗不同模型（gpt-4o / 3.5 / 4o-mini）並比較品質。
* 提供完整的評估與可視化工具協助觀察結果分布。
