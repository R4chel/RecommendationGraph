''' 
Created July 28, 2014

@author Adam Campbell, Rachel Ehrlich, Max Fowler
'''

from database import GRAPHDB
import mwparserfromhell
import pywikibot

def load_by_infobox_type(infobox_type):
    pages = get_pages(infobox_type)
    for page in pages:
        title = page.title().strip().encode()
        node = GRAPHDB.get_or_create_indexed_node("TitleIndex", "title", title, {"title": title})
        node.add_labels(infobox_type)
        text = page.get()
        parsed = mwparserfromhell.parse(text)
        links = parsed.filter_wikilinks()
        for link in links:
            link_title = extract_title(link)

def extract_title(s):
    if s is not None:
        s = re.sub("\[\[","",s)
        s = re.sub("\]\]", "",s)
        l = s.split("|")
        s = l[0]
    return s

def get_pages(infobox_type):
    site = pywikibot.getSite('en')
    infobox_template = pywikibot.Page(site, "Template:Infobox " + infobox_type)
    pages = list(infobox_template.embeddedin(False, 0))
    return pages

