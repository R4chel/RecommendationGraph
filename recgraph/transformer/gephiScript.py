# this script should be run through the gephi console, it does format and layout for graph
from time import sleep
import os

PROJECT_PATH = "/Users/mfowler/Desktop/dev/RecommendationGraph/"
INPUT_FILE = "data/neo4j.gexf"
OUTPUT_FILE = "static/output/test1.gexf"
i_file_name = INPUT_FILE
o_file_name = OUTPUT_FILE

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



