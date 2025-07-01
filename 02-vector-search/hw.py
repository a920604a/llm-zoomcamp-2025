#!/usr/bin/env python
# coding: utf-8

from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models
import numpy as np
import requests

# === 基本設定 ===
client = QdrantClient("http://localhost:6333")
embed_model_jina = TextEmbedding(model_name="jinaai/jina-embeddings-v2-small-en")
embed_model_bge = TextEmbedding(model_name="BAAI/bge-small-en")
model_jina = "jinaai/jina-embeddings-v2-small-en"
model_bge = "BAAI/bge-small-en"


# === Q1: 單句嵌入與最小值 ===
query = "I just discovered the course. Can I join now?"
embedding = list(embed_model_jina.embed([query]))[0]
print(min(embedding))


# === Q2: 計算 cosine 相似度 ===
doc = "Can I still join the course after the start date?"
q_vector = list(embed_model_jina.embed([query]))[0]
doc_vector = list(embed_model_jina.embed([doc]))[0]
similarity = np.dot(q_vector, doc_vector)
print(similarity)


# === Q3: 向量比對 - 根據 text 建立索引 ===
documents = [
    {'text': "...", 'section': '...', 'question': '...', 'course': 'data-engineering-zoomcamp'},
    # 略：原始題目中已給完整內容，此處略寫
]

collection_q3 = "question3"
client.delete_collection(collection_name=collection_q3)
client.create_collection(
    collection_name=collection_q3,
    vectors_config=models.VectorParams(size=512, distance=models.Distance.COSINE),
)

points_q3 = [
    models.PointStruct(
        id=idx,
        vector=models.Document(text=doc['text'], model=model_jina),
        payload={k: doc[k] for k in ['question', 'text', 'course']}
    )
    for idx, doc in enumerate(documents)
]
client.upsert(collection_name=collection_q3, points=points_q3)


def search_q3(query: str, limit: int = 1):
    return client.query_points(
        collection_name=collection_q3,
        query=models.Document(text=query, model=model_jina),
        limit=limit,
        with_payload=True
    )


res = search_q3(query, limit=1)
point = res.points[0]
print(f"最相似文件 ID: {point.id}")
print(f"相似度分數: {point.score:.4f}")
print(f"問題: {point.payload['question']}")
print(f"內容摘要: {point.payload['text'][:200]}...")


# === Q4: text + question 結合後上傳索引 ===
collection_q4 = "question4"
client.delete_collection(collection_name=collection_q4)
client.create_collection(
    collection_name=collection_q4,
    vectors_config=models.VectorParams(size=512, distance=models.Distance.COSINE),
)

points_q4 = [
    models.PointStruct(
        id=i,
        vector=models.Document(text=doc['question'] + ' ' + doc['text'], model=model_jina),
        payload=doc
    )
    for i, doc in enumerate(documents)
]
client.upsert(collection_name=collection_q4, points=points_q4)


def search_q4(query: str, limit: int = 1):
    return client.query_points(
        collection_name=collection_q4,
        query=models.Document(text=query, model=model_jina),
        limit=limit,
        with_payload=True
    )


res = search_q4(query, limit=1)
point = res.points[0]
print(f"最相似文件 ID: {point.id}")
print(f"相似度分數: {point.score:.4f}")
print(f"問題: {point.payload['question']}")
print(f"內容摘要: {point.payload['text'][:200]}...")


# === Q5: 列出所有模型並找出維度最小者 ===
models_list = TextEmbedding.list_supported_models()
min_model = min(models_list, key=lambda x: x['dim'])
print(f"最小維度模型: {min_model['model']} ({min_model['dim']} dimensions)")


# === Q5 補充: bge-small-en 嵌入維度驗證 ===
vector = list(embed_model_bge.embed(["Hello world!"]))[0]
print(f"Embedding vector dimension: {len(vector)}")  # 預期為 384


# === Q6: 使用遠端 json 下載課程文件並建立索引 ===
docs_url = 'https://github.com/alexeygrigorev/llm-rag-workshop/raw/main/notebooks/documents.json'
documents_raw = requests.get(docs_url).json()

documents_mlz = [
    {**doc, 'course': course['course']}
    for course in documents_raw if course['course'] == 'machine-learning-zoomcamp'
    for doc in course['documents']
]

collection_q6 = "question6"
client.delete_collection(collection_name=collection_q6)
client.create_collection(
    collection_name=collection_q6,
    vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
)

points_q6 = []
for i, doc in enumerate(documents_mlz):
    full_text = doc['question'] + ' ' + doc['text']
    point = models.PointStruct(
        id=i,
        vector=models.Document(text=full_text, model=model_bge),
        payload={k: doc[k] for k in ['text', 'section', 'course']}
    )
    points_q6.append(point)

client.upsert(collection_name=collection_q6, points=points_q6)


def search_q6(query: str, limit: int = 1):
    return client.query_points(
        collection_name=collection_q6,
        query=models.Document(text=query, model=model_bge),
        limit=limit,
        with_payload=True
    )


res = search_q6(query, limit=1)
print(res)
