# takes everything in the neo4j database and puts it into a gexf file

from settings import GRAPHDB, STATIC_PATH
from py2neo import neo4j, cypher
import gexf, os


def neo4jToGexf(output_file):
    print "++ neo4jToGef"

    # use gexf to write
    g = gexf.Gexf("recgraph","neo4j gexf output")
    graph=g.addGraph("directed","static","neo4j graph")

    # nodes
    rows, metadata = cypher.execute(GRAPHDB, "MATCH (n) RETURN n")
    for index,row in enumerate(rows):
        node = row[0]
        node_id = node._id
        node_name = node_id # TODO: change this
        n=graph.addNode(node_id,node_name)

        #n.addAttribute(idAttType,"institution")

    # edges
    rows, metadata = cypher.execute(GRAPHDB, "MATCH (a)-[r:RELEVANCY]->(b) RETURN a,r,b")
    edge_number = 0
    for nodeA, rel, nodeB in rows:
        weight = rel["weight"]
        e=graph.addEdge(edge_number,nodeA._id,nodeB._id,weight)
        edge_number += 1
        #e.setColor("255","0","0");
		#e.addAttribute("blah","true")

    # write it
    with open(output_file,"w+") as f:
        g.write(f)

if __name__ == "__main__":
    output_file_path = os.path.join(STATIC_PATH, "neo4j.gexf")
    neo4jToGexf(output_file_path)