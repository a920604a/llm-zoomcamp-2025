import requests
from dlt.destinations import qdrant

import dlt
print(dlt.__version__)


@dlt.resource
def zoomcamp_data():
    docs_url = 'https://github.com/alexeygrigorev/llm-rag-workshop/raw/main/notebooks/documents.json'
    docs_response = requests.get(docs_url)
    documents_raw = docs_response.json()

    for course in documents_raw:
        course_name = course['course']

        for doc in course['documents']:
            doc['course'] = course_name
            yield doc
            


qdrant_destination = qdrant(qd_path="db.qdrant")

pipeline = dlt.pipeline(
    pipeline_name="zoomcamp_pipeline",
    destination=qdrant_destination,
    dataset_name="zoomcamp_tagged_data"
)

load_info = pipeline.run(zoomcamp_data())

# 印出執行記錄
print(pipeline.last_trace)

