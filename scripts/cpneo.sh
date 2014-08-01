#!/bin/sh
neo4j stop
mv -f /msr/local/Cellar/neo4j/2.1.2/libexec/data /usr/local/Cellar/neo4j/2.1.2/libexec/data.backup
rm -r /usr/local/Cellar/neo4j/2.1.2/libexec/data
cp -r $1 /usr/local/Cellar/neo4j/2.1.2/libexec/data
neo4j start

