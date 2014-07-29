''' 
Created July 28, 2014

@author Adam Campbell, Rachel Ehrlich, Max Fowler
'''

import database
import json
import pywikibot
import re
import time
import mwparserfromhell
from py2neo import neo4j, cypher
from settings import GRAPHDB

def get_pages(infobox_type):
    site = pywikibot.getSite('en')
    infobox_template = pywikibot.Page(site, "Template:Infobox " + infobox_type)
    pages = list(infobox_template.embeddedin(False, 0))
    return pages

def parse_title(title):
    site = pywikibot.getSite('en')
    page = pywikibot.Page(site, title)
    return parse_page(page)

def parse_page(page):
    text = page.get()
    return mwparserfromhell.parse(text)

def clean(s):
    ''' remove references and comments '''
    if s is not None:
        s = re.sub("<ref>([^<>])*</ref>","",s)
        s = re.sub("<ref name([^<>])*/>","",s)
        s = re.sub("<ref name([^<>])*>([^<>])*</ref>","",s)
        s = re.sub("<!--([^<>])*-->","",s)
        s = re.sub("<br>","")
        s = re.sub("<br/>",", ",s)
        s = re.sub("<br />",", ",s)
        s = s.strip()
        s = s.strip(',')
    return s

def extract_title(s):
    if s is not None:
        s = re.sub("\[\[","",s)
        s = re.sub("\]\]", "",s)
        l = s.split("|")
        s = l[0]
    return s
 

'''def get_infobox(page):  
    #check if title is in list
    val = wikipedia_utils.GetWikipediaPage(title)
    if val is None:
        return None
    res = wikipedia_utils.ParseTemplates(val["text"])
    infobox_comedian = dict(res["templates"]).get("Infobox comedian")
    return infobox_comedian 
'''
def extract_list(str):
    if str is None:
        return
    str = clean(str)
    list = str.split(",")
    clean_list = []
    for item in list:
        clean_list.append(extract_title(item).encode())
    return clean_list    

def extract_names(str):
    if str is None:
        return
    regex = re.compile('\[\[([^\]\[]*)\]\]')
    clean_str = clean(str)
    print clean_str
    m = re.match(clean_str)
    if m is None: 
        return []
    return m.groups()

def extract_names_for_db(str):
    if str is None:
        return
    regex = re.compile('\[\[([^\]\[]*)\]\]')
    clean_str = clean(str)
    print clean_str
    m = re.findall(regex, clean_str)
    if m is None: 
        return []
    return m

def write_edges_to_db(db, node, list, category, relationship, is_forward):
    if list is None:
        return
    for item in list:
        item = extract_title(item).strip().lower().encode()
        if len(item) == 0:
            continue 
        new_node = db.get_or_create_indexed_node("NameIndex", category, item, {category: item})
        new_node.add_labels(category.title())
        path = neo4j.Path(node, relationship, new_node) if is_forward else neo4j.Path(new_node, relationship, new_node)
        path.get_or_create(db)

def store_edges_to_db(db,infobox_label,rel_label, is_forward_rel):
    nodes = get_all_comedian_nodes(db)
    print len(nodes)
    i = 0
    for row in nodes:
        time.sleep(2)  #
        print i
        i += 1
        node = row[0]
        props = node.get_properties()
        name = props['name']
        infobox = get_infobox(name)
        if infobox is not None:        
            list = extract_names_for_db(infobox.get(infobox_label))
            write_edges_to_db(db, node, list,infobox_label, rel_label, is_forward_rel)
    

def open_db():
    return GRAPHDB

def store_people_to_db(people, db):
    for person in people:
        name = person.title().strip().encode()
        node = db.get_or_create_indexed_node("NameIndex", "name", name, {"name": name})
        node.add_labels("Person", "ComedianInfobox")


def get_all_people_nodes(db):
    nodes, metadata = cypher.execute(db, "START n=node(*) MATCH (n:Person) RETURN n")
    return nodes

def get_all_comedian_nodes(db):
    nodes, metadata = cypher.execute(db, "START n=node(*) MATCH (n:ComedianInfobox) RETURN n")
    return nodes

def print_influence_edge_list_for_gephi(db):
    fout = open('influence_edge_list_gephi.csv', 'w')
    influence_results, metadata = cypher.execute(db, "START n=node(*) MATCH (n)-[b:INFLUENCED]->(c) RETURN n,c")
    for row in influence_results:
        person1_props = row[0].get_properties()
        person1 = person1_props['name']
        person2_props = row[1].get_properties()
        person2 = person2_props['name']
        str = person2 + "," + person1
        fout.write(str+"\r\n")
    fout.close()

def print_edge_list(db):
    fout = open('topic_edge_list.txt', 'w')
    topic_results, metadata = cypher.execute(db, "START n=node(*) MATCH (n)-[b:SPOKE_ABOUT]->(c) RETURN n,c")
    for row in topic_results:
        person_props = row[0].get_properties()
        person = person_props['name']
        topic_props = row[1].get_properties()
        topic = topic_props['subject']
        str = person + "#" + topic + "#S"
        print str
        fout.write(str+"\r\n")
    fout.close()
    fout = open('influence_edge_list.txt', 'w')
    influence_results, metadata = cypher.execute(db, "START n=node(*) MATCH (n)-[b:INFLUENCED]->(c) RETURN n,c")
    for row in influence_results:
        person1_props = row[0].get_properties()
        person1 = person1_props['name']
        person2_props = row[1].get_properties()
        person2 = person2_props['name']
        str = person1 + "#" + person2 + "#I"
        fout.write(str+"\r\n")
    fout.close()
    
def convert_to_json_influence(db):
    name_dict = {}
    nodes_list = []
    edge_list = []
    nodes, metadata = cypher.execute(db, "START n=node(*) MATCH (n:ComedianInfobox) RETURN n")
    i = 0
    for row in nodes:
        node = row[0]
        props = node.get_properties()
        name = props['name']
        name_dict[name] = i
        json_str = '{"name": "'+ name + '"}'
        nodes_list.append(json_str)
        i += 1
    nodes_list_str = ",".join(nodes_list)
        
    influence_results, metadata = cypher.execute(db, "START n=node(*) MATCH (n:ComedianInfobox)-[b:INFLUENCED]->(c:ComedianInfobox) RETURN n,c")
    for row in influence_results:
        person1_props = row[0].get_properties()
        person1_name = person1_props['name']
        person1 = name_dict[person1_name]
        person2_props = row[1].get_properties()
        person2_name = person2_props['name']
        person2 = name_dict[person2_name]
        json_str = '{"source":' + str(person1) + ', "target": '+ str(person2) + '}'
        edge_list.append(json_str)
    edge_list_str = ",".join(edge_list)
    fout = open('influences_json.json','w')
    complete_json_str = '{ "nodes":[' + nodes_list_str + '], "links":[' + edge_list_str + ']}'
    json.dump(complete_json_str, fout, indent=4)
    fout.close()

