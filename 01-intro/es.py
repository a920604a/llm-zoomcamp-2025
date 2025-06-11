
from tqdm.auto import tqdm
from elasticsearch import Elasticsearch

es_client = Elasticsearch("http://localhost:9200")


def elastic_index(documents,  index_name="course-questions", use_bulk=True):
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
            # st.info(f"已建立索引：{index_name}")
            print(f"已建立索引：{index_name}")
        else:
            # st.success(f"索引 {index_name} 已存在")
            print(f"索引 {index_name} 已存在")
    except Exception as e:
        # st.error(f"建立索引錯誤：{e}")
        print(f"建立索引錯誤：{e}")
        return index_name

    # if use_bulk:
    #     actions = [{"_index": index_name, "_source": doc} for doc in documents]
    #     bulk(es_client, actions)
    # else:
    for doc in tqdm(documents):
        es_client.index(index=index_name, document=doc)

    return index_name




def elastic_search(query, index_name, search_fields, num_results=5, course_filter=None):
    fields_with_boost = [f"{field}^{boost}" for field, boost in search_fields.items()]
    
    bool_query = {
        "must": {
            "multi_match": {
                "query": query,
                "fields": fields_with_boost,
                "type": "best_fields"
            }
        }
    }

    # 有選課程就加上 filter
    if course_filter and course_filter != "不過濾":
        bool_query["filter"] = {
            "term": {
                "course": course_filter
            }
        }

    search_query = {
        "size": num_results,
        "query": {
            "bool": bool_query
        }
    }

    response = es_client.search(index=index_name, body=search_query)
    
    result_docs = []
    
    for hit in response['hits']['hits']:
        doc = hit["_source"]
        doc["_score"] = hit["_score"]  # ✅ 把 _score 加入
        result_docs.append(doc)
    
    return result_docs
