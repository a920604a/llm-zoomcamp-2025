import streamlit as st
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch.helpers import bulk
import requests
import json
import os
from tqdm.auto import tqdm


@st.cache_data
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


def elastic_index(documents, es_client, index_name="course-questions", use_bulk=True):
    index_settings = {
        "settings": {"number_of_shards": 1, "number_of_replicas": 0},
        "mappings": {
            "properties": {
                "text": {"type": "text"},
                "question": {"type": "text"},
                "course": {"type": "keyword"},
                "section": {"type": "text"},
            }
        }
    }

    try:
        if not es_client.indices.exists(index=index_name):
            es_client.indices.create(index=index_name, body=index_settings)
            st.info(f"已建立索引：{index_name}")
        else:
            st.success(f"索引 {index_name} 已存在")
    except Exception as e:
        st.error(f"建立索引錯誤：{e}")
        return index_name

    if use_bulk:
        actions = [{"_index": index_name, "_source": doc} for doc in documents]
        bulk(es_client, actions)
    else:
        for doc in tqdm(documents):
            es_client.index(index=index_name, document=doc)

    return index_name


def elastic_search(query, index_name, es_client, search_fields, num_results = 5):
    fields_with_boost = [f"{field}^{boost}" for field, boost in search_fields.items()]
    search_query = {
        "size": num_results,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": fields_with_boost,
                        "type": "best_fields"
                    }
                },
                "filter": {
                    "term": {
                        "course": "data-engineering-zoomcamp"
                    }
                }
            }
        }
    }

    response = es_client.search(index=index_name, body=search_query)

    hits = response['hits']['hits']
    return hits


# -------------------- Streamlit UI --------------------

st.set_page_config(page_title="Course FAQ Search", layout="wide")
st.title("📚 Course QA Search with Elasticsearch")

es_client = Elasticsearch("http://localhost:9200")

with st.sidebar:
    st.header("設定")
    if st.button("重新建立索引"):
        docs = fetch_documents()
        elastic_index(docs, es_client)
        st.success("重新索引完成 ✅")
        
        
    st.header("搜尋欄位與權重設定")

    use_question = st.checkbox("使用 question 欄位", value=True)
    boost_question = st.number_input("question 權重", value=4, min_value=1) if use_question else 0

    use_text = st.checkbox("使用 text 欄位", value=True)
    boost_text = st.number_input("text 欄位權重", value=1, min_value=1) if use_text else 0

    use_section = st.checkbox("使用 section 欄位", value=False)
    boost_section = st.number_input("section 權重", value=1, min_value=1) if use_section else 0

    search_fields = {}
    if use_question:
        search_fields["question"] = boost_question
    if use_text:
        search_fields["text"] = boost_text
    if use_section:
        search_fields["section"] = boost_section
        
    


st.markdown("請輸入你的問題關鍵字：")

query = st.text_input("Query", value="how do I run kafka?")

# 欄位權重設定（固定但可改為動態）


if query:
    with st.spinner("搜尋中..."):
        print(search_fields)
        hits = elastic_search(query, "course-questions", es_client, search_fields)
    print(hits)
    if hits:
        top_score = hits[0]['_score']
        st.markdown(f"### 🔍 Top Result Score: `{top_score:.2f}`\n")

        for i, hit in enumerate(hits, 1):
            st.subheader(f"📄 結果 {i} — Score: {hit['_score']:.2f}")
            st.markdown(f"**Section:** {hit['_source']['section']}")
            st.markdown(f"**Question:** {hit['_source']['question']}")
            st.markdown(f"**Answer:** {hit['_source']['text']}")
            st.markdown("---")
    else:
        st.warning("查無結果")
