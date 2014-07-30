# convert all nodes in neo4j database into a json file which d3 can understand

from settings import GRAPHDB, STATIC_PATH
from py2neo import neo4j, cypher
import os, json

def outputD3JSON(output_file):

    nodes = []
    links = []
    node_id_to_index = {}

    to_output = {
        "nodes":nodes,
        "links":links
    }

    rows, metadata = cypher.execute(GRAPHDB, "MATCH (n) RETURN n")

    for index,row in enumerate(rows):
        node = row[0]
        node_id = node._id
        node_to_write = {
            "id":node_id
        }
        nodes.append(node_to_write)
        node_id_to_index[node_id] = index

    rows, metadata = cypher.execute(GRAPHDB, "MATCH (a)-[r:RELEVANCY]->(b) RETURN a,r,b")
    for nodeA, rel, nodeB in rows:
        weight = rel["weight"]
        edge_to_write = {
            "source":node_id_to_index[nodeA._id],
            "target":node_id_to_index[nodeB._id],
            "weight":weight
        }
        links.append(edge_to_write)

    to_write = json.dumps(to_output)
    with open(output_file, "w") as f:
        f.write(to_write)


def outputSigmaJSON(output_file):
    # TODO: implement this
    print "+EE: outputSigmaJson not yet implemented!"



if __name__ == "__main__":
    output_file_path = os.path.join(STATIC_PATH, "sigmagraph.json")
    outputSigmaJSON(output_file_path)