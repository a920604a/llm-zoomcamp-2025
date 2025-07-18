import streamlit as st
# from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch.helpers import bulk
import requests
import json
import os
from tqdm.auto import tqdm
from llm import build_prompt, llm
from es import elastic_index, elastic_search
from fetch_data import fetch_documents
import tiktoken

# -------------------- Streamlit UI --------------------

st.set_page_config(page_title="Course FAQ Search", layout="wide")
st.title("📚 Course QA Search with Elasticsearch")

with st.sidebar:
    st.header("設定")
    if st.button("重新建立索引"):
        docs = fetch_documents()
        elastic_index(docs)
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

    st.header("課程篩選")
    course_filter = st.selectbox(
        "選擇要篩選的課程（可選）",
        ["不過濾", "data-engineering-zoomcamp", "mlops-zoomcamp", "machine-learning-zoomcamp"]
    )

st.markdown("請輸入你的問題關鍵字：")

query = st.text_input("Query", value="how do I run kafka?")

if query:
    with st.spinner("搜尋中..."):
        print(search_fields)
        hits = elastic_search(query, "course-questions", search_fields, 5, course_filter)

    print(f"hits: {hits}")
    if hits:
        st.markdown("## 📄 Elasticsearch 原始搜尋結果（前 5 筆）")
        top_score = hits[0]['_score']
        print(top_score)
        st.markdown(f"### 🔍 Top Result Score: `{top_score:.2f}`\n")

        for i, hit in enumerate(hits, 1):
            st.subheader(f"📄 結果 {i} — Score: {hit['_score']:.2f}")
            st.markdown(f"**Section:** {hit['section']}")
            st.markdown(f"**Question:** {hit['question']}")
            st.markdown(f"**Answer:** {hit['text']}")
            st.markdown("---")

    else:
        st.warning("查無結果")

    prompt = build_prompt(query, hits)
    print(f"Prompt: {prompt}")
    print(f"Length of prompt: {len(prompt)}")

    enc = tiktoken.encoding_for_model("gpt-4o")
    tokens = enc.encode(prompt)
    print(f"Token 數量: {len(tokens)}")

    answer = llm(prompt)
    print(f"Answer: {answer}")

    # --- 分隔區塊 ---
    st.markdown("---")

    formatted_answer = answer.replace('\n', '<br>')

    with st.container():
        st.markdown("## 🤖 ChatGPT 綜合回覆")
        st.markdown("""
        <div style='padding: 1rem; background-color: #f0f4f9; border-left: 5px solid #2684FF; border-radius: 6px;'>
            📘 <b>本回覆由 AI 綜合 RAG 原始資料庫後生成，請斟酌參考使用。</b>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        with st.expander("📖 點此展開 AI 回覆內容", expanded=True):
            st.markdown(
                f"<div style='background-color: #ffffff; padding: 1rem; border-radius: 6px; "
                f"box-shadow: 0 0 8px rgba(0, 0, 0, 0.05); white-space: pre-wrap; font-family: monospace;'>"
                f"{formatted_answer}"
                f"</div>",
                unsafe_allow_html=True
            )
