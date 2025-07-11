import os
import asyncio

# 一定要在 import cognee 前設好 DB URL
# db_path = os.path.abspath("cognee_internal.db")
db_path = "/tmp/test_cognee.db"
os.environ["COGNEE_DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
open(db_path, 'a').close()  # 建立空檔案

print("使用資料庫：", db_path)
os.environ["COGNEE_DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"


from sqlalchemy import create_engine

engine = create_engine(f"sqlite:///{db_path}")  # 不要 +aiosqlite
with engine.connect() as conn:
    print("✅ 測試 DB 開啟成功")
# 如果你還有用 Neo4j，也設好
os.environ["GRAPH_DATABASE_PROVIDER"] = "neo4j"
os.environ["GRAPH_DATABASE_URL"] = "bolt://neo4j:7687"
os.environ["GRAPH_DATABASE_USERNAME"] = "neo4j"
os.environ["GRAPH_DATABASE_PASSWORD"] = "your_password_here"

# 然後才 import cognee
import cognee
from cognee.api.v1.search import SearchType

async def search_cognee(query, query_type=SearchType.SUMMARIES):
    try:
        results = await cognee.search(
            query_text=query,
            query_type=query_type,
        )
        return results
    except Exception as e:
        print("Cognee search 錯誤：", e)
        raise

async def main():
    results = await search_cognee("What endpoints does the Ticketmaster API provide?")
    print("Cognee 搜尋結果：")
    if results:
        print(results[0])
    else:
        print("沒有找到結果")

if __name__ == "__main__":
    asyncio.run(main())
