''' 
Created July 28, 2014

@author Adam Campbell, Rachel Ehrlich, Max Fowler
'''

from settings import GRAPHDB
import mwparserfromhell
import pywikibot
from py2neo import neo4j, cypher
import re

def load_by_infobox_type(infobox_type, depth):
    found_pages = get_pages(infobox_type)
    pages_to_crawl = map((lambda x: (x, depth)), found_pages)
    pages_to_link = []

    i = 0
    while len(pages_to_crawl) > 0:
        (page, depth_remaining) = pages_to_crawl.pop()
        pages_to_link.add(page)
        depth_remaining = depth_remaining - 1

        title = page.title().encode("UTF-8").split('#')[0]
        #TODO: use the actual infobox_type here; discard if none?
        node = add_title_to_db(title, [infobox_type])

        if depth_remaining >= 0:
            text = page.get()
            parsed = mwparserfromhell.parse(text)
            links = parsed.filter_wikilinks()
            for link in links:
                link_title = link.title.encode("UTF-8").split('#')[0]
                #TODO: wikipedia get page with link_title
                #TODO: add that page to pages_to_crawl in tuple (page, depth_remaining)
        print i
        i += 1

    for page in pages_to_link:
        text = page.get()
        parsed = mwparserfromhell.parse(text)
        links = parsed.filter_wikilinks()

        for link in links:
            #TODO: if other end of link is in database, connect the two
            #path = neo4j.Path(node, "links_to", adj_node)
            #path.get_or_create(GRAPHDB)


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
    load_by_infobox_type("Star Wars character", 0)
