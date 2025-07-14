from neo4j import GraphDatabase
import os

uri = os.getenv("GRAPH_DATABASE_URL", "bolt://neo4j:7687")  # 預設也用正確地址
user = os.getenv("GRAPH_DATABASE_USERNAME", "neo4j")
password = os.getenv("GRAPH_DATABASE_PASSWORD", "your_password_here")


driver = GraphDatabase.driver(uri, auth=(user, password))

with driver.session() as session:
    result = session.run("MATCH (n) RETURN count(n) as node_count")
    count = result.single()["node_count"]
    print("Neo4j node count:", count)

driver.close()
