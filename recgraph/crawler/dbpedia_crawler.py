# crawls dbpedia and populates a neo4j database

from recgraph.settings import PROJECT_PATH, GRAPHDB
import os,datetime,subprocess,time,sys
from py2neo import neo4j, node, rel


# what file has the links
links_file = os.path.join(PROJECT_PATH, "data/page_links_en.nt")


# helpers
def stripLink(link):
    link = link[1:-1]
    return link

def getNameFromLink(link):
    name = link.replace("http://dbpedia.org/resource/", "")
    return name


# iteratively expand the set of found pages
def crawlDbPedia(starting_pages, search_depth):
    found_pages = set(starting_pages)
    found_links = set([])
    # after this loop has run, found_links and found_pages should both be fully populated to appropriate search depth
    for i in range(search_depth):
        is_last_step = (i == search_depth-1) # on the last step of crawling, we only look for links between pages already found
        if is_last_step:
            expand = False
        else:
            expand = True
        # crawl one step deeper
        found_pages, found_links = crawlOneStepDeeper(found_pages, expand)
    return found_pages, found_links


def crawlOneStepDeeper(starting_pages, expand=True):
    found_pages = set(starting_pages.copy()) # just making sure found_pages is distinct object from starting_pages
    found_links = set([])
    # iterate through file
    with open(links_file, "r") as f:
        total = 172308908 # total number of links in dbpedia set
        i = 0
        start_time = datetime.datetime.now()
        for line in f:
            splitted = line.split()
            pageA = stripLink(splitted[0])
            pageB = stripLink(splitted[2])
            # if expand=True, then we include any link which starts in starting set even if it goes outside
            if (expand) and (pageA in starting_pages):
                found_links.add((pageA, pageB))
                found_pages.add(pageA)
                found_pages.add(pageB)
            # elif expand=False, then we only include links which are between nodes already in starting set
            elif (not expand) and (pageA in starting_pages) and (pageB in starting_pages):
                found_links.add((pageA, pageB))
                found_pages.add(pageA)
                found_pages.add(pageB)
            # profiling
            if not (i % 1000000):
                print pageA + " - " + pageB
                now = datetime.datetime.now()
                time_delta = (now - start_time).total_seconds()
                percent_complete = float(i) / float(total)
                if percent_complete:
                    percent_remaining = 1 - percent_complete
                    total_seconds_eta = time_delta * (1/percent_complete)
                    eta_seconds_remaining = total_seconds_eta * percent_remaining
                    print "---------"
                    print "percent complete: " + str(percent_complete)
                    print "elapsed: " + str(time_delta)
                    print "remaining: " + str(eta_seconds_remaining)
                else:
                    print "..."
            # increment
            i+=1
        print "=================="
        print "FOUND PAGES: " + str(len(found_pages))
        print "FOUND LINKS: " + str(len(found_links))
        print "=================="
        return found_pages, found_links


def saveToNeo4jBatch(found_pages, found_links):
    url_index = GRAPHDB.get_or_create_index(neo4j.Node, "UrlIndex")
    pageToNode = {}
    for page in found_pages:
        name = getNameFromLink(page)
        node = GRAPHDB.create({"name":name, "url":page})[0]
        # TODO: add labels based on infobox
        pageToNode[page] = node
    # save links
    i = 0
    batch = neo4j.WriteBatch(GRAPHDB)
    for link in found_links:
        pageA, pageB = link
        nodeA = pageToNode.get(pageA)
        nodeB = pageToNode.get(pageB)
        batch.create(rel(nodeA, "links_to", nodeB))
        if not i % 100:
            print "i: " + str(i)
            batch.run()
        i += 1
    batch.run()


def saveToNeo4j(found_pages, found_links):
    print "++: saving to neo4j"
    title_index = GRAPHDB.get_or_create_index(neo4j.Node, "TitleIndex")
    i=0
    for link in found_links:
        pageA, pageB = link
        nodeA = title_index.get_or_create("title", pageA, {"title": pageA})
        nodeB = title_index.get_or_create("title", pageB, {"title": pageB})
        GRAPHDB.create((nodeA, "links_to", nodeB))
        if not i % 100:
            print i
        i += 1



def crawlAndSave(starting_pages, search_depth):
    # crawl
    found_pages, found_links = crawlDbPedia(starting_pages, search_depth)
    # save to neo4j
    saveToNeo4jBatch(found_pages, found_links)
    # saveToNeo4j(found_pages, found_links)


# TODO: this function doesn't work
def backupDatabaseAndClear(db_title):
    # move old database to output_path and then clear it
    old_db_path = "/usr/local/Cellar/neo4j/2.1.2/libexec/data"
    output_dir = os.path.join(PROJECT_PATH, "data/output")
    output_path = os.path.join(output_dir, db_title + ".neo4j")
    script_path = os.path.join(PROJECT_PATH, "scripts/saveandclearneo.sh")
    # execute in subprocess
    my_env = os.environ.copy()
    my_env["PATH"] = "/usr/local/bin:" + my_env["PATH"]
    args = [script_path, output_path]
    subprocess.Popen(args, env=my_env)
    # just in case neo4j stopped for some reason
    print "++: sleeping 10 and then restarting neo4j ..."
    # TODO: neo4j won't start for some reason :(
    time.sleep(20)
    start_script_path = os.path.join(PROJECT_PATH, "scripts/startneo.sh")
    subprocess.Popen([start_script_path], env=my_env)


##################################################################################
# to crawl
# TO_CRAWL = [
#     "Music","Art","Book","Mathematics","Science","History","Sex","Philosophy",
#     "United_States","Computer_Science","Sport","Drug","Coffee","Palantir","Refrigerator"
# ]

TO_CRAWL = [
    "Music"
]

def multiPopulate():
    search_depth = 2
    errors = []
    success = []
    for crawl_set in TO_CRAWL:
        try:
            startings_pages = ["http://dbpedia.org/resource/" + crawl_set]
            crawlAndSave(startings_pages, search_depth)
            success.append(crawl_set)
            backupDatabaseAndClear(crawl_set)
        except Exception as e:
            print "e: " + e.message
            errors.append(crawl_set)
    print "$$$$$$$$$$$$$$$$$$$$$$$"
    for s in success:
        print "success: " + s
    for e in errors:
        print "error: " + e


def populateNeo4j(name, search_depth):
    startings_pages = ["http://dbpedia.org/resource/" + name]
    crawlAndSave(startings_pages, search_depth)


if __name__ == "__main__":
    crawl_name = sys.argv[1]
    print "PROCESSING: " + crawl_name
    search_depth = 2
    populateNeo4j(crawl_name, search_depth)






