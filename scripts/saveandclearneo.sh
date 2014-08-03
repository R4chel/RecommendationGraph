#!/bin/sh
echo "++: saving and clearing neo4j"
neo4j stop
rm -rf $1
mv -f /usr/local/Cellar/neo4j/2.1.2/libexec/data $1
mkdir /usr/local/Cellar/neo4j/2.1.2/libexec/data
neo4j start
