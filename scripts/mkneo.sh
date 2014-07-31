#!/bin/sh
neo4j stop
mv /usr/local/Cellar/neo4j/2.1.2/libexec/data /usr/local/Cellar/neo4j/2.1.2/libexec/data.$1
mkdir /usr/local/Cellar/neo4j/2.1.2/libexec/data
neo4j start

