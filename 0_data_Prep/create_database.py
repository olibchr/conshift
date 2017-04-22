import sqlite3
import json
import numpy as np
import csv
import sys, os, operator

path = sys.argv[1]

# RAW ARTICLE VARIABLES
NO_ANT_CNT = 0
NO_CTG_CNT = 0
ERR_CNT = 0
all_abouts = []

# CONCEPT VARIABLES
concepts = []
filter_id_to_ctg, all_id_to_ctg, docid_to_date, weights = {}, {}, {}, {}


class Concept():
    def __init__(self, id, name, features):
        self.id = id
        self.name = name
        self.features = features


def load_article_data():
    for filename in os.listdir(path):
        if ".jsonld" not in filename:
            continue
        print filename
        get_raw_data(path + filename)
    return 0


def load_docid_map():
    doc_to_id = {}
    with open('../1_data/doc_to_id.csv','r') as in_file:
        reader = csv.reader(in_file, delimiter=',')
        for line in reader:
            doc_to_id[line[0]] = line[1]
    return doc_to_id


def get_raw_data(dir):
    with open(dir) as json_data:
        data = json.load(json_data)
    content = data['@reverse']
    publisher = data['name']
    global NO_ANT_CNT
    global NO_CTG_CNT
    global ERR_CNT
    global all_abouts

    for i in range(0,len(content['publisher'])):
        this_id = content['publisher'][i]['@id']
        this_date = content['publisher'][i]['datePublished']
        this_headline = content['publisher'][i]['headline']
        this_url = content['publisher'][i]['url']
        try:
            c.execute("INSERT INTO articles VALUES (?,?,?,?,?,?)", (this_id, publisher, this_date, this_headline, this_url, doc_to_id[this_id]))
        except Exception as e:
            print 'Key Error'
    return 0


def get_ctg():
    filter_id_to_ctg = {}
    all_id_to_ctg = {}
    with open('../1_data/annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            filter_id_to_ctg[int(row[1])] = row[0]
            all_id_to_ctg[int(row[1])] = row[0]
    return filter_id_to_ctg, all_id_to_ctg


def load_docdate_map():
    docid_to_date = {}
    with open('../1_data/docid_to_date.csv') as docmap:
        reader = csv.reader(docmap, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            docid_to_date[int(row[0])] = row[1]
    return docid_to_date


def load_idf_weights():
    filter_id_to_weight = {}
    with open("../1_data/all_distributions_weights.csv") as weights_map:
        reader = csv.reader(weights_map, delimiter=',', quotechar='|',quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            filter_id_to_weight[int(row[0])] = float(row[1])
    return filter_id_to_weight


def load_distr():
    all_d_content = []
    with open('../1_data/all_distributions_time.csv') as distr_vec:
        reader = csv.reader(distr_vec, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        all_data = []
        for row in reader:
            all_data.append([int(row[0]),row[1:]])
    for item in all_data:
        tups = []
        for i in range(0,len(item[1])-2,2):
            tups.append(item[1][i])
        this_concept = Concept(item[0], filter_id_to_ctg[item[0]].split('/')[-1],tups)
        all_d_content.append(this_concept)
    return all_d_content


def insert_concept():
    for con in concepts:
        try:
            c.execute("INSERT  INTO concepts VALUES (?,?,?)", (con.id, con.name, con.features))
        except Exception as e:
            print 'Concept error'


def insert_weights():
    for k,v in weights.iteritems():
        try:
            c.execute("INSERT  INTO weights VALUES (?,?)", (k,v))
        except Exception as e:
            print 'Weight error'


print 'Articles..'
conn = sqlite3.connect('../1_data/articles.db')
c = conn.cursor()
# ARTICLES
c.execute('''DROP TABLE articles''')
c.execute('''CREATE TABLE articles
             (id text, publisher text, datePublished text, headline text, url text, docID real)''')
doc_to_id = load_docid_map()
load_article_data()

print 'Concepts...'
#CONCEPTS
c.execute('''DROP TABLE concepts''')
c.execute('''CREATE TABLE concepts(
            id real, name text, features text
)''')
print 'Weights...'
c.execute('''DROP TABLE weights''')
c.execute('''CREATE TABLE weights(
            id real, weight real
)''')
filter_id_to_ctg, all_id_to_ctg = get_ctg()
docid_to_date = load_docdate_map()
weights = load_idf_weights()
concepts = load_distr()
insert_concept()
insert_weights()

c.close()

