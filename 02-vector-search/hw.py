#!/usr/bin/env python
# coding: utf-8


from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models




client = QdrantClient("http://localhost:6333") #connecting to local Qdrant instance



model_handle = "jinaai/jina-embeddings-v2-small-en"
EMBEDDING_DIMENSIONALITY = 512


# Q1. Embedding the query


# 輸入查詢句子
query = "I just discovered the course. Can I join now?"
embed_model = TextEmbedding(model_name="jinaai/jina-embeddings-v2-small-en")

# 計算嵌入向量
embedding = list(embed_model.embed([query]))[0]  # 取出第一個結果

min_value = min(embedding)
print(min_value)


# Q2. Cosine similarity with another vector



import numpy as np

# 文字查詢與文件
doc = "Can I still join the course after the start date?"

# 各自嵌入
q_vector = list(embed_model.embed([query]))[0]
doc_vector = list(embed_model.embed([doc]))[0]

# 計算 cosine similarity（等同 dot product，因為已正規化）
similarity = np.dot(q_vector, doc_vector)

print(similarity)


# Q3. Ranking by cosine


documents = [{'text': "Yes, even if you don't register, you're still eligible to submit the homeworks.\nBe aware, however, that there will be deadlines for turning in the final projects. So don't leave everything for the last minute.",
  'section': 'General course-related questions',
  'question': 'Course - Can I still join the course after the start date?',
  'course': 'data-engineering-zoomcamp'},
 {'text': 'Yes, we will keep all the materials after the course finishes, so you can follow the course at your own pace after it finishes.\nYou can also continue looking at the homeworks and continue preparing for the next cohort. I guess you can also start working on your final capstone project.',
  'section': 'General course-related questions',
  'question': 'Course - Can I follow the course after it finishes?',
  'course': 'data-engineering-zoomcamp'},
 {'text': "The purpose of this document is to capture frequently asked technical questions\nThe exact day and hour of the course will be 15th Jan 2024 at 17h00. The course will start with the first  “Office Hours'' live.1\nSubscribe to course public Google Calendar (it works from Desktop only).\nRegister before the course starts using this link.\nJoin the course Telegram channel with announcements.\nDon’t forget to register in DataTalks.Club's Slack and join the channel.",
  'section': 'General course-related questions',
  'question': 'Course - When will the course start?',
  'course': 'data-engineering-zoomcamp'},
 {'text': 'You can start by installing and setting up all the dependencies and requirements:\nGoogle cloud account\nGoogle Cloud SDK\nPython 3 (installed with Anaconda)\nTerraform\nGit\nLook over the prerequisites and syllabus to see if you are comfortable with these subjects.',
  'section': 'General course-related questions',
  'question': 'Course - What can I do before the course starts?',
  'course': 'data-engineering-zoomcamp'},
 {'text': 'Star the repo! Share it with friends if you find it useful ❣️\nCreate a PR if you see you can improve the text or the structure of the repository.',
  'section': 'General course-related questions',
  'question': 'How can we contribute to the course?',
  'course': 'data-engineering-zoomcamp'}
 ]



# 從 documents 中擷取所有問題
questions = [doc['question'] for doc in documents]

collection_name = "question3"

# 2. 建立 Qdrant collection
client.delete_collection(collection_name=collection_name)

client.create_collection(  # recreate 可避免重複建立
    collection_name=collection_name,
    vectors_config=models.VectorParams(
        
        size=EMBEDDING_DIMENSIONALITY,
        distance=models.Distance.COSINE
    )
)



# 3. 上傳向量與 payload
points = [
    models.PointStruct(id=idx,
                    vector=models.Document(text=doc['text'], model=model_handle),
                    payload={
                        "question": doc['question'],
                        "text": doc['text'],
                        "course": doc['course']
                        }
                    )
    for idx, doc in enumerate(documents)
]

client.upsert(collection_name=collection_name, points=points)

def search(query, limit=1):
    results = client.query_points(
        collection_name=collection_name,
        query=models.Document(
            text=query,
            model=model_handle
        ),
        limit=limit,
        with_payload=True
    )
    return results

# 4. 查詢最相似的問句

res = search("I just discovered the course. Can I join now?", limit=1)
# print("最相似的文件 id:", res[0].id)
# print("內容:", res[0].payload)

print(res)
point = res.points[0]

print(f"最相似文件 ID: {point.id}")
print(f"相似度分數: {point.score:.4f}")
print(f"問題: {point.payload['question']}")
print(f"內容摘要: {point.payload['text'][:200]}...")


# Q4. Ranking by cosine, version two

# 從 documents 中擷取所有問題
questions = [doc['question'] for doc in documents]

collection_name = "question4"

# 2. 建立 Qdrant collection
client.delete_collection(collection_name=collection_name)

client.create_collection(  # recreate 可避免重複建立
    collection_name=collection_name,
    vectors_config=models.VectorParams(
        
        size=EMBEDDING_DIMENSIONALITY,
        distance=models.Distance.COSINE
    )
)



# 3. 上傳向量與 payload
points = []

for i, doc in enumerate(documents):
    full_text = doc['question'] + ' ' + doc['text']
    vector = models.Document(text=full_text, model=model_handle)
    point = models.PointStruct(
        id=i,
        vector=vector,
        payload=doc
    )
    points.append(point)
    
    
client.upsert(collection_name=collection_name, points=points)

def search(query, limit=1):
    results = client.query_points(
        collection_name=collection_name,
        query=models.Document(
            text=query,
            model=model_handle
        ),
        limit=limit,
        with_payload=True
    )
    return results

# 4. 查詢最相似的問句

res = search("I just discovered the course. Can I join now?", limit=1)
# print("最相似的文件 id:", res[0].id)
# print("內容:", res[0].payload)

print(res)
point = res.points[0]

print(f"最相似文件 ID: {point.id}")
print(f"相似度分數: {point.score:.4f}")
print(f"問題: {point.payload['question']}")
print(f"內容摘要: {point.payload['text'][:200]}...")


# Q5. Selecting the embedding model




from fastembed.embedding import TextEmbedding

models = TextEmbedding.list_supported_models()

# 找出最小維度的模型
min_model = min(models, key=lambda x: x['dim'])

print(f"最小維度模型: {min_model['model']} ({min_model['dim']} dimensions)")







from fastembed.embedding import TextEmbedding

embedder = TextEmbedding(model_name="BAAI/bge-small-en")

# embed 回傳 generator，要先轉成 list
vectors = list(embedder.embed(["Hello world!"]))
vector = vectors[0]

print(f"Embedding vector dimension: {len(vector)}")  # 預期為 384


# Q6. Indexing with qdrant (2 points)


import requests 

docs_url = 'https://github.com/alexeygrigorev/llm-rag-workshop/raw/main/notebooks/documents.json'
docs_response = requests.get(docs_url)
documents_raw = docs_response.json()


documents = []

for course in documents_raw:
    course_name = course['course']
    if course_name != 'machine-learning-zoomcamp':
        continue

    for doc in course['documents']:
        doc['course'] = course_name
        documents.append(doc)
        
       

# documents[:5]

collection_name = "question6"

# 2. 建立 Qdrant collection
client.delete_collection(collection_name=collection_name)

client.create_collection(  # recreate 可避免重複建立
    collection_name=collection_name,
    vectors_config=models.VectorParams(
        
        size=384,
        distance=models.Distance.COSINE
    )
)




points = []
id = 0
from qdrant_client import QdrantClient, models
for course in documents_raw:
    for doc in course['documents']:
        text = doc['question'] + ' ' + doc['text']
        point = models.PointStruct(
            id=id,
            vector=models.Document(text=text, model="BAAI/bge-small-en"), #embed text locally with "jinaai/jina-embeddings-v2-small-en" from FastEmbed
            payload={
                "text": doc['text'],
                "section": doc['section'],
                "course": course['course']
            } #save all needed metadata fields
        )
        points.append(point)

        id += 1
        


client.upsert(
    collection_name=collection_name,  # collection name
    points=points
)



def search(query, limit=1):
    results = client.query_points(
        collection_name=collection_name,
        query=models.Document(
            text=query,
            model="BAAI/bge-small-en"
        ),
        limit=limit,
        with_payload=True
    )
    return results

# 4. 查詢最相似的問句

res = search("I just discovered the course. Can I join now?", limit=1)
print(res)




