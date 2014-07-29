# iterate through all nodes in database and create random test relevancy edges between them

from settings import GRAPHDB
from py2neo import neo4j, cypher
import random

def clearRelevancy():
    cypher.execute(GRAPHDB, "MATCH ()-[r:RELEVANCY]->() DELETE r")

def createTestRelevancy():
    clearRelevancy()
    def handle_row(row):
        nodeA = row[0]
        def handle_row_inner(inner_row):
            nodeB = inner_row[0]
            weight = random.random()
            if nodeA != nodeB:
                GRAPHDB.create((nodeA, "RELEVANCY", nodeB, {"weight": weight}),)
        # for each node in inner loop
        cypher.execute(GRAPHDB, "START z=node(*) RETURN z", row_handler=handle_row_inner)
    # for each node in outer loop
    cypher.execute(GRAPHDB, "START z=node(*) RETURN z", row_handler=handle_row)


if __name__ == "__main__":
    createTestRelevancy()