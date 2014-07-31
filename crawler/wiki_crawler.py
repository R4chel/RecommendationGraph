''' 
Created July 28, 2014

@author Adam Campbell, Rachel Ehrlich, Max Fowler
'''

from settings import GRAPHDB
from enum import Enum
import pywikibot
from py2neo import neo4j, cypher
import re
import unicodedata

def crawl_pages(input_pages, depth):
    pages_to_crawl = map((lambda x: (x, depth)), input_pages)
    pages_to_link = []
    site = pywikibot.getSite('en')

    i = 0
    while len(pages_to_crawl) > 0:
        (page, depth_remaining) = pages_to_crawl.pop()
        pages_to_link.append(page)
        depth_remaining -= 1
        title = clean_title(page)
        infoboxes = get_infoboxes(page)
        node = add_page_to_db(title, infoboxes)

        categories = get_categories(page)
        for category in categories:
            adj_node = add_category_to_db(category)
            path = neo4j.Path(node, "has category", adj_node)
            path.get_or_create(GRAPHDB)

        if depth_remaining >= 0:
            linked_pages = page.linkedPages()
            for link in linked_pages:
                link_title = clean_title(link)

                if filter(link_title.startswith, ["File:", "Category:", "Wikipedia:", "Template:"]):
                    continue
                language_regex = re.compile("^[a-zA-Z][a-zA-Z]:.*$")
                if language_regex.match(link_title):
                    print "DEBUG: Rejecting language based title: " + link_title
                    continue
                pages_to_crawl.append((link, depth_remaining))
        print i
        i += 1
    print "******* " + str(len(pages_to_link))
    j = 0
    for page in pages_to_link:
        page_title = clean_title(page)
        page_node = GRAPHDB.get_indexed_node("TitleIndex", "title", page_title)
        links = page.linkedPages()

        for link in links:
            link_title = clean_title(link)
            if filter(link_title.startswith, ["File:", "Category:", "Wikipedia:", "Template:"]):
                continue


            adj_node = GRAPHDB.get_indexed_node("TitleIndex", "title", link_title)
            if adj_node:
                path = neo4j.Path(page_node, "links_to", adj_node)
                path.get_or_create(GRAPHDB)
        print j
        j += 1



def add_page_to_db(title, labels=[]):
    node = GRAPHDB.get_or_create_indexed_node("TitleIndex", "title", title, {"title": title})
    for label in labels:
        node.add_labels(label)
#    node.add_labels("Page")
    return node

def add_category_to_db(category):
    node = GRAPHDB.get_or_create_indexed_node("TitleIndex", "title", category, {"title": category})
    node.add_labels("Category")
    return node

def get_template_pages(searchtype, param):
    site = pywikibot.getSite('en')
    infobox_template = pywikibot.Page(site, searchtype + param)
    pages = list(infobox_template.embeddedin(False, 0))
    return pages

def get_category_pages(cat_name, recurse):
    site = pywikibot.getSite('en')
    cat = pywikibot.Category(site, cat_name)
    return list(cat.members(recurse=recurse))

def get_page(page_name):
    site = pywikibot.getSite('en')
    return pywikibot.Page(site, page_name)

def get_infoboxes(page):
    templates = []
    for template in page.itertemplates():
        template_title = clean_title(template)
        if template_title.startswith(u'Template:Infobox '):
            templates.append(template_title[len('Template:'):])
    return templates

HIDDEN_CATEGORY = pywikibot.Category(pywikibot.getSite('en'), 'Category:Hidden categories')
def get_categories(page):
    categories = []
    for category in page.categories():

        if not list(category.categories()).__contains__(HIDDEN_CATEGORY):
            categories.append(clean_title(category))
    return categories

def clean_title(s):
    return unicodedata.normalize('NFKD', s.title()).encode('ascii','ignore').split('#')[0]

class SearchType(Enum):
    infobox = "Template:Infobox "
    category = "Category:"
    template = "Template:"
    page = "Page"

if __name__ == '__main__':
    query = 'Software companies based in the San Francisco Bay Area'
    search_depth = 0
    searchtype = SearchType.category

    if searchtype in [SearchType.infobox, SearchType.template]:
        pages = get_template_pages(searchtype, query)
    else if searchtype == SearchType.category:
        pages = get_category_pages(query, True)
    else if searchtype == SearchType.page:
        pages = [get_page(query)]
    crawl_pages(pages, search_depth)
