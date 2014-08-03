#!/bin/sh
neo4j stop
rm -r /usr/local/Cellar/neo4j/2.1.2/libexec/data 
mkdir /usr/local/Cellar/neo4j/2.1.2/libexec/data
neo4j start

