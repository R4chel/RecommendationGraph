import os

from flask import Flask, render_template
from py2neo import cypher

from recgraph.settings import GRAPHDB, STATIC_PATH, STATIC

# HELPERS
########################################################################################################################

def create_graph(GRAPHDB):

    # Do we have a node that has a 'name' property, which is set to the value 'Neo'?
    # We've probably been here before.
    data, metadata = cypher.execute(GRAPHDB, "START n=node(*) where n.name='Neo' return n")
    if not data:
        # Create two nodes, one for us and one for you.
        # Make sure they both have 'name' properties with values.
        from_node, to_node = GRAPHDB.create({"name": "Neo"}, {"name": "you"})

        # create a 'loves' relationship from the 'from' node to the 'to' node
        GRAPHDB.create((from_node, "loves", to_node),)

    # To learn more, read the excellent Neo4j Manual at http://docs.neo4j.org


def find_lovers(GRAPHDB):
    query = "START n=node(*) MATCH (n)-[r:loves]->(m) return n, r, m"
    # This is our awesome Cypher query language.
    # STARTing with all the nodes in the graph
    # MATCH the ones that have a LOVES relationship
    # and RETURN the starting node, the relationship, and the end node.
    data, metadata = cypher.execute(GRAPHDB, query)
    return data[0]


# PAGES
########################################################################################################################
app = Flask(__name__)
app.debug = True

@app.route('/hello/')
def hello():
    # Query the database
    result = find_lovers(GRAPHDB)
    # Pull out the data we want from the single row of results
    return result[0]['name'] + " " + result[1].type + " " + result[2]['name']

@app.route('/test/')
def testPage():
    return render_template('test.html', name="Johnson")

@app.route('/')
def blogPage():
    return render_template('graphsblog.html', name="Johnson")

@app.route('/sigmajs/<path:path>/')
def sigmajsTemplate(path):
    return render_template('sigmajstemplate.html', which=path, static=STATIC)

@app.route('/sigma/<path:path>/')
def sigmaVis(path):
    if path == "sf1":
        graphjs = "sf.js"
    else:
        graphjs = "sigmavis1.js"
    gexf_path = STATIC + "output/" + path + ".gexf"
    return render_template('sigmavis.html', graphjs=graphjs, gexf_path=gexf_path, static=STATIC)


# STATIC
########################################################################################################################
@app.route('/static/<path:path>')
def static_proxy(path):
    print "STATIC PATH: " + STATIC_PATH
    file_path = os.path.join(STATIC_PATH, path)
    return app.send_static_file(file_path)


#  RUN FLASK APP
########################################################################################################################
if __name__ == '__main__':
    # Connect to the database

    # Make sure our reference data is there
    # create_graph(GRAPHDB)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)








