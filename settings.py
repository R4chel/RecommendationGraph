import os
from py2neo import neo4j
from urlparse import urlparse

# root project path
PROJECT_PATH = os.path.dirname(__file__)
STATIC_PATH = os.path.join(PROJECT_PATH, "static")

NEO4J_URL = os.environ.get('NEO4J_URL')
USE_REMOTE_DB = os.environ.get('USE_REMOTE_DB')
# database configuration
if NEO4J_URL and USE_REMOTE_DB:
    graph_db_url = urlparse(os.environ.get('NEO4J_URL'))
    # set up authentication parameters
    neo4j.authenticate("{host}:{port}".format(host=graph_db_url.hostname, port=graph_db_url.port), graph_db_url.username, graph_db_url.password)

    # connect to authenticated graph database
    GRAPHDB = neo4j.GraphDatabaseService('http://{host}:{port}/db/data'.format(host=graph_db_url.hostname, port=graph_db_url.port))
# local connection
else:
    NEO4J_URL = "http://localhost:7474/db/data/"
    GRAPHDB = neo4j.GraphDatabaseService(NEO4J_URL)
