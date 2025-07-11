from neo4j import GraphDatabase
import os

os.environ["GRAPH_DATABASE_URL"] = "bolt://localhost:7687"
os.environ["GRAPH_DATABASE_USERNAME"] = "neo4j"
os.environ["GRAPH_DATABASE_PASSWORD"] = "your_password_here"


uri = os.getenv("GRAPH_DATABASE_URL")
user = os.getenv("GRAPH_DATABASE_USERNAME")
password = os.getenv("GRAPH_DATABASE_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(user, password))

with driver.session() as session:
    result = session.run("MATCH (n) RETURN count(n) as node_count")
    count = result.single()["node_count"]
    print("Neo4j node count:", count)

driver.close()
