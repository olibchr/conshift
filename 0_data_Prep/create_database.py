import sqlite3
import json
import numpy as np
import csv
import sys, os, operator

path = sys.argv[1]
NO_ANT_CNT = 0
NO_CTG_CNT = 0
ERR_CNT = 0
all_abouts = []
doc_to_id = {}

def load_data():
    for filename in os.listdir(path):
        if ".jsonld" not in filename:
            continue
        print filename
        get_data(path + filename)
    return 0

def load_doc_map():
    doc_to_id = {}
    with open(path + 'doc_to_id.csv','r') as in_file:
        reader = csv.reader(in_file, delimiter=',')
        for line in reader:
            doc_to_id[line[0] = line[1]
    return doc_to_id


def get_data(dir):
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
        c.execute("INSERT INTO articles VALUES (?,?,?,?,?,?)", (this_id, publisher, this_date, this_headline, this_url, doc_to_id[this_id]))
    return 0

def main():
    global doc_to_id
    conn = sqlite3.connect('articles.db')
    c = conn.cursor()
    c.execute('''DROP TABLE articles''')
    c.execute('''CREATE TABLE articles
                 (id text, publisher text, datePublished text, headline text, url text, docID text)''')
    doc_to_id = load_doc_map()
    load_data()
    c.close()


if __name__ == '__main__':
    main()
