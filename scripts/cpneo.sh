#!/bin/sh
neo4j stop
mv /usr/local/Cellar/neo4j/2.1.2/libexec/data /usr/local/Cellar/neo4j/2.1.2/libexec/data.backup
cp -r $1 /usr/local/Cellar/neo4j/2.1.2/libexec/data
neo4j start

