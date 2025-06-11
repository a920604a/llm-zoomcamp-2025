import os
import json
import requests


def fetch_documents():
    local_path = 'documents.json'
    if os.path.exists(local_path):
        with open(local_path, 'r') as f:
            return json.load(f)
    else:
        docs_url = 'https://github.com/DataTalksClub/llm-zoomcamp/blob/main/01-intro/documents.json?raw=1'
        docs_response = requests.get(docs_url)
        documents_raw = docs_response.json()
        documents = []
        for course in documents_raw:
            course_name = course['course']
            for doc in course['documents']:
                doc['course'] = course_name
                documents.append(doc)
        with open(local_path, 'w') as f:
            json.dump(documents, f)
        return documents

