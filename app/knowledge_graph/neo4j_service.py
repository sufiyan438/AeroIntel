import os

from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

class Neo4jService:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            "bolt://127.0.0.1:7687",
            auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
        )

    def execute(self, query, parameters=None):
        with self.driver.session(database="neo4j") as session:

            result = session.run(
                query,
                parameters or {}
            )

            # Fetch all rows before closing the session
            return list(result)

    def close(self):
        self.driver.close()