import os

from py2neo import cypher

from recgraph.relevancy.randomRelevancy import randomRelevancyEdges
from recgraph.relevancy.simpleRelevancy import simpleRelevancyEdges
from recgraph.relevancy.convertToJson import outputD3JSON, outputSigmaJSON
from recgraph.settings import STATIC_PATH, GRAPHDB



# settings which determine how relevancy and is calculated and which visualization is being used
WHICH_RELEVANCY_ALGORITHM = "random"
WHICH_VIS = "d3"


def clearRelevancy():
    cypher.execute(GRAPHDB, "MATCH ()-[r:RELEVANCY]->() DELETE r")


def calculateRelevancy():

    # clear old relevancy
    clearRelevancy()

    # calculate relevancy
    if WHICH_RELEVANCY_ALGORITHM == "random":
        randomRelevancyEdges()
    elif WHICH_RELEVANCY_ALGORITHM == "simple":
        simpleRelevancyEdges()
    else:
        print "+EE+: Unknown Relevancy Algorithm"

    # output graph to json file in static directory
    if WHICH_VIS == "d3":
        output_file_path = os.path.join(STATIC_PATH, "d3graph.json")
        outputD3JSON(output_file_path)
    elif WHICH_VIS == "sigma":
        output_file_path = os.path.join(STATIC_PATH, "sigmagraph.json")
        outputSigmaJSON(output_file_path)


if __name__ == "__main__":
    calculateRelevancy()
