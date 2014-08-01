''' 
Created July 28, 2014

@author Adam Campbell, Rachel Ehrlich, Max Fowler
'''

import re
import unicodedata
import time

from py2neo import neo4j

from recgraph.settings import GRAPHDB
from enum import Enum
import pywikibot

SITE = pywikibot.getSite('en')

def crawl_pages(pages_to_crawl, depth_remaining, color=False):
    pages_to_crawl_next = []
    pages_to_link = []
    depth_remaining -= 1

    edge_batch = neo4j.WriteBatch(GRAPHDB)
    while pages_to_crawl:
        i = 0
        for page in pages_to_crawl:
            if page in pages_to_link:
                continue
            pages_to_link.append(page)
            
            title = clean_title(page.title())
            infoboxes = get_infoboxes(page)

            if color:
                node = add_color_to_db(title, infoboxes, get_hex(page))
            else:
                node = add_page_to_db(title, infoboxes)

            categories = get_categories(page)
            for category in categories:
                adj_node = add_category_to_db(category)
                edge_batch.get_or_create_path(node, "has_category", adj_node)
            if depth_remaining >= 0:
                linked_pages = get_links(page)
                for messy_link in linked_pages:
                    link_title = clean_title(messy_link.title.strip_code())
                    link = pywikibot.Page(SITE, link_title)
                    if filter(link_title.startswith, ["File:", "Category:", "Wikipedia:", "Template:"]):
                        continue
                    language_regex = re.compile("^[a-zA-Z][a-zA-Z]:.*$")
                    if language_regex.match(link_title):
                        print "DEBUG: Rejecting language based title: " + link_title
                        continue
                    pages_to_crawl_next.append(link)
            time.sleep(25)
            print str(i)
            i += 1

        pages_to_crawl = pages_to_crawl_next
        pages_to_crawl_next = []
        depth_remaining -= 1


    print "******* " + str(len(pages_to_link))
    j = 0
    for page in pages_to_link:
        page_title = clean_title(page.title())
        page_node = GRAPHDB.get_indexed_node("TitleIndex", "title", page_title)
        links = get_links(page)

        for messy_link in links:
            link_title = clean_title(messy_link.title.strip_code())
            if filter(link_title.startswith, ["File:", "Category:", "Wikipedia:", "Template:"]):
                continue


            adj_node = GRAPHDB.get_indexed_node("TitleIndex", "title", link_title)
            if adj_node:
                edge_batch.get_or_create_path(page_node, "links_to", adj_node)
        print j
        j += 1
    edge_batch.submit()


def add_page_to_db(title, labels=[]):
    node = GRAPHDB.get_or_create_indexed_node("TitleIndex", "title", title, {"title": title})
    for label in labels:
        node.add_labels(label)
#    node.add_labels("Page")
    return node

def add_color_to_db(title, labels=[], hex=None):
    if not hex:
        return add_page_to_db(title, labels)
    node = GRAPHDB.get_or_create_indexed_node("TitleIndex", "title", title, {"title": title, "hex": hex})
    for label in labels:
        node.add_labels(label)
    node.add_labels("Color")
    return node

def add_category_to_db(category):
    node = GRAPHDB.get_or_create_indexed_node("TitleIndex", "title", category, {"title": category})
    node.add_labels("Category")
    return node

def get_template_pages(searchtype, param):
    infobox_template = pywikibot.Page(SITE, searchtype + param)
    time.sleep(10)
    pages = infobox_template.embeddedin(False, 0)
    return pages

def get_category_pages(cat_name, recurse):
    cat = pywikibot.Category(SITE, cat_name)
    return cat.members(recurse=recurse)

def get_page(page_name):
    return pywikibot.Page(SITE, page_name)

def get_infoboxes(page):
    templates = []
    for template in page.itertemplates():
        template_title = clean_title(template.title())
        if template_title.startswith(u'Template:Infobox '):
            templates.append(template_title[len('Template:'):])
    return templates

HIDDEN_CATEGORY = pywikibot.Category(pywikibot.getSite('en'), 'Category:Hidden categories')
def get_categories(page):
    categories = []
    for category in page.categories():

        if not list(category.categories()).__contains__(HIDDEN_CATEGORY):
            categories.append(clean_title(category.title())[len("Category:"):])
    return categories

def get_links(page):
    text = page.get()
    parsed = pywikibot.mwparserfromhell.parse(text)
    return parsed.ifilter_wikilinks()

def clean_title(s):
    return unicodedata.normalize('NFKD', s).encode('ascii','ignore').split('#')[0]

def get_hex(page):
    regex = re.compile("hex\s*=\s*([0-9A-Fa-f]{6,6})",re.IGNORECASE)
    vals = regex.findall(page.get())
    if vals:
        return vals[0]
    return None

class SearchType(Enum):
    infobox = "Template:Infobox "
    category = "Category:"
    template = "Template:"
    page = "Page"

if __name__ == '__main__':
    START = time.time()
    print "START: 0.0"
    query = 'color'
    search_depth = 0
    searchtype = SearchType.infobox

    if searchtype in [SearchType.infobox, SearchType.template]:
        pages = get_template_pages(searchtype, query)
    elif searchtype == SearchType.category:
        pages = get_category_pages(query, False)
    elif searchtype == SearchType.page:
        pages = [get_page(query)]

    crawl_pages(pages, search_depth, True)

    ctime = time.time() - START
    print "END: " + str(ctime)
