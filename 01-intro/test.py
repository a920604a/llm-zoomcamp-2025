from llm import llm, build_prompt
from es import elastic_search, elastic_index
from fetch_data import fetch_documents


def rag(query, index_name):
    search_fields = {"question": 4, "text": 1}
    # course_filter  = "machine-learning-zoomcamp"
    search_results = elastic_search(query, "course-questions", search_fields)
    print("search_results", search_results)
    prompt = build_prompt(query, search_results)
    answer = llm(prompt)
    return answer


if __name__ == "__main__":
    documents = fetch_documents()
    
    index_name = elastic_index(documents)
    
    query = "how do I run kafka?"
    # print(f"query = {query}")
    ans = rag(query, index_name)
    print(f"ans = {ans}")
