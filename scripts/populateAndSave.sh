BDIR=/Users/mfowler/Desktop/dev/RecommendationGraph/
SCRIPTSDIR=$BDIR/scripts
OUTPUTDIR=$BDIR/data/output

#echo "SCRIPTSDIR: "$SCRIPTSDIR
#echo "OUTPUTDIR: "$OUTPUTDIR

# activate virtualenv
source /Users/mfowler/Desktop/dev/virtualenv/recgraph/bin/activate

# clear
echo "++: clearing old database"
$SCRIPTSDIR/clearneo.sh

# populate
echo "++: populating db with "$1
python $BDIR/recgraph/crawler/dbpedia_crawler.py $1

# save
OUTPUTPATH=$OUTPUTDIR/$1.neo4j
echo "++: saving db to "$OUTPUTPATH
$SCRIPTSDIR/saveandclearneo.sh $OUTPUTPATH
