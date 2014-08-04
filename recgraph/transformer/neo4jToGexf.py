# takes everything in the neo4j database and puts it into a gexf file

import os

from py2neo import cypher
import gexf, datetime

from recgraph.settings import GRAPHDB, PROJECT_PATH


def neo4jToGexf(output_file):
    print "++ neo4jToGexf"

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
        node_name = node["name"]
        # add it to the graph
        n=graph.addNode(node_id,node_name)
        n.addAttribute(infobox_attribute_id,infobox)

    # edges
    # paginated version
    result, metadata = cypher.execute(GRAPHDB, "START r=relationship(*) return count(r)")
    total = result[0][0]
    print "total: " + str(total)
    skip = 0
    limit = 50000
    found_edges = set([])
    edge_number = 0
    start_time = datetime.datetime.now()
    while skip < total:
        rows, metadata = cypher.execute(GRAPHDB, "MATCH (a)-[r]->(b) RETURN a,r,b  ORDER BY r.id SKIP %s LIMIT %s" % (skip,limit))
        for nodeA, rel, nodeB in rows:
            # weight = rel["weight"] # TODO: make this transformer
            weight = 1
            nodeA_id = nodeA._id
            nodeB_id = nodeB._id
            e=graph.addEdge(edge_number,nodeA_id,nodeB_id,weight)
            edge_number += 1
            skip += 1
            #e.setColor("255","0","0");
		    #e.addAttribute("blah","true")
            if not skip % 100:
                print "s: " + str(skip)
                now = datetime.datetime.now()
                time_delta = (now - start_time).total_seconds()
                percent_complete = float(skip) / float(total)
                if percent_complete:
                    percent_remaining = 1 - percent_complete
                    total_seconds_eta = time_delta * (1/percent_complete)
                    eta_seconds_remaining = total_seconds_eta * percent_remaining
                    print "---------"
                    print "percent complete: " + str(percent_complete)
                    print "elapsed: " + str(time_delta)
                    print "remaining: " + str(eta_seconds_remaining)
                else:
                    print "..."

    # unpaginated
    # rows, metadata = cypher.execute(GRAPHDB, "MATCH (a)-[r]->(b) RETURN a,r,b")
    # edge_number = 0
    # for nodeA, rel, nodeB in rows:
    #     weight = 1
    #     e=graph.addEdge(edge_number,nodeA._id,nodeB._id,weight)
    #     edge_number += 1
    #     #e.setColor("255","0","0");
    #     #e.addAttribute("blah","true")
    # if not edge_number % 1000:
    #     print "edge: " + str(edge_number)

    # write it
    with open(output_file,"w+") as f:
        g.write(f)

if __name__ == "__main__":
    data_path = os.path.join(PROJECT_PATH, "data")
    output_file_path = os.path.join(data_path, "test.gexf")
    neo4jToGexf(output_file_path)
