from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models

model_handle = "jinaai/jina-embeddings-v2-small-en"
EMBEDDING_DIMENSIONALITY = 512


import requests

docs_url = 'https://github.com/alexeygrigorev/llm-rag-workshop/raw/main/notebooks/documents.json'
docs_response = requests.get(docs_url)
documents_raw = docs_response.json()

client = QdrantClient("http://localhost:6333") #connecting to local Qdrant instance
# Define the collection name
collection_name = "zoomcamp-hw2"

# Create the collection with specified vector parameters
client.create_collection(
    collection_name=collection_name,
    vectors_config=models.VectorParams(
        size=EMBEDDING_DIMENSIONALITY,  # Dimensionality of the vectors
        distance=models.Distance.COSINE  # Distance metric for similarity search
    )
)

from fastembed.embedding import TextEmbedding

# 初始化模型
embed_model = TextEmbedding(model_name="jinaai/jina-embeddings-v2-small-en")

# 輸入查詢句子
query = "I just discovered the course. Can I join now?"

# 計算嵌入向量
embedding = list(embed_model.embed([query]))[0]  # 取出第一個結果
from fastembed.embedding import TextEmbedding

# 初始化模型
embed_model = TextEmbedding(model_name="jinaai/jina-embeddings-v2-small-en")

# 輸入查詢句子
query = "I just discovered the course. Can I join now?"

# 計算嵌入向量
embedding = list(embed_model.embed([query]))[0]  # 取出第一個結果

min_value = min(embedding)
print(min_value)