BDIR=/Users/mfowler/Desktop/dev/RecommendationGraph/
SCRIPTSDIR=$BDIR/scripts
OUTPUTDIR=$BDIR/data/output
echo "SCRIPTSDIR: "$SCRIPTSDIR
echo "OUTPUTDIR: "$OUTPUTDIR
# activate virtualenv
source /Users/mfowler/Desktop/dev/virtualenv/recgraph/bin/activate
# clear
$SCRIPTSDIR/clearneo.sh
# populate
python $BDIR/recgraph/crawler/dbpedia_crawler.py $1
# save
# $SCRIPTSDIR/saveandclearneo.sh $OUTPUTDIR/$1.neo4j
