from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models

model_handle = "jinaai/jina-embeddings-v2-small-en"
EMBEDDING_DIMENSIONALITY = 512


import requests



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

min_value = min(embedding)
print(min_value)


import numpy as np

# 文字查詢與文件
doc = "Can I still join the course after the start date?"

# 各自嵌入
q_vector = list(embed_model.embed([query]))[0]
doc_vector = list(embed_model.embed([doc]))[0]

# 計算 cosine similarity（等同 dot product，因為已正規化）
similarity = np.dot(q_vector, doc_vector)

print(similarity)


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

texts = [doc["text"] for doc in documents]
text_vecs = list(embed_model.embed(texts))
V = np.vstack(text_vecs)  # shape: (5, 512)

scores_q3 = V.dot(q_vec)
best_index_q3 = int(np.argmax(scores_q3))
print("Q3 best index:", best_index_q3)
