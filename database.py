# configure database for other files
import os
from py2neo import neo4j
from urlparse import urlparse


# this is how Heroku tells your app where to find the database.
if os.environ.get('NEO4J_URL'):
    graph_db_url = urlparse(os.environ.get('NEO4J_URL'))
    # set up authentication parameters
    neo4j.authenticate("{host}:{port}".format(host=graph_db_url.hostname, port=graph_db_url.port), graph_db_url.username, graph_db_url.password)

    # connect to authenticated graph database
    GRAPHDB = neo4j.GraphDatabaseService('http://{host}:{port}/db/data'.format(host=graph_db_url.hostname, port=graph_db_url.port))
# local connection
else:
    GRAPHDB = neo4j.GraphDatabaseService('http://localhost:7474/db/data')
