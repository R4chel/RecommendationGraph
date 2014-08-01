# this script should be run through the gephi console, it does format and layout for graph
from time import sleep
import os

PROJECT_PATH = "/Users/mfowler/Desktop/dev/RecommendationGraph/"
FILES = [
    ("data/neo4j.gexf","static/output/test1.gexf"),
    ("data/neo4j.gexf","static/output/test2.gexf"),
    ("data/neo4j.gexf","static/output/test3.gexf"),
    ]

def processGraph(i_file_name, o_file_name):
    def getCurrentGraph():
        from org.gephi.graph.api import GraphController
        gc = Lookup.getDefault().lookup(GraphController);
        model = gc.getModel();
        graph = model.getGraph();
        return graph

    # delete all current nodes
    cGraph = getCurrentGraph()
    print "++I: clearing graph"
    cGraph.clear()

    # load a .gexf
    input_file = os.path.join(PROJECT_PATH, i_file_name)
    print "++I: importing graph " + input_file
    importGraph(input_file)

    # layout
    print "++I: computing layout"
    runLayout(RandomLayout)
    stopLayout()
    runLayout(ForceAtlas2)
    sleep(3)
    stopLayout()

    # export
    output_file = os.path.join(PROJECT_PATH, o_file_name)
    exportGraph(output_file)
    print "++I: output to " + output_file

# process each file
for INPUT_FILE, OUTPUT_FILE in FILES:
    processGraph(INPUT_FILE, OUTPUT_FILE)
    print "=================="
    sleep(5)

