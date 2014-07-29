''' 
Created July 28, 2014

@author Adam Campbell, Rachel Ehrlich, Max Fowler
'''

#from database import GRAPHDB
import mwparserfromhell
import pywikibot
from py2neo import neo4j, cypher
import re

GRAPHDB = neo4j.GraphDatabaseService()

def load_by_infobox_type(infobox_type):
    pages = get_pages(infobox_type)
    print len(pages)
    i = 0
    for page in pages:
        title = page.title().encode("UTF-8").split('#')[0]
        node = add_title_to_db(title, [infobox_type])
        text = page.get()
        parsed = mwparserfromhell.parse(text)
        links = parsed.filter_wikilinks()
        for link in links:
            link_title = link.title.encode("UTF-8").split('#')[0]
            adj_node = add_title_to_db(link_title)
            path = neo4j.Path(node, "links_to", adj_node)
            path.get_or_create(GRAPHDB)
        print i
        i += 1

def add_title_to_db(title, labels=[]):
    node = GRAPHDB.get_or_create_indexed_node("TitleIndex", "title", title, {"title": title})
    for label in labels:
        node.add_labels(label)
    return node

def get_pages(infobox_type):
    site = pywikibot.getSite('en')
    infobox_template = pywikibot.Page(site, "Template:Infobox " + infobox_type)
    pages = list(infobox_template.embeddedin(False, 0))
    return pages

if __name__ == '__main__':
    load_by_infobox_type("Star Wars character")
