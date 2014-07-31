# takes everything in the neo4j database and puts it into a gexf file

import os

from py2neo import cypher
import gexf

from recgraph.settings import GRAPHDB, PROJECT_PATH


def neo4jToGexf(output_file):
    print "++ neo4jToGef"

    # use gexf to write
    g = gexf.Gexf("recgraph","neo4j gexf output")
    graph=g.addGraph("directed","static","neo4j graph")
    # add infobox attribute to graph
    infobox_attribute_id = graph.addNodeAttribute("infobox","none", "string")

    # nodes
    rows, metadata = cypher.execute(GRAPHDB, "MATCH (n) RETURN n")
    for index,row in enumerate(rows):
        node = row[0]
        # set the infobox if there is one
        labels = node.get_labels()
        if labels:
            infobox = list(labels)[0]
        else:
            infobox = "none"
        node_id = node._id
        # get the title of the node
        node_name = node["title"]
        # add it to the graph
        n=graph.addNode(node_id,node_name)
        n.addAttribute(infobox_attribute_id,infobox)

    # edges
    # rows, metadata = cypher.execute(GRAPHDB, "MATCH (a)-[r:RELEVANCY]->(b) RETURN a,r,b")
    rows, metadata = cypher.execute(GRAPHDB, "MATCH (a)-[r]->(b) RETURN a,r,b")
    edge_number = 0
    for nodeA, rel, nodeB in rows:
        # weight = rel["weight"] # TODO: make this relevancy
        weight = 1
        e=graph.addEdge(edge_number,nodeA._id,nodeB._id,weight)
        edge_number += 1
        #e.setColor("255","0","0");
		#e.addAttribute("blah","true")

    # write it
    with open(output_file,"w+") as f:
        g.write(f)

if __name__ == "__main__":
    data_path = os.path.join(PROJECT_PATH, "data")
    output_file_path = os.path.join(data_path, "neo4j.gexf")
    neo4jToGexf(output_file_path)