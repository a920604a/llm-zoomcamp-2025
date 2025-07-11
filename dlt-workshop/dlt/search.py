#!/usr/bin/env python
# coding: utf-8
import os

os.environ["GRAPH_DATABASE_PROVIDER"] = "neo4j"
os.environ["GRAPH_DATABASE_URL"] = "bolt://localhost:7687"
os.environ["GRAPH_DATABASE_USERNAME"] = "neo4j"
os.environ["GRAPH_DATABASE_PASSWORD"] = "your_password_here"


print("GRAPH_DATABASE_PROVIDER:", os.environ.get("GRAPH_DATABASE_PROVIDER"))
# print("GRAPH_DATABASE_URL:", os.environ.get("GRAPH_DATABASE_URL"))

import cognee
from cognee.api.v1.search import SearchType
from cognee.modules.engine.models import NodeSet

async def search_cognee(query, node_set, query_type=SearchType.GRAPH_COMPLETION):
    """
    使用 Cognee 執行查詢
    
    :param query: 查詢文字 (str)
    :param node_set: 節點集合名稱列表 (list of str)
    :param query_type: 查詢類型，預設為 GRAPH_COMPLETION
    :return: 查詢結果列表
    """
    answer = await cognee.search(
        query_text=query,
        query_type=query_type,
        node_type=NodeSet,
        node_name=node_set
    )
    return answer


async def main():
    # 明確告知 Cognee 使用 Neo4j
    
    
    # 查詢 Ticketmaster API 的端點
    results = await search_cognee(
        query="What API endpoints are in the Ticketmaster api? Give me specific endpoint urls.",
        node_set=['developer.ticketmaster.com']
    )
    print(results[0])

    # 查詢 Ticketmaster API 的認證方式
    # results = await search_cognee(
    #     query="What auth info do i need in the ticketmaster API?",
    #     node_set=['developer.ticketmaster.com']
    # )
    # print(results[0])

    # # 查詢 Ticketmaster API 的分頁資訊
    # results = await search_cognee(
    #     query="What pagination do i need in the ticketmaster API?",
    #     node_set=['developer.ticketmaster.com']
    # )
    # print(results[0])

    # # Broad Search (RAG 模式) 範例
    # results = await search_cognee(
    #     query="What sort of API information is in this knowledge graph?",
    #     node_set=['docs'],
    #     query_type=SearchType.RAG_COMPLETION
    # )
    # print(results[0])

    # # Focused Search 範例
    # results = await search_cognee(
    #     query="What sort of API information is in this knowledge graph?",
    #     node_set=['developer.ticketmaster.com']
    # )
    # print(results[0])


# 若此檔案作為主程式執行，請使用 asyncio 執行 main()
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
